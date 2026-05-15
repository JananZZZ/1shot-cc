"""CC-Switch 安装服务"""
import json
import os
import subprocess
import tempfile
import urllib.request
import urllib.error

from app.config import CCSWITCH_RELEASES_API
from app.utils.downloader import download_file

# 下载回退 URL 列表（按优先级）
# jsDelivr 的 gh 端点无法提供 GitHub Release 附件，故用国内加速代理
_CCSWITCH_FALLBACK_URLS = [
    "https://ghproxy.com/https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
    "https://mirror.ghproxy.com/https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
    "https://gh.llkk.cc/https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
    "https://gh.api.99988866.xyz/https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
    "https://gh.con.sh/https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
    "https://github.ur1.fun/https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
    "https://github.com/farion1231/cc-switch/releases/latest/download/CC-Switch-Setup-x64.msi",
]


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


def download_ccswitch(callback=None) -> dict:
    """下载 CC-Switch MSI 安装包（多源快速回退）"""
    dest = os.path.join(tempfile.gettempdir(), "cc-switch-installer.msi")
    MSI_MIN_SIZE = 1024 * 1024  # MSI 至少 1MB

    # 第1层：GitHub API 获取真实下载 URL 和文件名
    info = get_latest_release_info()
    version = "latest"

    # 构建回退列表：API 返回的真实 URL 优先，然后硬编码镜像兜底
    fallback_urls = list(_CCSWITCH_FALLBACK_URLS)
    if info["success"] and info.get("download_url"):
        version = info.get("version", "latest")
        # 把 API 返回的真实 URL 插到列表最前面
        fallback_urls.insert(0, info["download_url"])
        if callback:
            callback(0, f"正在下载 CC-Switch {version}...")
    elif callback:
        callback(0, "GitHub API 不可达，使用 CDN 加速源...")

    result = _try_download_urls(fallback_urls, dest, callback=callback, min_size=MSI_MIN_SIZE)
    if not result["success"]:
        return {
            "success": False,
            "error": (
                "CC-Switch 桌面版下载失败，所有下载源均不可用。\n"
                "可尝试下方「命令行版」安装（npm 国内镜像，更稳定）：\n"
                "https://github.com/farion1231/cc-switch/releases"
            ),
            "hint_cli": True,
        }

    return {"success": True, "path": result["path"], "version": version}


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
        return {"success": False, "error": "安装超时，npm 下载可能较慢，请检查网络后重试"}
    except FileNotFoundError:
        return {"success": False, "error": "未找到 npm 命令，请先安装 Node.js"}
    except Exception as e:
        return {"success": False, "error": str(e)}
