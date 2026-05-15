"""统一检测引擎 — 所有环境检测收敛到此处，各路由/服务直接调用"""
import json
import os
import re
import time
import threading

from app.config import NODEJS_VERSION, GIT_VERSION
from app.utils.subprocess_runner import run_cmd, run_powershell
from app.utils.path_helper import (
    check_appdata_path,
    get_claude_settings_path,
    get_claude_json_path,
    get_npm_global_path,
)
from app.utils.registry_reader import (
    get_nodejs_install_path as reg_nodejs,
    get_git_install_path as reg_git,
    get_ccswitch_install_path as reg_ccswitch,
)

# ─── 后端内存缓存 ───
_cache_data: dict | None = None
_cache_time: float = 0.0
_cache_lock = threading.Lock()
_CACHE_TTL = 60  # 秒


def clear_cache():
    """清除后端检测缓存（安装完成后调用）"""
    global _cache_data, _cache_time
    with _cache_lock:
        _cache_data = None
        _cache_time = 0.0


# ─── helpers ───

def _ver(raw: str) -> str:
    """从命令输出中提取语义版本号 (x.y.z)"""
    m = re.search(r"(\d+\.\d+\.\d+)", raw)
    return m.group(1) if m else raw.strip()


def _outdated(current: str, latest: str) -> bool:
    """简单比较版本号，判断是否落后于 latest"""
    try:
        c = tuple(int(x) for x in current.split("."))
        l = tuple(int(x) for x in latest.split("."))
        return c < l
    except Exception:
        return False


# ─── individual detectors ───

def _detect_nodejs() -> dict:
    r = run_cmd("node --version", timeout=10)
    installed = r["success"] and r["stdout"].startswith("v")
    version = _ver(r["stdout"]) if installed else ""
    path = reg_nodejs() or ""

    # CLI 失败但注册表有安装路径 → Node.js 已安装但不在 PATH
    if not installed and path:
        node_exe = os.path.join(path, "node.exe")
        r2 = run_cmd(f'"{node_exe}" --version', timeout=10)
        if r2["success"] and r2["stdout"].startswith("v"):
            installed = True
            version = _ver(r2["stdout"])

    latest = NODEJS_VERSION
    return {
        "installed": installed,
        "version": version,
        "latest_version": latest,
        "outdated": _outdated(version, latest) if installed and version else False,
        "paths": [path] if path else [],
        "method": "npm",
        "ok": installed,
    }


def _detect_npm() -> dict:
    r = run_cmd("npm --version", timeout=10)
    installed = r["success"] and r["stdout"].replace(".", "").isdigit()
    version = _ver(r["stdout"]) if installed else ""
    global_path = get_npm_global_path()

    # 检查 npm 最新版本
    latest = ""
    if installed:
        lr = run_cmd("npm view npm version", timeout=15)
        if lr["success"]:
            latest = _ver(lr["stdout"])

    return {
        "installed": installed,
        "version": version,
        "latest_version": latest,
        "outdated": _outdated(version, latest) if version and latest else False,
        "paths": [global_path] if global_path else [],
        "method": "nodejs",
        "ok": installed,
    }


def _detect_git() -> dict:
    r = run_cmd("git --version", timeout=10)
    installed = r["success"] and "git version" in r["stdout"].lower()
    version = _ver(r["stdout"]) if installed else ""
    path = reg_git() or ""

    # CLI 失败但注册表有安装路径 → Git 已安装但不在 PATH
    if not installed and path:
        git_exe = os.path.join(path, "bin", "git.exe")
        r2 = run_cmd(f'"{git_exe}" --version', timeout=10)
        if r2["success"] and "git version" in r2["stdout"].lower():
            installed = True
            version = _ver(r2["stdout"])

    latest = GIT_VERSION
    return {
        "installed": installed,
        "version": version,
        "latest_version": latest,
        "outdated": _outdated(version, latest) if installed and version else False,
        "paths": [path] if path else [],
        "method": "installer",
        "ok": installed,
    }


def _detect_claude_code() -> dict:
    r = run_cmd("claude --version", timeout=15)
    installed = r["success"] and not r["stderr"]
    version = _ver(r["stdout"]) if installed else ""
    npm_global = get_npm_global_path()
    paths = []
    if npm_global:
        p = os.path.join(npm_global, "node_modules", "@anthropic-ai", "claude-code")
        paths.append(p)
        # CLI 失败但 npm 全局目录有包 → Claude Code 已安装但不在 PATH
        if not installed and os.path.isdir(p):
            installed = True

    # 检查 Claude Code 最新版本
    latest = ""
    if installed:
        lr = run_cmd("npm view @anthropic-ai/claude-code version", timeout=15)
        if lr["success"]:
            latest = _ver(lr["stdout"])

    return {
        "installed": installed,
        "version": version,
        "latest_version": latest,
        "outdated": _outdated(version, latest) if version and latest else False,
        "paths": paths,
        "method": "npm",
        "ok": installed,
    }


def _detect_ccswitch() -> dict:
    """检测 CC-Switch（桌面版优先，其次是 CLI 版）"""
    path = reg_ccswitch()
    installed = path is not None
    vers = ""
    ctype = "desktop" if path else "none"

    if not installed:
        r = run_cmd("cc-switch --version", timeout=10)
        if r["success"]:
            installed = True
            vers = _ver(r["stdout"])
            ctype = "cli"
        # CLI 也失败但注册表有桌面版路径 → 已安装但 cc-switch 不在 PATH
        elif path:
            installed = True
            ctype = "desktop"

    # 从 GitHub API 获取最新版本
    latest = ""
    try:
        import urllib.request
        from app.config import CCSWITCH_RELEASES_API
        req = urllib.request.Request(
            CCSWITCH_RELEASES_API,
            headers={"User-Agent": "1shot-CC/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            latest = data.get("tag_name", "").lstrip("v")
    except Exception:
        pass

    paths = [path] if path else []
    return {
        "installed": installed,
        "version": vers,
        "latest_version": latest,
        "outdated": _outdated(vers, latest) if vers and latest else False,
        "paths": paths,
        "method": "msi" if ctype == "desktop" else ("npm" if ctype == "cli" else "none"),
        "ok": installed,
    }


def _detect_colorcc() -> dict:
    """检测 Color-cc (Oh My Posh 主题配置)"""
    omp_config = os.path.join(os.path.expanduser("~"), ".claude", "claude-dashboard.omp.json")
    settings_path = get_claude_settings_path()
    has_omp = os.path.exists(omp_config)
    has_statusline = False

    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            has_statusline = "statusLine" in data
        except Exception:
            pass

    installed = has_omp and has_statusline
    paths = [omp_config] if has_omp else []
    if has_statusline:
        paths.append(settings_path)
    return {
        "installed": installed,
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": paths,
        "method": "script",
        "ok": True,  # optional component
    }


def _detect_claude_config() -> dict:
    """检测 Claude Code 配置文件"""
    settings_path = get_claude_settings_path()
    claude_json_path = get_claude_json_path()
    settings_exists = os.path.exists(settings_path)
    claude_json_exists = os.path.exists(claude_json_path)
    onboarding_done = False

    if claude_json_exists:
        try:
            with open(claude_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            onboarding_done = data.get("hasCompletedOnboarding", False)
        except Exception:
            pass

    paths = []
    if settings_exists:
        paths.append(settings_path)
    if claude_json_exists:
        paths.append(claude_json_path)
    return {
        "installed": settings_exists or claude_json_exists,
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": paths,
        "method": "file",
        "ok": True,
        "settings_exists": settings_exists,
        "claude_json_exists": claude_json_exists,
        "onboarding_done": onboarding_done,
    }


def _detect_windows_terminal() -> dict:
    """检测 Windows Terminal 是否已安装"""
    installed = False
    paths = []

    r = run_cmd("where wt", timeout=8)
    if r["success"] and r["stdout"].strip():
        installed = True
        paths.append(r["stdout"].strip().split("\n")[0])
    else:
        r2 = run_cmd(
            r'reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\wt.exe" /ve',
            timeout=8,
        )
        if r2["success"] and "wt.exe" in r2["stdout"]:
            installed = True

    return {
        "installed": installed,
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": paths,
        "method": "msstore",
        "ok": installed,
    }


def _detect_powershell_policy() -> dict:
    """检测 PowerShell 执行策略"""
    r = run_powershell("Get-ExecutionPolicy -Scope CurrentUser", timeout=10)
    current_user = r["stdout"] if r["success"] else "Unknown"

    r2 = run_powershell("Get-ExecutionPolicy", timeout=10)
    effective = r2["stdout"] if r2["success"] else "Unknown"

    need_fix = effective in ("Restricted", "Undefined")
    return {
        "installed": True,  # always present
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": [],
        "method": "system",
        "ok": not need_fix,
        "current_user": current_user,
        "effective": effective,
        "need_fix": need_fix,
    }


def _detect_npm_registry() -> dict:
    """检测 npm 镜像源配置"""
    r = run_cmd("npm config get registry", timeout=10)
    current = r["stdout"] if r["success"] else ""
    is_mirror = "npmmirror.com" in current
    return {
        "installed": True,  # npm itself is present
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": [],
        "method": "config",
        "ok": True,
        "current": current,
        "is_mirror": is_mirror,
    }


def _detect_path_env() -> dict:
    """检测 PATH 环境变量"""
    paths = os.environ.get("PATH", "").split(os.pathsep)
    has_npm = any("npm" in p.lower() for p in paths)
    return {
        "installed": True,
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": paths,
        "method": "system",
        "ok": True,
        "has_npm": has_npm,
        "count": len(paths),
    }


def _detect_path_issues() -> dict:
    """检测中文路径等路径问题"""
    data = check_appdata_path()
    issues = data.get("issues", [])
    return {
        "installed": len(issues) == 0,  # True means no issues
        "version": "",
        "latest_version": "",
        "outdated": False,
        "paths": [],
        "method": "system",
        "ok": len(issues) == 0,
        "appdata": data.get("appdata", ""),
        "localappdata": data.get("localappdata", ""),
        "issues": issues,
    }


# ─── orchestrator ───

_detectors = {
    "nodejs": _detect_nodejs,
    "npm": _detect_npm,
    "git": _detect_git,
    "claude_code": _detect_claude_code,
    "ccswitch": _detect_ccswitch,
    "colorcc": _detect_colorcc,
    "claude_config": _detect_claude_config,
    "windows_terminal": _detect_windows_terminal,
    "powershell_policy": _detect_powershell_policy,
    "npm_registry": _detect_npm_registry,
    "path_env": _detect_path_env,
    "path_issues": _detect_path_issues,
}


def detect_all() -> dict:
    """运行所有检测器，返回完整结果字典（带 60s 内存缓存）"""
    global _cache_data, _cache_time

    with _cache_lock:
        if _cache_data is not None and (time.time() - _cache_time) < _CACHE_TTL:
            return _cache_data

    results = {}
    for key, func in _detectors.items():
        try:
            results[key] = func()
        except Exception as e:
            results[key] = {
                "installed": False,
                "version": "",
                "latest_version": "",
                "outdated": False,
                "paths": [],
                "method": "error",
                "ok": False,
                "error": str(e),
            }

    # 汇总 ready 状态 — 仅计算必需组件
    required = ["nodejs", "npm", "git", "claude_code"]
    results["ready"] = all(
        results.get(k, {}).get("installed", False) for k in required
    ) and not results.get("powershell_policy", {}).get("need_fix", True)

    with _cache_lock:
        _cache_data = results
        _cache_time = time.time()

    return results


def detect_one(key: str) -> dict:
    """运行单个检测器"""
    func = _detectors.get(key)
    if not func:
        return {
            "installed": False,
            "version": "",
            "latest_version": "",
            "outdated": False,
            "paths": [],
            "method": "unknown",
            "ok": False,
            "error": f"未知检测项: {key}",
        }
    try:
        return func()
    except Exception as e:
        return {
            "installed": False,
            "version": "",
            "latest_version": "",
            "outdated": False,
            "paths": [],
            "method": "error",
            "ok": False,
            "error": str(e),
        }
