"""一键卸载引擎 — 探测并清理通过 1shot-CC 安装的全部组件"""
import os
import shutil
import subprocess
from datetime import datetime

from app.utils.logger import info, warning
from app.utils.subprocess_runner import run_cmd


def detect_all() -> dict:
    """探测所有组件的安装状态（复用 detector 统一引擎 + 追加卸载专用字段）"""
    from app.services.detector import detect_all as base_detect
    base = base_detect()

    results = {}

    # Claude Code
    cc = base.get("claude_code", {})
    results["claude_code"] = {
        "name": "Claude Code",
        "installed": cc.get("installed", False),
        "version": cc.get("version", ""),
        "uninstall_cmd": 'npm uninstall -g @anthropic-ai/claude-code',
        "category": "software",
    }

    # CC-Switch 桌面版 (复用 detector 统一检测)
    csc = base.get("ccswitch", {})
    cc_paths = csc.get("paths", [])
    results["ccswitch_gui"] = {
        "name": "CC Switch 桌面版",
        "installed": csc.get("installed", False),
        "path": cc_paths[0] if cc_paths else "",
        "uninstall_method": "msi",
        "category": "software",
    }

    # Node.js
    nd = base.get("nodejs", {})
    from app.utils.registry_reader import get_nodejs_install_path
    results["nodejs"] = {
        "name": "Node.js",
        "installed": nd.get("installed", False),
        "version": nd.get("version", ""),
        "path": get_nodejs_install_path() or "",
        "uninstall_method": "msi",
        "category": "software",
    }

    # Git
    git = base.get("git", {})
    from app.utils.registry_reader import get_git_install_path
    results["git"] = {
        "name": "Git",
        "installed": git.get("installed", False),
        "version": git.get("version", ""),
        "path": get_git_install_path() or "",
        "uninstall_method": "inno",
        "category": "software",
    }

    # Color-cc
    color = base.get("colorcc", {})
    results["colorcc"] = {
        "name": "Color-cc 终端美化",
        "installed": color.get("installed", False),
        "path": color.get("paths", [""])[0] if color.get("paths") else "",
        "uninstall_method": "file",
        "category": "config",
    }

    # Claude 配置
    cfg = base.get("claude_config", {})
    results["claude_config"] = {
        "name": "Claude Code 配置文件",
        "installed": cfg.get("installed", False),
        "path": cfg.get("paths", [""])[0] if cfg.get("paths") else "",
        "uninstall_method": "file",
        "category": "config",
    }

    # 日志文件
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
    order = ["claude_code", "ccswitch_gui", "colorcc", "nodejs", "git", "claude_config", "logs"]
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
    """通过 MSI product code 卸载（四层回退）
    1) 注册表 UninstallString（最可靠）
    2) PowerShell Get-Package（现代 Windows）
    3) wmic 命令行（兼容旧系统）
    4) 手动清理快捷方式 + 安装目录
    """
    search_name = {"nodejs": "Node.js", "ccswitch_gui": "CC-Switch"}.get(key, key)

    # 第1层：注册表查找 UninstallString
    if _uninstall_from_registry(search_name):
        return

    # 第2层：PowerShell Get-Package（仅 CC-Switch）
    if key == "ccswitch_gui" and _uninstall_via_powershell():
        return

    # 第3层：wmic 回退
    try:
        proc = subprocess.run(
            f'wmic product where "Name like \'%{search_name}%\'" get IdentifyingNumber',
            shell=True, capture_output=True, text=True, timeout=60,
        )
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line and line != "IdentifyingNumber" and "{" in line:
                info(f"wmic 找到 {search_name} product code: {line}")
                subprocess.run(
                    f'msiexec /x {line} /quiet /norestart',
                    shell=True, capture_output=True, timeout=120,
                )
                return
    except Exception as e:
        warning(f"wmic 查询失败 [{search_name}]: {e}")

    # 第4层：手动清理（仅 CC-Switch）
    if key == "ccswitch_gui":
        _manual_cleanup_ccswitch(item)
    else:
        path = item.get("path", "")
        if path and os.path.exists(path):
            info(f"MSI product code 未找到，跳过 {search_name}（路径: {path}）")


def _uninstall_from_registry(search_name: str) -> bool:
    """在注册表 Uninstall 键中搜索应用并执行卸载命令"""
    for hive in ["HKLM", "HKCU"]:
        uninstall_base = f"{hive}\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        try:
            r = subprocess.run(
                ["reg", "query", uninstall_base, "/s", "/f", search_name, "/d"],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0:
                continue

            current_key = None
            for line in r.stdout.splitlines():
                stripped = line.strip()
                if stripped.startswith("HKEY_"):
                    current_key = stripped
                elif current_key and ("QuietUninstallString" in stripped or "UninstallString" in stripped):
                    for val_name in ["QuietUninstallString", "UninstallString"]:
                        r2 = subprocess.run(
                            ["reg", "query", current_key, "/v", val_name],
                            capture_output=True, text=True, timeout=15,
                        )
                        if r2.returncode == 0:
                            cmd = _parse_reg_sz(r2.stdout, val_name)
                            if cmd:
                                # UninstallString 格式为 MsiExec.exe /I{GUID}，需转换为 /x 才是卸载
                                import re as _re
                                _m = _re.search(r'\{[A-Fa-f0-9\-]+\}', cmd)
                                if _m:
                                    cmd = f'msiexec /x {_m.group()} /quiet /norestart'
                                info(f"注册表卸载 {search_name}: {cmd}")
                                subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
                                return True
        except Exception as e:
            warning(f"注册表卸载查询失败 [{hive}]: {e}")
    return False


def _parse_reg_sz(output: str, value_name: str) -> str | None:
    """从 reg query /v 输出中提取 REG_SZ 值"""
    for line in output.splitlines():
        if value_name in line:
            parts = line.strip().split("    ")
            if len(parts) >= 3:
                return parts[-1].strip()
    return None


def _uninstall_via_powershell() -> bool:
    """使用 PowerShell Get-Package 卸载 CC-Switch"""
    try:
        ps_cmd = (
            'Get-Package -Name "*CC-Switch*" -ErrorAction SilentlyContinue '
            '| Uninstall-Package -Force -ErrorAction SilentlyContinue'
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=120,
        )
        return r.returncode == 0
    except Exception as e:
        warning(f"PowerShell 卸载失败: {e}")
        return False


def _manual_cleanup_ccswitch(item: dict):
    """手动清理 CC-Switch：删除开始菜单快捷方式 + 安装目录"""
    _CC_NAMES = ["cc-switch", "cc switch", "ccswitch"]

    # 删除开始菜单快捷方式
    for sm_base in [
        os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.environ.get("PROGRAMDATA", ""), r"Microsoft\Windows\Start Menu\Programs"),
    ]:
        if not os.path.isdir(sm_base):
            continue
        try:
            for root, dirs, files in os.walk(sm_base):
                for f in files:
                    if f.endswith(".lnk"):
                        fn = f.lower().replace(".lnk", "")
                        if any(name in fn for name in _CC_NAMES):
                            p = os.path.join(root, f)
                            os.remove(p)
                            info(f"已删除快捷方式: {p}")
        except Exception as e:
            warning(f"清理快捷方式失败 [{sm_base}]: {e}")

    # 尝试删除安装目录
    path = item.get("path", "")
    if not path:
        try:
            from app.utils.registry_reader import _reg_query_value
            path = _reg_query_value(r"HKCU\Software\farion1231\CC-Switch", "InstallDir")
        except Exception:
            pass
    if not path:
        for base in [
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "CC-Switch"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "CC-Switch"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "CC-Switch"),
        ]:
            if os.path.isdir(base):
                path = base
                break
    if path and os.path.exists(path):
        try:
            if os.path.isfile(path):
                path = os.path.dirname(path)
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
                info(f"已删除安装目录: {path}")
        except Exception as e:
            warning(f"清理安装目录失败 [{path}]: {e}")

    # 删除 Tauri 注册表残留
    try:
        subprocess.run(
            ["reg", "delete", r"HKCU\Software\farion1231\CC-Switch", "/f"],
            capture_output=True, timeout=15,
        )
        info("已删除 CC-Switch 注册表残留")
    except Exception as e:
        warning(f"清理注册表残留失败: {e}")


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
