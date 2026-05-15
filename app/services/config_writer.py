"""settings.json / .claude.json 配置写入服务"""
import json
import os
import shutil
from datetime import datetime

from app.utils.path_helper import get_claude_config_dir
from app.config import PROVIDERS


def backup_config(path: str) -> str | None:
    """备份配置文件，返回备份路径"""
    if not os.path.exists(path):
        return None
    bak = path + f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(path, bak)
    return bak


def read_claude_settings() -> dict:
    path = os.path.join(get_claude_config_dir(), "settings.json")
    if not os.path.exists(path):
        return {"env": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"env": {}}


def write_claude_settings(provider_key: str, api_key: str, custom_base_url: str = "", haiku_model: str = "", sonnet_model: str = "", opus_model: str = "") -> dict:
    if provider_key == "custom":
        if not custom_base_url:
            return {"success": False, "error": "自定义提供商需要输入 Base URL"}
        provider = {"name": "自定义", "base_url": custom_base_url}
    else:
        provider = PROVIDERS.get(provider_key)
        if not provider:
            return {"success": False, "error": f"未知的提供商: {provider_key}"}

    config_dir = get_claude_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    settings_path = os.path.join(config_dir, "settings.json")

    existing = {}
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass

    backup_config(settings_path)

    env = existing.get("env", {})
    env.update({
        "ANTHROPIC_AUTH_TOKEN": api_key,
        "ANTHROPIC_BASE_URL": provider["base_url"],
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    })

    # 模型：用户手动填的优先，否则用提供商默认值
    haiku = haiku_model or provider.get("default_haiku", "")
    sonnet = sonnet_model or provider.get("default_sonnet", "")
    opus = opus_model or provider.get("default_opus", "")
    if haiku:
        env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = haiku
    if sonnet:
        env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = sonnet
    if opus:
        env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = opus

    existing["env"] = env

    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    except Exception as e:
        return {"success": False, "error": f"写入失败: {e}"}

    write_claude_json()

    return {"success": True, "provider": provider["name"]}


def write_claude_json() -> dict:
    path = os.path.join(os.path.expanduser("~"), ".claude.json")
    existing = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            pass

    existing["hasCompletedOnboarding"] = True

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_current_config_safe() -> dict:
    """读取当前配置（API Key 脱敏）"""
    path = os.path.join(get_claude_config_dir(), "settings.json")
    if not os.path.exists(path):
        return {"configured": False, "provider": "", "base_url": ""}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        env = data.get("env", {})
        base_url = env.get("ANTHROPIC_BASE_URL", "")
        token = env.get("ANTHROPIC_AUTH_TOKEN", "")

        provider_name = ""
        for key, p in PROVIDERS.items():
            if p["base_url"] == base_url:
                provider_name = p["name"]
                break

        masked = ""
        if token:
            if len(token) > 8:
                masked = token[:4] + "****" + token[-4:]
            else:
                masked = token[:2] + "****"

        return {
            "configured": bool(token),
            "provider": provider_name,
            "base_url": base_url,
            "api_key_masked": masked,
        }
    except Exception:
        return {"configured": False, "provider": "", "base_url": ""}
