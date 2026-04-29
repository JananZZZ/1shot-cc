"""/api/install/* — 安装操作 API + SSE 进度推送"""
import json
import os
import tempfile
import threading
import uuid
import time
from flask import Blueprint, jsonify, request, Response

bp = Blueprint("install", __name__, url_prefix="/api/install")

_tasks: dict[str, dict] = {}
_lock = threading.Lock()


def _update_task(task_id: str, step: str, progress: float, message: str, done: bool = False, error: str = ""):
    with _lock:
        _tasks[task_id] = {
            "step": step,
            "progress": progress,
            "message": message,
            "done": done,
            "error": error,
            "updated_at": time.time(),
        }


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _run_in_thread(task_id: str, install_fn, callback=None):
    def _run():
        try:
            install_fn(
                callback=lambda pct, msg: _update_task(task_id, "installing", pct, msg)
                if not callback else callback(pct, msg)
            )
            _update_task(task_id, "complete", 100, "安装完成", done=True)
        except Exception as e:
            _update_task(task_id, "error", 0, str(e), done=True, error=str(e))

    threading.Thread(target=_run, daemon=True).start()


@bp.route("/nodejs", methods=["POST"])
def install_nodejs():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备下载 Node.js...")

    def do_install(callback):
        from app.services.node_installer import download_nodejs, install_nodejs, set_npm_registry_mirror, refresh_path_env

        dl = download_nodejs(callback=callback)
        if not dl["success"]:
            _update_task(task_id, "error", 0, dl["error"], done=True, error=dl["error"])
            return
        inst = install_nodejs(dl["path"], callback=callback)
        if not inst["success"]:
            _update_task(task_id, "error", 0, inst["error"], done=True, error=inst["error"])
            return
        callback(95, "设置 npm 镜像源...")
        set_npm_registry_mirror()
        refresh_path_env()
        callback(100, "Node.js 安装完成！")

    _run_in_thread(task_id, do_install)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/git", methods=["POST"])
def install_git():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备下载 Git for Windows...")

    def do_install(callback):
        from app.services.git_installer import download_git, install_git

        dl = download_git(callback=callback)
        if not dl["success"]:
            _update_task(task_id, "error", 0, dl["error"], done=True, error=dl["error"])
            return
        inst = install_git(dl["path"], callback=callback)
        if not inst["success"]:
            _update_task(task_id, "error", 0, inst["error"], done=True, error=inst["error"])
            return
        callback(100, "Git 安装完成！")

    _run_in_thread(task_id, do_install)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/claude-code", methods=["POST"])
def install_claude_code():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Claude Code...")

    def do_install(callback):
        from app.services.claude_installer import fix_powershell_policy, install_claude_code

        callback(0, "正在修复 PowerShell 执行策略...")
        fix_powershell_policy()

        result = install_claude_code(callback=callback)
        if not result["success"]:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])
            return
        callback(100, "Claude Code 安装完成！")

    _run_in_thread(task_id, do_install)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/ccswitch-gui", methods=["POST"])
def install_ccswitch_gui():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备下载 CC-Switch...")

    def do_install(callback):
        from app.services.ccswitch_installer import download_ccswitch, install_ccswitch

        dl = download_ccswitch(callback=callback)
        if not dl["success"]:
            _update_task(task_id, "error", 0, dl["error"], done=True, error=dl["error"])
            return
        inst = install_ccswitch(dl["path"], callback=callback)
        if not inst["success"]:
            _update_task(task_id, "error", 0, inst["error"], done=True, error=inst["error"])
            return
        callback(100, "CC-Switch 安装完成！")

    _run_in_thread(task_id, do_install)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/ccswitch-cli", methods=["POST"])
def install_ccswitch_cli():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 cc-switch-cli...")

    def do_install(callback):
        from app.services.ccswitch_installer import install_ccswitch_cli

        result = install_ccswitch_cli(callback=callback)
        if not result["success"]:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])
            return
        callback(100, "cc-switch-cli 安装完成！")

    _run_in_thread(task_id, do_install)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/fix-policy", methods=["POST"])
def fix_policy():
    from app.services.claude_installer import fix_powershell_policy
    result = fix_powershell_policy()
    return jsonify(result)


@bp.route("/fix-registry", methods=["POST"])
def fix_registry():
    from app.services.proxy_helper import set_npm_mirror
    result = set_npm_mirror()
    return jsonify(result)


@bp.route("/zhipu-helper", methods=["POST"])
def install_zhipu_helper():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备运行智谱一键配置...")

    def do_install(callback):
        from app.services.claude_installer import install_zhipu_helper
        result = install_zhipu_helper(callback=callback)
        if not result["success"]:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])
            return
        callback(100, "智谱配置完成！")

    _run_in_thread(task_id, do_install)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/launch-powershell", methods=["POST"])
def launch_powershell():
    import subprocess
    try:
        script = (
            'Start-Process powershell -ArgumentList \'-NoExit -Command '
            '"Write-Host \\"============================================\\" -ForegroundColor Cyan; '
            'Write-Host \\"  🚀 1shot-CC — Claude Code 启动就绪！\\" -ForegroundColor Green; '
            'Write-Host \\"============================================\\" -ForegroundColor Cyan; '
            'Write-Host \\"\\"; '
            'Write-Host \\"📌 请在下方输入 claude 并按 Enter 开始：\\" -ForegroundColor Yellow; '
            'Write-Host \\"\\""\''
        )
        subprocess.Popen(script, shell=True, creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@bp.route("/progress/<task_id>")
def progress(task_id):
    def stream():
        last_data = None
        for _ in range(600):
            with _lock:
                task = _tasks.get(task_id, {})
            if task:
                data = {
                    "step": task.get("step", ""),
                    "progress": task.get("progress", 0),
                    "message": task.get("message", ""),
                    "done": task.get("done", False),
                    "error": task.get("error", ""),
                }
                new = json.dumps(data, ensure_ascii=False)
                if new != last_data:
                    last_data = new
                    yield _sse_event(data)
                if task.get("done"):
                    break
            time.sleep(0.5)
        yield _sse_event({"step": "timeout", "progress": 100, "message": "", "done": True, "error": ""})

    response = Response(stream(), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response
