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


def get_ccswitch_install_path() -> str | None:
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
    return None
