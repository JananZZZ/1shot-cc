"""Color-cc 终端美化安装器
Color-cc 是 JananZZZ 的 Oh My Posh statusline 主题
仓库: https://github.com/JananZZZ/color-cc
"""
import json
import os
import subprocess
import tempfile
import urllib.request

INSTALL_PS1_URLS = [
    "https://gitee.com/JananZZZ/color-cc/raw/main/install.ps1",             # Gitee 镜像（国内优先）
    "https://raw.githubusercontent.com/JananZZZ/color-cc/main/install.ps1",  # GitHub raw
    "https://cdn.jsdelivr.net/gh/JananZZZ/color-cc@main/install.ps1",        # jsDelivr CDN
]

_THEME_URLS = [
    "https://gitee.com/JananZZZ/color-cc/raw/main/config/claude-dashboard.omp.json",
    "https://raw.githubusercontent.com/JananZZZ/color-cc/main/config/claude-dashboard.omp.json",
]

CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
SETTINGS_PATH = os.path.join(CLAUDE_DIR, "settings.json")
OMP_CONFIG_PATH = os.path.join(CLAUDE_DIR, "claude-dashboard.omp.json")


def check_windows_terminal() -> dict:
    """检测 Windows Terminal 是否已安装"""
    try:
        r = subprocess.run(["where", "wt"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return {"installed": True, "path": r.stdout.strip().split("\n")[0]}
    except Exception:
        pass

    wt_paths = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "wt.exe"),
        r"C:\Program Files\WindowsApps\Microsoft.WindowsTerminal_8wekyb3d8bbwe\wt.exe",
    ]
    for p in wt_paths:
        if os.path.exists(p):
            return {"installed": True, "path": p}

    return {"installed": False, "path": ""}


def _ensure_settings_json() -> None:
    """确保 ~/.claude/settings.json 存在（install.ps1 需要它）"""
    os.makedirs(CLAUDE_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)


def _download_install_script(callback=None) -> str | None:
    """下载 Color-cc 官方 install.ps1，返回临时文件路径或 None"""
    for url in INSTALL_PS1_URLS:
        if callback:
            callback(10, "正在下载 Color-cc 安装脚本...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "1shot-CC/2.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
                if resp.status == 200 and content.strip():
                    tmpdir = tempfile.gettempdir()
                    ps1_path = os.path.join(tmpdir, "color-cc-install.ps1")
                    with open(ps1_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return ps1_path
        except Exception:
            continue

    return None


def _download_theme(callback=None) -> bool:
    """从 Gitee/GitHub 下载主题文件，直接写入 ~/.claude/（Python 端处理，绕过 ps1 网络问题）"""
    for url in _THEME_URLS:
        if callback:
            callback(60, "正在下载主题配置...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "1shot-CC/2.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    content = resp.read()
                    os.makedirs(CLAUDE_DIR, exist_ok=True)
                    with open(OMP_CONFIG_PATH, "wb") as f:
                        f.write(content)
                    return True
        except Exception:
            continue
    return False


def _write_statusline_config() -> bool:
    """在 settings.json 中写入 statusLine 配置"""
    try:
        os.makedirs(CLAUDE_DIR, exist_ok=True)
        data = {}
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {}
        data["statusLine"] = {
            "type": "oh-my-posh",
            "config": OMP_CONFIG_PATH,
        }
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def _verify_installation() -> dict:
    """安装后验证：检查配置是否已写入"""
    result = {"omp_config_exists": False, "statusline_configured": False}

    if os.path.exists(OMP_CONFIG_PATH):
        result["omp_config_exists"] = True

    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "statusLine" in data:
                result["statusline_configured"] = True
        except Exception:
            pass

    return result


def install_colorcc(callback=None) -> dict:
    """安装 Color-cc — 执行 install.ps1 安装 Oh My Posh，
    然后 Python 端直接从 Gitee 镜像下载主题配置，不依赖 ps1 的网络逻辑。"""
    wt_check = check_windows_terminal()
    if not wt_check["installed"]:
        if callback:
            callback(0, "未检测到 Windows Terminal，请先从 Microsoft Store 安装")
        return {
            "success": False,
            "error": "未检测到 Windows Terminal。请先在 Microsoft Store 搜索并安装 Windows Terminal。",
        }

    # install.ps1 需要 settings.json 存在
    if callback:
        callback(5, "检查配置文件...")
    _ensure_settings_json()

    ps1_path = _download_install_script(callback)
    if not ps1_path:
        if callback:
            callback(0, "下载安装脚本失败，请检查网络连接")
        return {
            "success": False,
            "error": (
                "下载 Color-cc 安装脚本失败，请检查网络连接后重试。\n"
                "也可访问 https://github.com/JananZZZ/color-cc 手动安装"
            ),
        }

    # 执行 install.ps1 — 安装 Oh My Posh
    # ps1 内部的网络下载（主题文件）可能在中国失败，但我们会在 Python 端处理
    if callback:
        callback(40, "正在安装 Oh My Posh（可能需要几分钟）...")

    ohmyposh_ok = False
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1_path],
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode == 0:
            ohmyposh_ok = True
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装 Oh My Posh 超时（超过 5 分钟），请检查网络后重试"}
    except Exception as e:
        return {"success": False, "error": f"执行安装脚本失败: {str(e)}"}

    # Python 端独立下载主题文件（从 Gitee 镜像，绕过 ps1 的网络问题）
    if callback:
        callback(70, "正在下载终端美化主题...")
    theme_ok = _download_theme(callback)

    # 写入 statusLine 配置
    if callback:
        callback(85, "正在写入配置...")
    statusline_ok = _write_statusline_config()

    # 验证
    if callback:
        callback(95, "验证安装结果...")
    verify = _verify_installation()

    if verify["omp_config_exists"] and verify["statusline_configured"]:
        if callback:
            callback(100, "Color-cc 安装完成！")
        return {
            "success": True,
            "message": "Color-cc 安装完成！Oh My Posh 状态栏主题已配置。\n在 Claude Code 中发一条消息即可看到效果。",
        }

    # 部分成功
    issues = []
    if not ohmyposh_ok:
        issues.append("Oh My Posh 安装可能未完成")
    if not theme_ok:
        issues.append("主题文件下载失败（网络问题）")
    if not statusline_ok:
        issues.append("配置文件写入失败")

    if callback:
        callback(100, "安装完成（部分步骤未成功）")

    return {
        "success": False,
        "partial": True,
        "error": (
            "Color-cc 安装未完全成功。\n"
            + "；".join(issues)
            + "\n\n请尝试：\n"
            + "1. 以管理员身份运行后重试\n"
            + "2. 检查网络连接是否正常\n"
            + "3. 访问 https://github.com/JananZZZ/color-cc 手动安装"
        ),
    }


def launch_colorcc_guide() -> dict:
    """打开 Color-cc 的 GitHub 页面"""
    import webbrowser

    try:
        webbrowser.open("https://github.com/JananZZZ/color-cc")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
