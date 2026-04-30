"""/api/system/* — 系统环境检测 API"""
import json
import os
from flask import Blueprint, jsonify

bp = Blueprint("system", __name__, url_prefix="/api/system")


@bp.route("/check-all")
def check_all():
    from app.utils.subprocess_runner import run_cmd, run_powershell
    from app.utils.path_helper import check_appdata_path, get_claude_settings_path, get_claude_json_path, get_npm_global_path
    from app.utils.registry_reader import get_nodejs_install_path as reg_nodejs, get_git_install_path as reg_git, get_ccswitch_install_path as reg_ccswitch

    results = {}

    # Node.js
    r = run_cmd("node --version", timeout=10)
    nodejs_installed = r["success"] and r["stdout"].startswith("v")
    results["nodejs"] = {
        "installed": nodejs_installed,
        "version": r["stdout"] if nodejs_installed else "",
        "path": reg_nodejs() or "",
    }

    # npm
    r = run_cmd("npm --version", timeout=10)
    npm_installed = r["success"] and r["stdout"].replace(".", "").isdigit()
    npm_global = get_npm_global_path()
    results["npm"] = {
        "installed": npm_installed,
        "version": r["stdout"] if npm_installed else "",
        "global_path": npm_global,
    }

    # Git
    r = run_cmd("git --version", timeout=10)
    git_installed = r["success"] and "git version" in r["stdout"].lower()
    results["git"] = {
        "installed": git_installed,
        "version": r["stdout"].replace("git version ", "") if git_installed else "",
        "path": reg_git() or "",
    }

    # Claude Code
    r = run_cmd("claude --version", timeout=10)
    claude_installed = r["success"] and not r["stderr"]
    results["claude_code"] = {
        "installed": claude_installed,
        "version": r["stdout"] if claude_installed else "",
    }

    # CC-Switch
    ccswitch_path = reg_ccswitch()
    # 也尝试检查 CLI 版
    ccswitch_installed = ccswitch_path is not None
    if not ccswitch_installed:
        r = run_cmd("cc-switch --version", timeout=10)
        ccswitch_installed = r["success"]
    results["ccswitch"] = {
        "installed": ccswitch_installed,
        "type": "desktop" if ccswitch_path else ("cli" if ccswitch_installed else "none"),
        "path": ccswitch_path or "",
    }

    # PowerShell 执行策略
    r = run_powershell("Get-ExecutionPolicy -Scope CurrentUser", timeout=10)
    policy_current_user = r["stdout"] if r["success"] else "Unknown"
    r = run_powershell("Get-ExecutionPolicy", timeout=10)
    policy_effective = r["stdout"] if r["success"] else "Unknown"
    results["powershell_policy"] = {
        "current_user": policy_current_user,
        "effective": policy_effective,
        "need_fix": policy_effective in ("Restricted", "Undefined"),
    }

    # npm 镜像源
    r = run_cmd("npm config get registry", timeout=10)
    results["npm_registry"] = {
        "current": r["stdout"] if r["success"] else "",
        "is_mirror": "npmmirror.com" in r["stdout"] if r["success"] else False,
    }

    # PATH 检测
    paths = os.environ.get("PATH", "").split(os.pathsep)
    has_npm_in_path = any("npm" in p.lower() for p in paths)
    results["path_env"] = {
        "has_npm": has_npm_in_path,
        "count": len(paths),
    }

    # 中文路径检测
    results["path_issues"] = check_appdata_path()

    # Claude Code 配置
    settings_path = get_claude_settings_path()
    claude_json_path = get_claude_json_path()
    results["claude_config"] = {
        "settings_exists": os.path.exists(settings_path),
        "claude_json_exists": os.path.exists(claude_json_path),
        "onboarding_done": False,
    }

    if os.path.exists(claude_json_path):
        try:
            with open(claude_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                results["claude_config"]["onboarding_done"] = data.get("hasCompletedOnboarding", False)
        except Exception:
            pass

    # Windows Terminal
    wt_installed = False
    r = run_cmd("where wt", timeout=8)
    if r["success"] and r["stdout"].strip():
        wt_installed = True
    else:
        # 备用检测：检查注册表
        r2 = run_cmd(
            r'reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\wt.exe" /ve',
            timeout=8,
        )
        if r2["success"] and "wt.exe" in r2["stdout"]:
            wt_installed = True
    results["windows_terminal"] = {
        "installed": wt_installed,
        "ok": wt_installed,
    }

    # 汇总：计算 ready 状态
    results["ready"] = all([
        nodejs_installed,
        git_installed,
        claude_installed,
        not results["powershell_policy"]["need_fix"],
    ])

    return jsonify({"success": True, "data": results})


@bp.route("/check-nodejs")
def check_nodejs():
    from app.utils.subprocess_runner import run_cmd
    r = run_cmd("node --version", timeout=10)
    return jsonify({"success": True, "installed": r["success"] and r["stdout"].startswith("v"), "version": r["stdout"]})


@bp.route("/check-git")
def check_git():
    from app.utils.subprocess_runner import run_cmd
    r = run_cmd("git --version", timeout=10)
    return jsonify({"success": True, "installed": r["success"], "version": r["stdout"]})


@bp.route("/check-claude")
def check_claude():
    from app.utils.subprocess_runner import run_cmd
    r = run_cmd("claude --version", timeout=10)
    return jsonify({"success": True, "installed": r["success"], "version": r["stdout"]})


@bp.route("/check-ccswitch")
def check_ccswitch():
    from app.utils.registry_reader import get_ccswitch_install_path
    path = get_ccswitch_install_path()
    return jsonify({"success": True, "installed": path is not None, "path": path or ""})


@bp.route("/check-policy")
def check_policy():
    from app.utils.subprocess_runner import run_powershell
    r = run_powershell("Get-ExecutionPolicy", timeout=10)
    return jsonify({"success": True, "policy": r["stdout"] if r["success"] else "Unknown"})


@bp.route("/check-winterm")
def check_winterm():
    """轻量检测 Windows Terminal 是否已安装"""
    from app.utils.subprocess_runner import run_cmd

    wt_installed = False
    r = run_cmd("where wt", timeout=8)
    if r["success"] and r["stdout"].strip():
        wt_installed = True
    else:
        r2 = run_cmd(
            r'reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\wt.exe" /ve',
            timeout=8,
        )
        if r2["success"] and "wt.exe" in r2["stdout"]:
            wt_installed = True
    return jsonify({"success": True, "installed": wt_installed})


@bp.route("/check-config")
def check_config():
    from app.utils.path_helper import get_claude_settings_path, get_claude_json_path
    settings_ok = os.path.exists(get_claude_settings_path())
    claude_json_ok = os.path.exists(get_claude_json_path())
    return jsonify({
        "success": True,
        "settings_exists": settings_ok,
        "claude_json_exists": claude_json_ok,
    })
