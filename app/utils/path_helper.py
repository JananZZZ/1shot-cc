"""路径处理工具"""
import os
import sys


def is_chinese_path(path: str) -> bool:
    for ch in path:
        if "一" <= ch <= "鿿" or "㐀" <= ch <= "䶿":
            return True
    return False


def check_appdata_path() -> dict:
    appdata = os.environ.get("APPDATA", "")
    roaming = os.environ.get("APPDATA", "")
    local = os.environ.get("LOCALAPPDATA", "")
    issues = []
    for name, p in [("APPDATA", appdata), ("LOCALAPPDATA", local)]:
        if is_chinese_path(p):
            issues.append({"var": name, "path": p, "problem": "路径含中文字符"})
    return {"appdata": appdata, "localappdata": local, "issues": issues, "ok": len(issues) == 0}


def get_claude_config_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".claude")


def get_claude_settings_path() -> str:
    return os.path.join(get_claude_config_dir(), "settings.json")


def get_claude_json_path() -> str:
    return os.path.join(os.path.expanduser("~"), ".claude.json")


def get_npm_global_path() -> str:
    npm_prefix = os.environ.get("npm_config_prefix", "")
    if npm_prefix:
        return npm_prefix
    appdata = os.environ.get("APPDATA", "")
    return os.path.join(appdata, "npm") if appdata else ""
