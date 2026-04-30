"""/api/install/* — 安装操作 API + SSE 进度推送"""
import json
import os
import subprocess
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
            "step": step, "progress": progress, "message": message,
            "done": done, "error": error, "updated_at": time.time(),
        }


def _sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


def _bg(task_id: str, work):
    """在后台线程运行 work(callback)，统一异常处理"""
    def _runner():
        def cb(pct, msg):
            _update_task(task_id, "installing", pct, msg)
        try:
            work(cb)
        except Exception as e:
            _update_task(task_id, "error", 0, str(e), done=True, error=str(e))
    threading.Thread(target=_runner, daemon=True).start()


# ─── 系统依赖安装 ───

@bp.route("/nodejs", methods=["POST"])
def install_nodejs():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Node.js...")

    def work(callback):
        from app.services.node_installer import download_nodejs, install_nodejs, set_npm_registry_mirror, refresh_path_env
        dl = download_nodejs(callback=callback)
        if not dl["success"]:
            _update_task(task_id, "error", 0, dl["error"], done=True, error=dl["error"])
            return
        inst = install_nodejs(dl["path"], callback=callback)
        if not inst["success"]:
            _update_task(task_id, "error", 0, inst["error"], done=True, error=inst["error"])
            return
        callback(90, "正在配置国内加速镜像...")
        set_npm_registry_mirror()
        refresh_path_env()
        _update_task(task_id, "complete", 100, "Node.js 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/git", methods=["POST"])
def install_git():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Git...")

    def work(callback):
        from app.services.git_installer import download_git, install_git
        dl = download_git(callback=callback)
        if not dl["success"]:
            _update_task(task_id, "error", 0, dl["error"], done=True, error=dl["error"])
            return
        inst = install_git(dl["path"], callback=callback)
        if not inst["success"]:
            _update_task(task_id, "error", 0, inst["error"], done=True, error=inst["error"])
            return
        _update_task(task_id, "complete", 100, "Git 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/claude-code", methods=["POST"])
def install_claude_code():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Claude Code...")

    def work(callback):
        from app.services.claude_installer import fix_powershell_policy, install_claude_code
        callback(0, "正在调整系统安全设置...")
        fix_powershell_policy()
        callback(5, "正在从网络下载 Claude Code（需要几分钟）...")
        result = install_claude_code(callback=callback)
        if not result["success"]:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])
            return
        _update_task(task_id, "complete", 100, "Claude Code 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── CC-Switch ───

@bp.route("/ccswitch-gui", methods=["POST"])
def install_ccswitch_gui():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "正在获取 CC-Switch 下载地址...")

    def work(callback):
        from app.services.ccswitch_installer import download_ccswitch, install_ccswitch
        dl = download_ccswitch(callback=callback)
        if not dl["success"]:
            _update_task(task_id, "error", 0, dl["error"], done=True, error=dl["error"])
            return
        inst = install_ccswitch(dl["path"], callback=callback)
        if not inst["success"]:
            _update_task(task_id, "error", 0, inst["error"], done=True, error=inst["error"])
            return
        _update_task(task_id, "complete", 100, "CC-Switch 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/ccswitch-cli", methods=["POST"])
def install_ccswitch_cli():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 CC-Switch CLI...")

    def work(callback):
        from app.services.ccswitch_installer import install_ccswitch_cli
        result = install_ccswitch_cli(callback=callback)
        if not result["success"]:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])
            return
        _update_task(task_id, "complete", 100, "CC-Switch CLI 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── 快速修复 ───

@bp.route("/fix-policy", methods=["POST"])
def fix_policy():
    from app.services.claude_installer import fix_powershell_policy
    return jsonify(fix_powershell_policy())


@bp.route("/fix-registry", methods=["POST"])
def fix_registry():
    from app.services.proxy_helper import set_npm_mirror
    return jsonify(set_npm_mirror())


@bp.route("/zhipu-helper", methods=["POST"])
def install_zhipu_helper():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备运行智谱配置工具...")

    def work(callback):
        from app.services.claude_installer import install_zhipu_helper
        result = install_zhipu_helper(callback=callback)
        if not result["success"]:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])
            return
        _update_task(task_id, "complete", 100, "智谱配置完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── 一键启动 ───

@bp.route("/launch-powershell", methods=["POST"])
def launch_powershell():
    """在新窗口打开带引导信息的 PowerShell"""
    from app.services.launcher import launch_powershell_with_guide
    result = launch_powershell_with_guide()
    return jsonify(result)


@bp.route("/launch-ccswitch", methods=["POST"])
def launch_ccswitch():
    """启动 CC-Switch 桌面应用"""
    from app.services.launcher import launch_ccswitch_app
    result = launch_ccswitch_app()
    return jsonify(result)


@bp.route("/launch-claude", methods=["POST"])
def launch_claude():
    """在 PowerShell 中启动 Claude Code"""
    from app.services.launcher import launch_claude_in_powershell
    result = launch_claude_in_powershell()
    return jsonify(result)


# ─── Windows Terminal ───

@bp.route("/winterm", methods=["POST"])
def install_winterm():
    """安装 Windows Terminal（winget 静默安装）"""
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Windows Terminal...")

    def work(callback):
        import subprocess
        callback(5, "正在通过 winget 安装 Windows Terminal...")
        try:
            proc = subprocess.run(
                ["winget", "install", "--silent", "--accept-package-agreements", "Microsoft.WindowsTerminal"],
                capture_output=True, text=True, timeout=300,
                encoding="utf-8", errors="replace",
            )
            if proc.returncode == 0:
                _update_task(task_id, "complete", 100, "Windows Terminal 安装完成！", done=True)
            else:
                err = proc.stderr[:200] if proc.stderr else f"返回码: {proc.returncode}"
                _update_task(task_id, "error", 0, f"安装失败: {err}", done=True, error=err)
        except subprocess.TimeoutExpired:
            _update_task(task_id, "error", 0, "安装超时", done=True, error="安装超时")
        except FileNotFoundError:
            _update_task(task_id, "error", 0,
                "未找到 winget 命令。请确保系统已安装 App Installer。",
                done=True, error="winget 不可用")
        except Exception as e:
            _update_task(task_id, "error", 0, str(e), done=True, error=str(e))

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── Color-cc ───

@bp.route("/colorcc", methods=["POST"])
def install_colorcc():
    """安装 Color-cc 终端美化"""
    from app.services.colorcc_installer import install_colorcc
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Color-cc...")

    def work(callback):
        result = install_colorcc(callback=callback)
        if result.get("partial"):
            _update_task(task_id, "complete", 100, result.get("message", "安装完成，请手动配置。"), done=True)
        elif result["success"]:
            _update_task(task_id, "complete", 100, result["message"], done=True)
        else:
            _update_task(task_id, "error", 0, result["error"], done=True, error=result["error"])

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/colorcc-check", methods=["GET"])
def check_colorcc():
    """检测 Windows Terminal 是否已安装"""
    from app.services.colorcc_installer import check_windows_terminal
    result = check_windows_terminal()
    result["success"] = True
    return jsonify(result)


# ─── SSE 进度 ───

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
