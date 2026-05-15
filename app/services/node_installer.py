"""Node.js 下载与安装服务"""
import os
import sys
import subprocess

from app.config import NODEJS_DOWNLOAD_URL, NODEJS_VERSION
from app.utils.downloader import download_file

# 官方源回退 URL
_NODEJS_FALLBACK_URL = f"https://nodejs.org/dist/v{NODEJS_VERSION}/node-v{NODEJS_VERSION}-x64.msi"


def preflight_nodejs() -> dict:
    """安装前预检，返回 go/no-go 状态"""
    import shutil
    from app.utils.elevation import is_admin
    from app.utils.logger import info

    issues = []

    try:
        tmp = os.environ.get("TEMP", "C:\\")
        usage = shutil.disk_usage(tmp)
        free_gb = usage.free / (1024 * 1024 * 1024)
        if free_gb < 1.0:
            issues.append(f"磁盘空间不足（仅剩 {free_gb:.1f} GB），需要至少 1GB")
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

    from app.utils.subprocess_runner import run_cmd

    r = run_cmd("node --version", timeout=10)
    if r["success"] and r["stdout"].startswith("v"):
        info(f"Node.js 已安装: {r['stdout']}")

    return {"ok": len(issues) == 0, "issues": issues}


def download_nodejs(callback=None) -> dict:
    dest = os.path.join(os.environ.get("TEMP", "."), "nodejs-installer.msi")

    urls = [NODEJS_DOWNLOAD_URL, _NODEJS_FALLBACK_URL]
    last_error = ""
    for i, url in enumerate(urls):
        if callback:
            if i == 0:
                callback(0, "正在从国内镜像下载 Node.js...")
            else:
                callback(0, "国内镜像失败，尝试从官方源下载...")
        result = download_file(url, dest, progress_callback=callback)
        if result["success"]:
            return {"success": True, "path": result["path"]}
        last_error = result.get("error", "未知错误")
        try:
            os.remove(dest)
        except Exception:
            pass

    return {"success": False, "error": f"Node.js 下载失败: {last_error}"}


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
