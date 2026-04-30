"""Color-cc 终端美化安装器
Color-cc 是 JananZZZ 的 Oh My Posh statusline 主题
仓库: https://github.com/JananZZZ/color-cc
"""
import os
import subprocess
import tempfile
import urllib.request

INSTALL_PS1_URLS = [
    "https://raw.githubusercontent.com/JananZZZ/color-cc/main/install.ps1",
    "https://cdn.jsdelivr.net/gh/JananZZZ/color-cc@main/install.ps1",
]


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


def _download_install_script(callback=None) -> str | None:
    """下载 Color-cc 官方 install.ps1，返回临时文件路径或 None"""
    for url in INSTALL_PS1_URLS:
        if callback:
            callback(10, f"正在下载 Color-cc 安装脚本...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "1shot-CC/2.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode("utf-8")
                if resp.status == 200 and content.strip():
                    tmpdir = tempfile.gettempdir()
                    ps1_path = os.path.join(tmpdir, "color-cc-install.ps1")
                    with open(ps1_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return ps1_path
        except Exception:
            continue  # 尝试下一个 URL

    return None


def install_colorcc(callback=None) -> dict:
    """安装 Color-cc — 下载并执行官方 install.ps1 一键脚本"""
    wt_check = check_windows_terminal()
    if not wt_check["installed"]:
        if callback:
            callback(0, "未检测到 Windows Terminal，请先从 Microsoft Store 安装")
        return {"success": False, "error": "未检测到 Windows Terminal。请先在 Microsoft Store 搜索并安装 Windows Terminal。"}

    ps1_path = _download_install_script(callback)
    if not ps1_path:
        if callback:
            callback(0, "下载安装脚本失败，请检查网络连接")
        return {"success": False, "error": "下载 Color-cc 安装脚本失败。请检查网络连接后重试，或访问 https://github.com/JananZZZ/color-cc 手动安装"}

    if callback:
        callback(40, "正在执行 Color-cc 安装脚本（可能需要下载 Oh My Posh）...")

    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1_path],
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="replace",
        )

        if callback:
            callback(100, "Color-cc 安装完成！")

        if proc.returncode == 0:
            return {
                "success": True,
                "message": "Color-cc 安装完成！Oh My Posh 状态栏主题已配置。\n在 Claude Code 中发一条消息即可看到效果。",
            }

        # 部分成功（脚本返回非零但可能已部分安装）
        return {
            "success": True,
            "partial": True,
            "message": (
                "安装脚本执行完毕（部分内容可能需要手动确认）。\n"
                "如果 Oh My Posh 未安装，请参考: https://ohmyposh.dev/docs/installation/windows"
            ),
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时"}
    except Exception as e:
        return {"success": False, "error": f"执行安装脚本失败: {str(e)}"}


def launch_colorcc_guide() -> dict:
    """打开 Color-cc 的 GitHub 页面"""
    import webbrowser

    try:
        webbrowser.open("https://github.com/JananZZZ/color-cc")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
