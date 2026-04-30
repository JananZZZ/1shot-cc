"""/api/config/* — 配置管理 API"""
from flask import Blueprint, jsonify, request

from app.config import PROVIDERS
from app.services.config_writer import (
    write_claude_settings,
    read_current_config_safe,
    backup_config,
)
from app.utils.path_helper import get_claude_settings_path

bp = Blueprint("config", __name__, url_prefix="/api/config")


@bp.route("/providers")
def list_providers():
    result = {}
    for key, p in PROVIDERS.items():
        result[key] = {
            "name": p["name"],
            "register_url": p["register_url"],
            "api_key_url": p["api_key_url"],
            "docs_url": p["docs_url"],
        }
    return jsonify({"success": True, "data": result})


@bp.route("/write", methods=["POST"])
def write_config():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"success": False, "error": "请求数据为空"})

    provider_key = body.get("provider", "")
    api_key = body.get("api_key", "").strip()
    custom_base_url = body.get("base_url", "").strip()
    haiku_model = body.get("haiku_model", "").strip()
    sonnet_model = body.get("sonnet_model", "").strip()
    opus_model = body.get("opus_model", "").strip()

    if not provider_key:
        return jsonify({"success": False, "error": "请选择提供商"})

    if provider_key == "custom" and not custom_base_url:
        return jsonify({"success": False, "error": "自定义模式需要填写 Base URL"})

    if provider_key != "custom" and provider_key not in PROVIDERS:
        return jsonify({"success": False, "error": "无效的提供商"})

    if not api_key:
        return jsonify({"success": False, "error": "API Key 不能为空"})

    result = write_claude_settings(provider_key, api_key, custom_base_url, haiku_model, sonnet_model, opus_model)
    return jsonify(result)


@bp.route("/current")
def current_config():
    return jsonify({"success": True, "data": read_current_config_safe()})


@bp.route("/backup", methods=["POST"])
def do_backup():
    path = get_claude_settings_path()
    bak = backup_config(path)
    if bak:
        return jsonify({"success": True, "backup_path": bak})
    return jsonify({"success": True, "backup_path": None, "message": "无现有配置需要备份"})
