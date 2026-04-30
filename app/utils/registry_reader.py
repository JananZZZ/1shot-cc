"""Windows 注册表读取工具"""
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

    # 备选：检查 64 位注册表
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


def _find_ccswitch_exe_path() -> str | None:
    """扫描常见安装位置查找 CC-Switch 可执行文件"""
    import os as _os

    search_paths = [
        _os.path.join(_os.environ.get("LOCALAPPDATA", ""), "Programs", "CC-Switch"),
        _os.path.join(_os.environ.get("PROGRAMFILES", "C:\\Program Files"), "CC-Switch"),
        _os.path.join(_os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "CC-Switch"),
        _os.path.join(_os.environ.get("APPDATA", ""), "CC-Switch"),
    ]

    for base in search_paths:
        if not base or not _os.path.isdir(base):
            continue
        for pattern in ["CC-Switch.exe", "cc-switch.exe", "CCSwitch.exe"]:
            for root, _, files in _os.walk(base):
                for f in files:
                    if f.lower() == pattern.lower():
                        return _os.path.join(root, f)

    return None


def get_ccswitch_install_path() -> str | None:
    # 1) 注册表文本搜索
    for uninstall_key in [
        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]:
        try:
            result = subprocess.run(
                ["reg", "query", uninstall_key, "/s", "/f", "CC-Switch"],
                capture_output=True, text=True, timeout=30,
            )
            if "CC-Switch" in result.stdout:
                return "已安装"
        except Exception:
            pass

    # 2) 注册表 Uninstall 位置解析 DisplayName
    for hive in ["HKLM", "HKCU"]:
        for uninstall_key in [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]:
            try:
                r = subprocess.run(
                    ["reg", "query", f"{hive}\\{uninstall_key}", "/s", "/f", "CC-Switch"],
                    capture_output=True, text=True, timeout=30,
                )
                if "CC-Switch" in r.stdout:
                    return "已安装"
            except Exception:
                pass

    # 3) 文件系统扫描 fallback
    exe_path = _find_ccswitch_exe_path()
    if exe_path:
        return exe_path

    return None
