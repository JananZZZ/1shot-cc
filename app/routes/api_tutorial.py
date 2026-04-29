"""/api/tutorial/* — 教程 API"""
from flask import Blueprint, jsonify
from app.config import TUTORIALS

bp = Blueprint("tutorial", __name__, url_prefix="/api/tutorial")


@bp.route("/list")
def list_tutorials():
    return jsonify({"success": True, "data": list(TUTORIALS.values())})
