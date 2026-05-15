"""Git for Windows 下载与安装服务"""
import os
import sys
import subprocess

from app.config import GIT_DOWNLOAD_URL, GIT_VERSION
from app.utils.downloader import download_file

# GitHub 官方回退 URL
_GIT_FALLBACK_URL = f"https://github.com/git-for-windows/git/releases/download/v{GIT_VERSION}.windows.1/Git-{GIT_VERSION}-64-bit.exe"


def preflight_git() -> dict:
    """Git 安装前预检"""
    import shutil
    from app.utils.elevation import is_admin

    issues = []

    try:
        tmp = os.environ.get("TEMP", "C:\\")
        usage = shutil.disk_usage(tmp)
        free_gb = usage.free / (1024 * 1024 * 1024)
        if free_gb < 0.5:
            issues.append(f"磁盘空间不足（仅剩 {free_gb:.1f} GB），需要至少 500MB")
    except Exception:
        pass

    if not is_admin():
        issues.append("建议以管理员身份运行（右键 exe → 以管理员身份运行）")

    try:
        test = os.path.join(os.environ.get("TEMP", "."), "1shot-cc-test.tmp")
        with open(test, "w") as f:
            f.write("ok")
        os.remove(test)
    except Exception:
        issues.append("临时目录不可写，无法下载安装包")

    return {"ok": len(issues) == 0, "issues": issues}


def download_git(callback=None) -> dict:
    dest = os.path.join(os.environ.get("TEMP", "."), "git-installer.exe")

    urls = [GIT_DOWNLOAD_URL, _GIT_FALLBACK_URL]
    last_error = ""
    for i, url in enumerate(urls):
        if callback:
            if i == 0:
                callback(0, "正在从国内镜像下载 Git for Windows...")
            else:
                callback(0, "国内镜像失败，尝试从 GitHub 官方源下载...")
        result = download_file(url, dest, progress_callback=callback)
        if result["success"]:
            return {"success": True, "path": result["path"]}
        last_error = result.get("error", "未知错误")
        try:
            os.remove(dest)
        except Exception:
            pass

    return {"success": False, "error": f"Git 下载失败: {last_error}"}


def install_git(exe_path: str, callback=None) -> dict:
    if callback:
        callback(0, "正在安装 Git for Windows...")

    try:
        proc = subprocess.run(
            [
                exe_path,
                "/VERYSILENT", "/NORESTART", "/NOCANCEL",
                "/SUPPRESSMSGBOXES", "/CLOSEAPPLICATIONS",
                "/COMPONENTS=icons,ext,ext\\shellhere,ext\\guihere,gitlfs,assoc",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if proc.returncode != 0:
            return {"success": False, "error": f"安装返回码: {proc.returncode}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}

    if callback:
        callback(100, "Git 安装完成")

    return {"success": True}
