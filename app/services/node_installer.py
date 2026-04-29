"""Node.js 下载与安装服务"""
import os
import sys
import subprocess

from app.config import NODEJS_DOWNLOAD_URL
from app.utils.downloader import download_file


def download_nodejs(callback=None) -> dict:
    dest = os.path.join(os.environ.get("TEMP", "."), "nodejs-installer.msi")
    if callback:
        callback(0, "正在从国内镜像下载 Node.js...")

    result = download_file(NODEJS_DOWNLOAD_URL, dest, progress_callback=callback)
    if not result["success"]:
        return {"success": False, "error": result["error"]}
    return {"success": True, "path": result["path"]}


def install_nodejs(msi_path: str, callback=None) -> dict:
    if callback:
        callback(0, "正在安装 Node.js...")

    try:
        proc = subprocess.run(
            ["msiexec", "/i", msi_path, "/quiet", "/norestart"],
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
        callback(100, "Node.js 安装完成")

    return {"success": True}


def set_npm_registry_mirror() -> dict:
    from app.services.proxy_helper import set_npm_mirror
    return set_npm_mirror()


def refresh_path_env():
    """刷新当前进程的 PATH 环境变量（从注册表读取最新值）"""
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                '[Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + '
                '[Environment]::GetEnvironmentVariable("PATH", "User")',
            ],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            os.environ["PATH"] = result.stdout.strip()
    except Exception:
        pass
