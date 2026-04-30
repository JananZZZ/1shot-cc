"""Windows 注册表读取工具"""
import os as _os
import subprocess
import sys


def get_nodejs_install_path() -> str | None:
    try:
        result = subprocess.run(
            ["reg", "query", r"HKLM\SOFTWARE\Node.js", "/v", "InstallPath"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "InstallPath" in line and "REG_SZ" in line:
                    return line.split("REG_SZ")[-1].strip()
    except Exception:
        pass
    return None


def get_git_install_path() -> str | None:
    try:
        result = subprocess.run(
            ["reg", "query", r"HKLM\SOFTWARE\GitForWindows", "/v", "InstallPath"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "InstallPath" in line and "REG_SZ" in line:
                    return line.split("REG_SZ")[-1].strip()
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["reg", "query", r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Git_is1", "/v", "InstallLocation"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "InstallLocation" in line:
                    return line.split("REG_SZ")[-1].strip()
    except Exception:
        pass
    return None


def _reg_query_value(hive_key: str, value_name: str, timeout: int = 10) -> str | None:
    """查询单个注册表值，返回 REG_SZ 数据或 None"""
    try:
        r = subprocess.run(
            ["reg", "query", hive_key, "/v", value_name],
            capture_output=True, text=True, timeout=timeout,
        )
        if r.returncode == 0:
            for line in r.stdout.splitlines():
                if value_name in line and "REG_SZ" in line:
                    return line.split("REG_SZ")[-1].strip()
    except Exception:
        pass
    return None


def _walk_find_exe(directory: str) -> str | None:
    """在目录中搜索 CC-Switch 可执行文件，限制深度"""
    if not directory or not _os.path.isdir(directory):
        return None
    max_depth = 3
    for root, dirs, files in _os.walk(directory):
        depth = root[len(directory):].count(_os.sep)
        if depth > max_depth:
            dirs.clear()
            continue
        for f in files:
            name_lower = f.lower()
            if name_lower in ("cc-switch.exe", "ccswitch.exe"):
                return _os.path.join(root, f)
    return None


def _find_ccswitch_exe_path() -> str | None:
    """通过注册表 + 文件系统查找 CC-Switch 可执行文件"""

    # 1) Tauri 安装路径 — 最可靠的信息来源
    install_dir = _reg_query_value(r"HKCU\Software\farion1231\CC-Switch", "InstallDir")
    if install_dir:
        exe = _walk_find_exe(install_dir)
        if exe:
            return exe

    # 2) 尝试 HKCU + HKLM 的 DisplayIcon（Tauri .msi 设置，格式: path,0）
    for hive_key in ["HKLM", "HKCU"]:
        uninstall_base = f"{hive_key}\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        try:
            r = subprocess.run(
                ["reg", "query", uninstall_base, "/s", "/f", "CC-Switch"],
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode != 0 or "CC-Switch" not in r.stdout:
                continue

            # 从输出中找到对应的子键名，然后查询 DisplayIcon
            current_subkey = None
            for line in r.stdout.splitlines():
                stripped = line.strip()
                if stripped.startswith("HKEY_"):
                    current_subkey = stripped
                elif current_subkey and "DisplayIcon" in stripped and "REG_" in stripped:
                    icon_val = stripped.split("REG_")[-1].strip()
                    if icon_val.startswith("SZ") or icon_val.startswith("EXPAND_SZ"):
                        continue
                    # DisplayIcon 格式: C:\path\to\CC-Switch.exe,0
                    exe_path = stripped.split("REG_SZ")[-1].strip() if "REG_SZ" in stripped else ""
                    if not exe_path:
                        exe_path = stripped.split("REG_EXPAND_SZ")[-1].strip()
                    if exe_path:
                        # 去掉末尾的 ",0" 图标索引
                        if "," in exe_path and exe_path.endswith(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")):
                            exe_path = exe_path.rsplit(",", 1)[0]
                        if _os.path.exists(exe_path):
                            return exe_path

            # 3) 从同一子键查询 InstallLocation
            if current_subkey:
                loc = _reg_query_value(current_subkey, "InstallLocation")
                if loc:
                    exe = _walk_find_exe(loc)
                    if exe:
                        return exe
        except Exception:
            continue

    # 4) 文件系统扫描 fallback
    for base in [
        _os.path.join(_os.environ.get("PROGRAMFILES", "C:\\Program Files"), "CC-Switch"),
        _os.path.join(_os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "CC-Switch"),
        _os.path.join(_os.environ.get("LOCALAPPDATA", ""), "Programs", "CC-Switch"),
        _os.path.join(_os.environ.get("APPDATA", ""), "CC-Switch"),
    ]:
        exe = _walk_find_exe(base)
        if exe:
            return exe

    return None


def get_ccswitch_install_path() -> str | None:
    """检测 CC-Switch 安装路径，未安装返回 None"""
    return _find_ccswitch_exe_path()
