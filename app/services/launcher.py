"""统一的应用/脚本启动器 — 优先使用 Windows Terminal"""
import os
import subprocess
import tempfile


def _find_wt_exe() -> str | None:
    """检测 Windows Terminal wt.exe 是否可用"""
    try:
        r = subprocess.run(["where", "wt"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().split("\n")[0]
    except Exception:
        pass

    local_wt = os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "wt.exe"
    )
    if os.path.exists(local_wt):
        return local_wt

    return None


def launch_in_terminal(ps1_path: str) -> dict:
    """在最佳终端中执行 .ps1 脚本（WT 优先，PowerShell 回退）"""
    if not os.path.exists(ps1_path):
        return {"success": False, "error": f"脚本文件不存在: {ps1_path}"}

    wt_exe = _find_wt_exe()
    try:
        if wt_exe:
            cmd = [wt_exe, "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps1_path]
        else:
            cmd = ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", ps1_path]

        subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE if not wt_exe else 0,
        )
        return {"success": True, "message": "已在新窗口启动"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_ccswitch_exe() -> str | None:
    """通过开始菜单 + 注册表 + 文件系统查找 CC-Switch"""
    # 1) 扫描开始菜单快捷方式
    _CC_NAMES = ["cc-switch", "cc switch", "ccswitch"]
    _start_dirs = [
        os.path.join(os.environ.get("APPDATA",""), r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.environ.get("PROGRAMDATA",""), r"Microsoft\Windows\Start Menu\Programs"),
    ]
    for sm_base in _start_dirs:
        if not os.path.isdir(sm_base): continue
        try:
            for root, dirs, files in os.walk(sm_base):
                for f in files:
                    if f.endswith(".lnk"):
                        fn = f.lower().replace(".lnk","")
                        if any(name in fn for name in _CC_NAMES):
                            return os.path.join(root, f)
        except Exception: pass
    # 2) 注册表回退
    from app.utils.registry_reader import _find_ccswitch_exe_path
    return _find_ccswitch_exe_path()


def launch_powershell_with_guide() -> dict:
    """在新终端窗口打开带引导信息的 PowerShell"""
    guide_content = r'''
Write-Host ""
Write-Host "" -ForegroundColor Cyan
Write-Host "                                              " -ForegroundColor Cyan
Write-Host "     Claude Code          !          " -ForegroundColor Green
Write-Host "                                              " -ForegroundColor Cyan
Write-Host "" -ForegroundColor Cyan
Write-Host ""
Write-Host "    claude   Enter  ：" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ：Ctrl+C  ，Ctrl+D  " -ForegroundColor DarkGray
Write-Host ""
'''
    try:
        tmpdir = tempfile.gettempdir()
        ps1_path = os.path.join(tmpdir, "1shot-cc-welcome.ps1")
        with open(ps1_path, "w", encoding="utf-8") as f:
            f.write(guide_content)
        return launch_in_terminal(ps1_path)
    except Exception as e:
        return {"success": False, "error": str(e)}


def launch_ccswitch_app() -> dict:
    """启动 CC-Switch 桌面应用"""
    path = find_ccswitch_exe()
    if not path:
        return {"success": False, "error": "找不到 CC-Switch 安装位置，请确认已安装。可以从开始菜单手动启动。"}
    try:
        subprocess.Popen(
            [path],
            creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, "CREATE_NEW_CONSOLE") else 0,
        )
        return {"success": True, "message": f"CC-Switch 已启动: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def launch_claude_in_powershell() -> dict:
    """在终端中直接启动 claude"""
    script = r'''
Write-Host ""
Write-Host "  Claude Code  ..." -ForegroundColor Green
Write-Host ""
claude
'''
    try:
        tmpdir = tempfile.gettempdir()
        ps1_path = os.path.join(tmpdir, "1shot-cc-run-claude.ps1")
        with open(ps1_path, "w", encoding="utf-8") as f:
            f.write(script)
        return launch_in_terminal(ps1_path)
    except Exception as e:
        return {"success": False, "error": str(e)}
