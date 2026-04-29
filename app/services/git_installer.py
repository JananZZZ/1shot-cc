"""Git for Windows 下载与安装服务"""
import os
import sys
import subprocess

from app.config import GIT_DOWNLOAD_URL
from app.utils.downloader import download_file


def download_git(callback=None) -> dict:
    dest = os.path.join(os.environ.get("TEMP", "."), "git-installer.exe")
    if callback:
        callback(0, "正在从国内镜像下载 Git for Windows...")

    result = download_file(GIT_DOWNLOAD_URL, dest, progress_callback=callback)
    if not result["success"]:
        return {"success": False, "error": result["error"]}
    return {"success": True, "path": result["path"]}


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
