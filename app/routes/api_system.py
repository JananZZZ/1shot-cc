"""/api/system/* — 系统环境检测 API + 页面生命周期管理"""
import json
import os
import time
import threading

from flask import Blueprint, jsonify, request
from app.utils.logger import info

bp = Blueprint("system", __name__, url_prefix="/api/system")

# ─── 页面引用计数（看门狗用） ───
_page_lock = threading.Lock()
_page_last_seen: dict[str, float] = {}
_last_close_time: float = 0.0


def get_page_state():
    """供 main.py 的看门狗线程使用，返回 (last_seen, lock, last_close_time)"""
    return _page_last_seen, _page_lock, _last_close_time


def _page_count() -> int:
    """返回当前活跃页面数"""
    return len(_page_last_seen)


# ─── 健康检查 ───

@bp.route("/ping")
def ping():
    return jsonify({"success": True, "message": "pong", "timestamp": time.time()})


@bp.route("/startup-checks")
def startup_checks():
    """运行系统启动健康检查"""
    from app.utils.startup_checker import run_startup_checks
    results = run_startup_checks()
    return jsonify({"success": True, "data": results})


# ─── 统一检测 ───

@bp.route("/check-all")
def check_all():
    from app.services.detector import detect_all
    results = detect_all()
    return jsonify({"success": True, "data": results})


# ─── 单项检测 ───

@bp.route("/check-nodejs")
def check_nodejs():
    from app.services.detector import _detect_nodejs
    return jsonify({"success": True, "data": _detect_nodejs()})


@bp.route("/check-git")
def check_git():
    from app.services.detector import _detect_git
    return jsonify({"success": True, "data": _detect_git()})


@bp.route("/check-claude")
def check_claude():
    from app.services.detector import _detect_claude_code
    return jsonify({"success": True, "data": _detect_claude_code()})


@bp.route("/check-ccswitch")
def check_ccswitch():
    from app.services.detector import _detect_ccswitch
    return jsonify({"success": True, "data": _detect_ccswitch()})


@bp.route("/check-policy")
def check_policy():
    from app.services.detector import _detect_powershell_policy
    return jsonify({"success": True, "data": _detect_powershell_policy()})


@bp.route("/clear-detect-cache", methods=["POST"])
def clear_detect_cache():
    """清除后端检测缓存（卸载/安装后调用）"""
    from app.services.detector import clear_cache
    clear_cache()
    return jsonify({"success": True})


@bp.route("/check-winterm")
def check_winterm():
    from app.services.detector import _detect_windows_terminal
    return jsonify({"success": True, "data": _detect_windows_terminal()})


@bp.route("/check-config")
def check_config():
    from app.services.detector import _detect_claude_config
    return jsonify({"success": True, "data": _detect_claude_config()})


# ─── 页面生命周期 ───

@bp.route("/page-open", methods=["POST"])
def page_open():
    """前端页面打开时调用，注册页面引用（防止看门狗误杀）"""
    data = request.get_json(silent=True) or {}
    page_id = data.get("page_id", str(time.time()))
    with _page_lock:
        _page_last_seen[page_id] = time.time()
    cnt = _page_count()
    info(f"页面打开 [{page_id}], 当前页面数: {cnt}")
    return jsonify({"ok": True, "count": cnt})


@bp.route("/page-closed", methods=["POST"])
def page_closed():
    """前端页面关闭时调用，释放页面引用"""
    body = request.get_json(silent=True) or {}
    page_id = body.get("page_id", "")
    with _page_lock:
        if page_id and page_id in _page_last_seen:
            del _page_last_seen[page_id]
        global _last_close_time
        _last_close_time = time.time()
    return jsonify({"ok": True})


@bp.route("/heartbeat", methods=["POST"])
def heartbeat():
    """前端心跳，更新页面 last_seen 时间"""
    body = request.get_json(silent=True) or {}
    page_id = body.get("page_id", "")
    with _page_lock:
        if page_id and page_id in _page_last_seen:
            _page_last_seen[page_id] = time.time()
        elif page_id:
            _page_last_seen[page_id] = time.time()
    return jsonify({"ok": True})


@bp.route("/shutdown", methods=["POST"])
def shutdown():
    """前端请求关闭后端进程"""
    import atexit

    def delayed_exit():
        import time as _time
        _time.sleep(2)
        os._exit(0)

    threading.Thread(target=delayed_exit, daemon=True).start()
    return jsonify({"success": True, "message": "正在关闭..."})


@bp.route("/cleanup-splash", methods=["POST"])
def cleanup_splash():
    """清理安装过程中产生的临时文件"""
    import tempfile
    import glob as _glob
    try:
        tmpdir = tempfile.gettempdir()
        patterns = [
            "nodejs-installer*.msi",
            "git-installer*.exe",
            "cc-switch-installer*.msi",
            "color-cc-install*.ps1",
            "1shot-cc-welcome*.ps1",
            "1shot-cc-run-claude*.ps1",
            "1shot-cc-health-check*.tmp",
            "1shot-cc-test.tmp",
        ]
        cleaned = 0
        for pat in patterns:
            for f in _glob.glob(os.path.join(tmpdir, pat)):
                try:
                    os.remove(f)
                    cleaned += 1
                except Exception:
                    pass
        return jsonify({"success": True, "cleaned": cleaned})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
