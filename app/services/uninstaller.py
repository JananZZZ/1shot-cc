"""一键卸载引擎 — 探测并清理通过 1shot-CC 安装的全部组件"""
import os
import shutil
import subprocess
from datetime import datetime

from app.utils.logger import info, warning
from app.utils.subprocess_runner import run_cmd


def detect_all() -> dict:
    """探测所有组件的安装状态，返回 {component: {installed, version, path, uninstall_method}}"""
    results = {}

    # 1. Claude Code (npm global)
    r = run_cmd("claude --version", timeout=10)
    results["claude_code"] = {
        "name": "Claude Code",
        "installed": r["success"] and not r["stderr"],
        "version": r["stdout"] if r["success"] else "",
        "uninstall_cmd": 'npm uninstall -g @anthropic-ai/claude-code',
        "category": "software",
    }

    # 2. CC-Switch CLI (npm global)
    r = run_cmd("cc-switch --version", timeout=10)
    results["ccswitch_cli"] = {
        "name": "CC-Switch CLI",
        "installed": r["success"],
        "version": r["stdout"] if r["success"] else "",
        "uninstall_cmd": 'npm uninstall -g cc-switch-cli',
        "category": "software",
    }

    # 3. CC-Switch GUI (注册表 + 文件系统)
    from app.utils.registry_reader import get_ccswitch_install_path
    cc_path = get_ccswitch_install_path()
    results["ccswitch_gui"] = {
        "name": "CC-Switch 桌面版",
        "installed": cc_path is not None,
        "path": cc_path or "",
        "uninstall_method": "msi",
        "category": "software",
    }

    # 4. Node.js
    r = run_cmd("node --version", timeout=10)
    from app.utils.registry_reader import get_nodejs_install_path
    node_path = get_nodejs_install_path()
    results["nodejs"] = {
        "name": "Node.js",
        "installed": r["success"] and r["stdout"].startswith("v"),
        "version": r["stdout"] if r["success"] else "",
        "path": node_path or "",
        "uninstall_method": "msi",
        "category": "software",
    }

    # 5. Git
    r = run_cmd("git --version", timeout=10)
    from app.utils.registry_reader import get_git_install_path
    git_path = get_git_install_path()
    results["git"] = {
        "name": "Git",
        "installed": r["success"] and "git version" in r["stdout"].lower(),
        "version": r["stdout"].replace("git version ", "") if r["success"] else "",
        "path": git_path or "",
        "uninstall_method": "inno",
        "category": "software",
    }

    # 6. Color-cc (Oh My Posh 主题配置)
    omp_config = os.path.join(os.path.expanduser("~"), ".claude", "claude-dashboard.omp.json")
    results["colorcc"] = {
        "name": "Color-cc 终端美化",
        "installed": os.path.exists(omp_config),
        "path": omp_config if os.path.exists(omp_config) else "",
        "uninstall_method": "file",
        "category": "config",
    }

    # 7. Claude 配置
    settings_path = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
    claude_json = os.path.join(os.path.expanduser("~"), ".claude.json")
    results["claude_config"] = {
        "name": "Claude Code 配置文件",
        "installed": os.path.exists(settings_path) or os.path.exists(claude_json),
        "path": settings_path if os.path.exists(settings_path) else claude_json,
        "uninstall_method": "file",
        "category": "config",
    }

    # 8. 日志文件
    log_dir = os.path.join(os.environ.get("TEMP", "."), "1shot-cc")
    results["logs"] = {
        "name": "1shot-CC 诊断日志",
        "installed": os.path.isdir(log_dir),
        "path": log_dir if os.path.isdir(log_dir) else "",
        "uninstall_method": "dir",
        "category": "config",
    }

    return results


def uninstall_all(selected: list[str], callback=None) -> dict:
    """执行卸载，通过 callback(progress, message) 推送进度。返回 {success, uninstalled, failed, errors}"""
    import time
    all_items = detect_all()
    uninstalled = []
    failed = []
    errors = []

    # 按顺序卸载：先软件后配置
    order = ["claude_code", "ccswitch_cli", "ccswitch_gui", "colorcc", "nodejs", "git", "claude_config", "logs"]
    ordered = [k for k in order if k in selected]

    total = len(ordered)
    for i, key in enumerate(ordered):
        item = all_items.get(key, {})
        name = item.get("name", key)
        pct = (i / max(total, 1)) * 100

        if not item.get("installed"):
            info(f"跳过卸载 {name}: 未检测到安装")
            if callback:
                callback(pct, f"跳过 {name}（未检测到）")
            continue

        if callback:
            callback(pct, f"正在卸载 {name}...")

        try:
            _uninstall_one(key, item)
            uninstalled.append(name)
            info(f"已卸载: {name}")
        except Exception as e:
            warning(f"卸载失败 [{name}]: {e}")
            failed.append(name)
            errors.append(f"{name}: {e}")

        time.sleep(0.5)  # 让 SSE 有时间推送

    # 清除检测缓存，确保重新检测时反映真实状态
    from app.services.detector import clear_cache as _clear_detect_cache
    _clear_detect_cache()

    if callback:
        callback(100, "卸载完成")

    return {
        "success": len(failed) == 0,
        "uninstalled": uninstalled,
        "failed": failed,
        "errors": errors,
    }


def _uninstall_one(key: str, item: dict):
    """卸载单个组件"""
    method = item.get("uninstall_method", "cmd")
    cmd = item.get("uninstall_cmd", "")

    if method == "cmd" and cmd:
        _run_silent(cmd, timeout=120)

    elif method == "msi":
        _uninstall_msi(key, item)

    elif method == "inno":
        _uninstall_inno(item)

    elif method == "file":
        path = item.get("path", "")
        if path and os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
            info(f"已删除文件: {path}")

    elif method == "dir":
        path = item.get("path", "")
        if path and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
            info(f"已删除目录: {path}")


def _run_silent(cmd: str, timeout: int = 120):
    """静默执行命令"""
    info(f"执行卸载命令: {cmd}")
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        info(f"卸载命令返回 {proc.returncode}: {proc.stderr[:200]}")


def _uninstall_msi(key: str, item: dict):
    """通过 MSI product code 卸载"""
    search_name = {"nodejs": "Node.js", "ccswitch_gui": "CC-Switch"}.get(key, key)
    # 尝试通过 wmic 查找 product code
    try:
        proc = subprocess.run(
            f'wmic product where "Name like \'%{search_name}%\'" get IdentifyingNumber',
            shell=True, capture_output=True, text=True, timeout=60,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line and line != "IdentifyingNumber" and "{" in line:
                info(f"找到 {search_name} product code: {line}")
                subprocess.run(
                    f'msiexec /x {line} /quiet /norestart',
                    shell=True, capture_output=True, timeout=120,
                )
                return
    except Exception as e:
        warning(f"wmic 查询失败 [{search_name}]: {e}")

    # 回退：通过路径推断卸载命令
    path = item.get("path", "")
    if path and os.path.exists(path):
        info(f"MSI product code 未找到，跳过 {search_name}（路径: {path}）")


def _uninstall_inno(item: dict):
    """通过 Inno Setup unins000.exe 卸载"""
    path = item.get("path", "")
    if not path:
        # 尝试默认路径
        path = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Git")
    unins = os.path.join(path, "unins000.exe")
    if os.path.exists(unins):
        subprocess.run(
            [unins, "/VERYSILENT", "/NORESTART"],
            capture_output=True, timeout=120,
        )
        info(f"Inno Setup 卸载完成: {unins}")
    else:
        warning(f"Git 卸载程序未找到: {unins}")


def backup_configs() -> str | None:
    """卸载前备份配置文件，返回备份目录路径或 None"""
    claude_dir = os.path.join(os.path.expanduser("~"), ".claude")
    if not os.path.isdir(claude_dir):
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(claude_dir, f"backup_uninstall_{ts}")
    os.makedirs(backup_dir, exist_ok=True)

    # ~/.claude/ 下的配置文件
    for fname in ["settings.json", "claude-dashboard.omp.json"]:
        src = os.path.join(claude_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_dir, fname))
            info(f"已备份: {src} -> {backup_dir}")

    # ~/.claude.json（HOME 根目录）
    home_json = os.path.join(os.path.expanduser("~"), ".claude.json")
    if os.path.exists(home_json):
        shutil.copy2(home_json, os.path.join(backup_dir, ".claude.json"))
        info(f"已备份: {home_json} -> {backup_dir}")

    return backup_dir if os.listdir(backup_dir) else None
