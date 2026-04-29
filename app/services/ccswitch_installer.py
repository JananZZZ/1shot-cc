"""CC-Switch 安装服务"""
import json
import os
import subprocess
import tempfile
import urllib.request
import urllib.error

from app.config import CCSWITCH_RELEASES_API
from app.utils.downloader import download_file


def get_latest_release_info() -> dict:
    """从 GitHub API 获取最新 CC-Switch 版本信息"""
    try:
        req = urllib.request.Request(
            CCSWITCH_RELEASES_API,
            headers={"User-Agent": "1shot-CC/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assets = data.get("assets", [])
            msi_asset = None
            for a in assets:
                name = a.get("name", "")
                if name.endswith(".msi") and "windows" in name.lower():
                    msi_asset = a
                    break
            if not msi_asset:
                for a in assets:
                    if a.get("name", "").endswith(".msi"):
                        msi_asset = a
                        break

            return {
                "success": True,
                "version": data.get("tag_name", ""),
                "download_url": msi_asset["browser_download_url"] if msi_asset else "",
                "filename": msi_asset["name"] if msi_asset else "",
                "size": msi_asset.get("size", 0) if msi_asset else 0,
            }
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"GitHub API 请求失败: HTTP {e.code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def download_ccswitch(callback=None) -> dict:
    """下载 CC-Switch MSI 安装包"""
    info = get_latest_release_info()
    if not info["success"]:
        if callback:
            callback(0, f"获取版本信息失败: {info.get('error', '')}，尝试使用备用链接...")
        # 备用方案：固定下载链接
        info = {
            "download_url": "https://github.com/farion1231/cc-switch/releases/latest",
            "filename": "CC-Switch-Setup.msi",
        }

    if not info.get("download_url"):
        return {"success": False, "error": "未找到下载链接，请手动安装 CC-Switch"}

    dest = os.path.join(tempfile.gettempdir(), "cc-switch-installer.msi")
    if callback:
        callback(0, f"正在下载 CC-Switch {info.get('version', '')}...")

    result = download_file(info["download_url"], dest, progress_callback=callback)
    if not result["success"]:
        return {"success": False, "error": result["error"]}
    return {"success": True, "path": result["path"], "version": info.get("version", "")}


def install_ccswitch(msi_path: str, callback=None) -> dict:
    """安装 CC-Switch MSI"""
    if callback:
        callback(0, "正在安装 CC-Switch...")

    try:
        proc = subprocess.run(
            ["msiexec", "/i", msi_path, "/quiet", "/norestart"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if proc.returncode != 0:
            return {"success": False, "error": f"安装返回码: {proc.returncode}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}

    if callback:
        callback(100, "CC-Switch 安装完成！")

    return {"success": True}


def install_ccswitch_cli(callback=None) -> dict:
    """通过 npm 安装 CC-Switch CLI 版"""
    if callback:
        callback(0, "正在安装 cc-switch-cli...")
    try:
        env = os.environ.copy()
        env["npm_config_registry"] = "https://registry.npmmirror.com"
        process = subprocess.Popen(
            "npm install -g cc-switch-cli",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        out = []
        for line in iter(process.stdout.readline, ""):
            if line:
                out.append(line.rstrip())
                if callback and len(out) % 5 == 0:
                    callback(min(90, 10 + len(out)), line.rstrip()[:120])
        process.wait(timeout=300)
        if process.returncode == 0:
            if callback:
                callback(100, "cc-switch-cli 安装完成！")
            return {"success": True}
        return {"success": False, "error": "\n".join(out[-10:])}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时"}
    except Exception as e:
        return {"success": False, "error": str(e)}
