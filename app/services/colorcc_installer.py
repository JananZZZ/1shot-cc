"""Color-cc 终端美化安装器
使用 Color-cc 官方推荐的一键安装命令（irm ... | iex）
仓库: https://github.com/JananZZZ/color-cc
"""
import json
import os
import subprocess

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
    """使用 Color-cc 官方推荐的一键安装命令（irm ... | iex）
    install.ps1 自行处理：Oh My Posh 安装 → 主题下载 → statusLine 配置 → cc-switch 集成"""
    wt_check = check_windows_terminal()
    if not wt_check["installed"]:
        if callback:
            callback(0, "未检测到 Windows Terminal，请先从 Microsoft Store 安装")
        return {
            "success": False,
            "error": "未检测到 Windows Terminal。请先在 Microsoft Store 搜索并安装 Windows Terminal。",
        }

    if callback:
        callback(5, "确保配置文件目录存在...")
    _ensure_settings_json()

    if callback:
        callback(20, "正在运行 Color-cc 一键安装命令（可能需要几分钟）...")

    try:
        # GitHub 首选，失败则回退到 Gitee 镜像
        cmd = (
            'powershell -NoProfile -ExecutionPolicy Bypass -Command "'
            'try { irm https://raw.githubusercontent.com/JananZZZ/color-cc/main/install.ps1 | iex } '
            'catch { irm https://gitee.com/JananZZZ/Color-cc/raw/main/install.ps1 | iex }"'
        )
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
            encoding="utf-8",
            errors="replace",
        )

        if callback:
            callback(90, "验证安装结果...")

        verify = _verify_installation()

        if verify.get("statusline_configured"):
            if callback:
                callback(100, "Color-cc 安装完成！")
            return {
                "success": True,
                "message": "Color-cc 安装完成！重启终端即可看到美化效果。",
            }

        # install.ps1 返回非0但 statusLine 已配置 → 仍算成功
        if verify.get("omp_config_exists"):
            if callback:
                callback(100, "安装完成（主题已下载）")
            return {
                "success": True,
                "message": "Color-cc 主题已配置，可能需要手动重启终端。",
            }

        error_detail = proc.stderr[:300] if proc.stderr else f"返回码: {proc.returncode}"
        return {"success": False, "error": f"安装失败: {error_detail}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时（超过 5 分钟），请检查网络后重试"}
    except Exception as e:
        return {"success": False, "error": f"安装失败: {str(e)}"}


def launch_colorcc_guide() -> dict:
    """打开 Color-cc 的 GitHub 页面"""
    import webbrowser

    try:
        webbrowser.open("https://github.com/JananZZZ/color-cc")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
