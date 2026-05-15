"""CC-Switch 安装服务"""
import json
import os
import subprocess
import tempfile
import urllib.request
import urllib.error

from app.config import CCSWITCH_RELEASES_API
from app.utils.downloader import download_file

# 唯一验证可用的国内加速代理（2026-05 实测）
_CCSWITCH_PROXY = "https://gh.llkk.cc"


def preflight_ccswitch() -> dict:
    """CC-Switch 安装前预检（GUI 版需要管理员权限）"""
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
        issues.append("安装桌面版 CC-Switch 需要管理员权限（右键 exe → 以管理员身份运行）")

    try:
        test = os.path.join(os.environ.get("TEMP", "."), "1shot-cc-test.tmp")
        with open(test, "w") as f:
            f.write("ok")
        os.remove(test)
    except Exception:
        issues.append("临时目录不可写，无法下载安装包")

    return {"ok": len(issues) == 0, "issues": issues}


def get_latest_release_info() -> dict:
    """从 GitHub API 获取最新 CC-Switch 版本信息"""
    try:
        req = urllib.request.Request(
            CCSWITCH_RELEASES_API,
            headers={"User-Agent": "1shot-CC/1.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
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


def _try_download_urls(urls: list[str], dest: str, callback=None, min_size: int = 0) -> dict:
    """依次尝试多个下载 URL，返回第一个成功的结果"""
    last_error = ""
    for i, url in enumerate(urls):
        if callback:
            if i == 0:
                callback(0, "正在连接下载源...")
            else:
                callback(0, f"切换备用下载源 {i}...")
        result = download_file(url, dest, progress_callback=callback, min_size=min_size)
        if result["success"]:
            return result
        last_error = result.get("error", "未知错误")
        try:
            os.remove(dest)
        except Exception:
            pass
    return {"success": False, "error": last_error or "所有下载源均失败"}


def _get_release_info_via_proxy() -> dict:
    """通过代理下载 latest.json 获取真实文件名（GitHub API 不可达时的轻量回退）"""
    latest_json_url = (
        f"{_CCSWITCH_PROXY}/https://github.com/farion1231/cc-switch"
        "/releases/latest/download/latest.json"
    )
    try:
        req = urllib.request.Request(latest_json_url, headers={"User-Agent": "1shot-CC/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            version = data.get("tag_name", "latest")
            for asset in data.get("assets", []):
                name = asset.get("name", "")
                if name.endswith(".msi"):
                    return {
                        "success": True,
                        "version": version,
                        "filename": name,
                        "download_url": asset.get("browser_download_url", ""),
                    }
    except Exception:
        pass
    return {"success": False}


def download_ccswitch(callback=None) -> dict:
    """下载 CC-Switch MSI 安装包（两层智能回退）
    1) GitHub API → 真实文件名 → 直连+代理双路下载
    2) gh.llkk.cc 代理 latest.json → 解析文件名 → 代理下载
    """
    dest = os.path.join(tempfile.gettempdir(), "cc-switch-installer.msi")
    MSI_MIN_SIZE = 1024 * 1024

    info = get_latest_release_info()
    version = "latest"
    filename = None

    if info["success"] and info.get("filename"):
        version = info.get("version", "latest")
        filename = info["filename"]
    else:
        # API 不可达 → 尝试 latest.json 轻量回退
        if callback:
            callback(0, "GitHub API 不可达，尝试加速通道...")
        proxy_info = _get_release_info_via_proxy()
        if proxy_info["success"]:
            version = proxy_info.get("version", "latest")
            filename = proxy_info.get("filename")

    if filename:
        # 用真实文件名拼接下载 URL：直连 + 代理双路
        urls = [
            f"https://github.com/farion1231/cc-switch/releases/download/{version}/{filename}",
            f"{_CCSWITCH_PROXY}/https://github.com/farion1231/cc-switch/releases/download/{version}/{filename}",
        ]
        if callback:
            callback(0, f"正在下载 CC-Switch {version}...")
        result = _try_download_urls(urls, dest, callback=callback, min_size=MSI_MIN_SIZE)
        if result["success"]:
            return {"success": True, "path": result["path"], "version": version}

    return {
        "success": False,
        "error": (
            "CC-Switch 下载失败，下载源暂时不可用。\n"
            "请检查网络连接后重试，或手动下载安装：\n"
            "https://github.com/farion1231/cc-switch/releases"
        ),
    }


def install_ccswitch(msi_path: str, callback=None) -> dict:
    """安装 CC-Switch MSI"""
    if callback:
        callback(0, "正在安装 CC-Switch...")

    try:
        proc = subprocess.run(
            ["msiexec", "/i", msi_path, "/quiet", "/norestart"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if proc.returncode != 0:
            return {"success": False, "error": f"安装返回码: {proc.returncode}"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时，请检查系统后重试"}
    except FileNotFoundError:
        return {"success": False, "error": "未找到 msiexec 命令，请确认 Windows Installer 服务正常运行"}
    except Exception as e:
        return {"success": False, "error": str(e)}

    if callback:
        callback(100, "CC-Switch 安装完成！")

    return {"success": True}
