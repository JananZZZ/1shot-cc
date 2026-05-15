"""系统环境完整检测服务"""
import os
import json

from app.utils.subprocess_runner import run_cmd, run_powershell
from app.utils.path_helper import (
    check_appdata_path,
    get_claude_settings_path,
    get_claude_json_path,
    get_npm_global_path,
)
from app.utils.registry_reader import (
    get_nodejs_install_path as reg_nodejs,
    get_git_install_path as reg_git,
    get_ccswitch_install_path as reg_ccswitch,
)


def check_nodejs() -> dict:
    r = run_cmd("node --version", timeout=10)
    installed = r["success"] and r["stdout"].startswith("v")
    version = r["stdout"] if installed else ""
    path = reg_nodejs() or ""
    return {"installed": installed, "version": version, "path": path, "ok": installed}


def check_npm() -> dict:
    r = run_cmd("npm --version", timeout=10)
    installed = r["success"] and r["stdout"].replace(".", "").isdigit()
    global_path = get_npm_global_path()
    return {"installed": installed, "version": r["stdout"] if installed else "", "global_path": global_path, "ok": installed}


def check_git() -> dict:
    r = run_cmd("git --version", timeout=10)
    installed = r["success"] and "git version" in r["stdout"].lower()
    v = r["stdout"].replace("git version ", "") if installed else ""
    return {"installed": installed, "version": v, "path": reg_git() or "", "ok": installed}


def check_claude_code() -> dict:
    r = run_cmd("claude --version", timeout=15)
    installed = r["success"] and not r["stderr"]
    return {"installed": installed, "version": r["stdout"] if installed else "", "ok": installed}


def check_ccswitch() -> dict:
    ccswitch_path = reg_ccswitch()
    installed = ccswitch_path is not None
    return {"installed": installed, "type": "desktop" if installed else "none", "path": ccswitch_path or "", "ok": installed}


def check_powershell_policy() -> dict:
    r = run_powershell("Get-ExecutionPolicy", timeout=10)
    policy = r["stdout"] if r["success"] else "Unknown"
    need_fix = policy in ("Restricted", "Undefined")
    return {"policy": policy, "need_fix": need_fix, "ok": not need_fix}


def check_npm_registry() -> dict:
    r = run_cmd("npm config get registry", timeout=10)
    current = r["stdout"] if r["success"] else ""
    is_mirror = "npmmirror.com" in current
    return {"current": current, "is_mirror": is_mirror, "ok": True}


def check_path_env() -> dict:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    has_npm = any("npm" in p.lower() for p in paths)
    return {"has_npm": has_npm, "count": len(paths), "ok": True}


def check_claude_config() -> dict:
    settings_path = get_claude_settings_path()
    claude_json_path = get_claude_json_path()
    result = {
        "settings_exists": os.path.exists(settings_path),
        "claude_json_exists": os.path.exists(claude_json_path),
        "onboarding_done": False,
        "ok": True,
    }
    if os.path.exists(claude_json_path):
        try:
            with open(claude_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                result["onboarding_done"] = data.get("hasCompletedOnboarding", False)
        except Exception:
            pass
    return result


def run_full_check() -> dict:
    results = {
        "nodejs": check_nodejs(),
        "npm": check_npm(),
        "git": check_git(),
        "claude_code": check_claude_code(),
        "ccswitch": check_ccswitch(),
        "powershell_policy": check_powershell_policy(),
        "npm_registry": check_npm_registry(),
        "path_env": check_path_env(),
        "path_issues": check_appdata_path(),
        "claude_config": check_claude_config(),
    }
    results["ready"] = all(v["ok"] for k, v in results.items() if k not in ("npm_registry", "path_env", "path_issues", "claude_config", "ccswitch"))
    return results
