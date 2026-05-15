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
    from app.services.node_installer import preflight_nodejs

    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "正在检查安装环境...")

    pre = preflight_nodejs()
    if not pre["ok"]:
        issues = pre["issues"]
        title = issues[0] if issues else "安装前检查发现问题"
        return jsonify({
            "success": False,
            "error": f"Node.js 预检发现问题: {'; '.join(issues)}",
            "error_detail": {
                "title": "安装前需要注意",
                "causes": issues,
                "auto_fix": [],
                "manual_fix": ["请先解决上述问题，再点击重试"],
                "raw_error": "; ".join(issues),
                "category": "system",
            },
        })

    def work(callback):
        from app.services.node_installer import download_nodejs, install_nodejs, set_npm_registry_mirror, refresh_path_env
        from app.services.error_resolver import resolve
        dl = download_nodejs(callback=callback)
        if not dl["success"]:
            diag = resolve(dl["error"])
            _update_task(task_id, "error", 0, dl["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
            return
        inst = install_nodejs(dl["path"], callback=callback)
        if not inst["success"]:
            diag = resolve(inst["error"])
            _update_task(task_id, "error", 0, inst["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
            return
        callback(90, "正在配置国内加速镜像...")
        set_npm_registry_mirror()
        refresh_path_env()
        _update_task(task_id, "complete", 100, "Node.js 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/git", methods=["POST"])
def install_git():
    from app.services.git_installer import preflight_git

    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "正在检查安装环境...")

    pre = preflight_git()
    if not pre["ok"]:
        issues = pre["issues"]
        return jsonify({
            "success": False,
            "error": f"Git 预检发现问题: {'; '.join(issues)}",
            "error_detail": {
                "title": "安装前需要注意",
                "causes": issues,
                "auto_fix": [],
                "manual_fix": ["请先解决上述问题，再点击重试"],
                "raw_error": "; ".join(issues),
                "category": "system",
            },
        })

    def work(callback):
        from app.services.git_installer import download_git, install_git
        from app.services.error_resolver import resolve
        dl = download_git(callback=callback)
        if not dl["success"]:
            diag = resolve(dl["error"])
            _update_task(task_id, "error", 0, dl["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
            return
        inst = install_git(dl["path"], callback=callback)
        if not inst["success"]:
            diag = resolve(inst["error"])
            _update_task(task_id, "error", 0, inst["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
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
        from app.services.error_resolver import resolve
        callback(0, "正在调整系统安全设置...")
        fix_powershell_policy()
        callback(5, "正在从网络下载 Claude Code（需要几分钟）...")
        result = install_claude_code(callback=callback)
        if not result["success"]:
            diag = resolve(result["error"])
            _update_task(task_id, "error", 0, result["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
            return
        _update_task(task_id, "complete", 100, "Claude Code 安装完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── CC-Switch ───

@bp.route("/ccswitch-gui", methods=["POST"])
def install_ccswitch_gui():
    from app.services.ccswitch_installer import preflight_ccswitch

    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "正在检查安装环境...")

    pre = preflight_ccswitch()
    if not pre["ok"]:
        issues = pre["issues"]
        return jsonify({
            "success": False,
            "error": f"CC-Switch 预检发现问题: {'; '.join(issues)}",
            "error_detail": {
                "title": "安装前需要注意",
                "causes": issues,
                "auto_fix": [],
                "manual_fix": ["请先解决上述问题，再点击重试"],
                "raw_error": "; ".join(issues),
                "category": "system",
            },
        })

    def work(callback):
        from app.services.ccswitch_installer import download_ccswitch, install_ccswitch
        from app.services.error_resolver import resolve
        dl = download_ccswitch(callback=callback)
        if not dl["success"]:
            diag = resolve(dl["error"])
            if dl.get("hint_cli"):
                diag["hint_cli"] = True
            _update_task(task_id, "error", 0, dl["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
            return
        inst = install_ccswitch(dl["path"], callback=callback)
        if not inst["success"]:
            diag = resolve(inst["error"])
            _update_task(task_id, "error", 0, inst["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
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
        from app.services.error_resolver import resolve
        result = install_ccswitch_cli(callback=callback)
        if not result["success"]:
            diag = resolve(result["error"])
            _update_task(task_id, "error", 0, result["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
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


@bp.route("/auto-fix", methods=["POST"])
def auto_fix():
    """批量自动修复已知问题（策略 + 镜像源）"""
    from app.services.claude_installer import fix_powershell_policy
    from app.services.proxy_helper import set_npm_mirror

    results = {}
    p = fix_powershell_policy()
    results["policy"] = {"success": p["success"], "error": p.get("error", "")}

    r = set_npm_mirror()
    results["registry"] = {"success": r["success"], "error": r.get("stderr", "")}

    all_ok = results["policy"]["success"] and results["registry"]["success"]
    return jsonify({"success": all_ok, "results": results})


# ─── 智谱助手 ───

@bp.route("/zhipu-helper", methods=["POST"])
def install_zhipu_helper():
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备运行智谱配置工具...")

    def work(callback):
        from app.services.claude_installer import install_zhipu_helper
        from app.services.error_resolver import resolve
        result = install_zhipu_helper(callback=callback)
        if not result["success"]:
            diag = resolve(result["error"])
            _update_task(task_id, "error", 0, result["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
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
        from app.services.error_resolver import resolve
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
                diag = resolve(err)
                _update_task(task_id, "error", 0, f"安装失败: {err}", done=True, error=json.dumps(diag, ensure_ascii=False))
        except subprocess.TimeoutExpired:
            diag = resolve("安装超时")
            _update_task(task_id, "error", 0, "安装超时", done=True, error=json.dumps(diag, ensure_ascii=False))
        except FileNotFoundError:
            diag = resolve("winget 不可用")
            _update_task(task_id, "error", 0,
                "未找到 winget 命令。请确保系统已安装 App Installer。",
                done=True, error=json.dumps(diag, ensure_ascii=False))
        except Exception as e:
            diag = resolve(str(e))
            _update_task(task_id, "error", 0, str(e), done=True, error=json.dumps(diag, ensure_ascii=False))

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── Color-cc ───

@bp.route("/colorcc", methods=["POST"])
def install_colorcc():
    """安装 Color-cc 终端美化"""
    from app.services.colorcc_installer import install_colorcc
    from app.services.error_resolver import resolve
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "准备安装 Color-cc...")

    def work(callback):
        result = install_colorcc(callback=callback)
        if result.get("partial"):
            _update_task(task_id, "complete", 100, result.get("message", "安装完成，请手动配置。"), done=True)
        elif result["success"]:
            _update_task(task_id, "complete", 100, result["message"], done=True)
        else:
            diag = resolve(result["error"])
            _update_task(task_id, "error", 0, result["error"], done=True, error=json.dumps(diag, ensure_ascii=False))

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


@bp.route("/colorcc-check", methods=["GET"])
def check_colorcc():
    """检测 Windows Terminal 是否已安装"""
    from app.services.colorcc_installer import check_windows_terminal
    result = check_windows_terminal()
    result["success"] = True
    return jsonify(result)


# ─── 升级 ───

@bp.route("/upgrade/<component>", methods=["POST"])
def upgrade_component(component: str):
    """升级指定组件"""
    valid = {"nodejs", "git", "claude", "ccswitch", "ccswitch-cli"}
    if component not in valid:
        return jsonify({"success": False, "error": f"不支持的升级组件: {component}"})

    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, f"准备升级 {component}...")

    def work(callback):
        from app.services.error_resolver import resolve

        if component == "nodejs":
            from app.services.node_installer import download_nodejs, install_nodejs, refresh_path_env
            dl = download_nodejs(callback=callback)
            if not dl["success"]:
                diag = resolve(dl["error"])
                _update_task(task_id, "error", 0, dl["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            inst = install_nodejs(dl["path"], callback=callback)
            if not inst["success"]:
                diag = resolve(inst["error"])
                _update_task(task_id, "error", 0, inst["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            refresh_path_env()
            _update_task(task_id, "complete", 100, "Node.js 升级完成！", done=True)

        elif component == "git":
            from app.services.git_installer import download_git, install_git
            dl = download_git(callback=callback)
            if not dl["success"]:
                diag = resolve(dl["error"])
                _update_task(task_id, "error", 0, dl["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            inst = install_git(dl["path"], callback=callback)
            if not inst["success"]:
                diag = resolve(inst["error"])
                _update_task(task_id, "error", 0, inst["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            _update_task(task_id, "complete", 100, "Git 升级完成！", done=True)

        elif component == "claude":
            from app.services.claude_installer import install_claude_code, fix_powershell_policy
            callback(0, "正在调整策略...")
            fix_powershell_policy()
            result = install_claude_code(callback=callback)
            if not result["success"]:
                diag = resolve(result["error"])
                _update_task(task_id, "error", 0, result["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            _update_task(task_id, "complete", 100, "Claude Code 升级完成！", done=True)

        elif component == "ccswitch":
            from app.services.ccswitch_installer import download_ccswitch, install_ccswitch
            dl = download_ccswitch(callback=callback)
            if not dl["success"]:
                diag = resolve(dl["error"])
                if dl.get("hint_cli"):
                    diag["hint_cli"] = True
                _update_task(task_id, "error", 0, dl["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            inst = install_ccswitch(dl["path"], callback=callback)
            if not inst["success"]:
                diag = resolve(inst["error"])
                _update_task(task_id, "error", 0, inst["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            _update_task(task_id, "complete", 100, "CC-Switch 升级完成！", done=True)

        elif component == "ccswitch-cli":
            from app.services.ccswitch_installer import install_ccswitch_cli
            result = install_ccswitch_cli(callback=callback)
            if not result["success"]:
                diag = resolve(result["error"])
                _update_task(task_id, "error", 0, result["error"], done=True, error=json.dumps(diag, ensure_ascii=False))
                return
            _update_task(task_id, "complete", 100, "CC-Switch CLI 升级完成！", done=True)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


# ─── 卸载 ───

@bp.route("/uninstall-status", methods=["GET"])
def uninstall_status():
    """获取当前所有组件的安装状态（强制刷新，不走缓存）"""
    from app.services.detector import clear_cache
    from app.services.uninstaller import detect_all
    clear_cache()  # 卸载前强制刷新检测结果
    results = detect_all()
    return jsonify({"success": True, "data": results})


@bp.route("/uninstall-all", methods=["POST"])
def uninstall_all():
    """一键卸载选定组件"""
    from app.services.uninstaller import uninstall_all, backup_configs
    body = request.get_json(silent=True) or {}
    selected = body.get("components", [])

    if not selected:
        return jsonify({"success": False, "error": "请选择要卸载的组件"})

    backup_dir = backup_configs()

    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, "开始卸载...")

    def work(callback):
        result = uninstall_all(selected, callback=callback)
        if result["success"]:
            _update_task(task_id, "complete", 100, "卸载完成！", done=True)
        else:
            errs = "; ".join(result["errors"]) if result["errors"] else "部分卸载失败"
            _update_task(task_id, "error", 0, errs, done=True, error=errs)

    _bg(task_id, work)
    return jsonify({
        "success": True,
        "task_id": task_id,
        "backup_dir": backup_dir or "",
    })


@bp.route("/uninstall-single/<component>", methods=["POST"])
def uninstall_single(component: str):
    """卸载单个组件"""
    from app.services.uninstaller import detect_all, uninstall_all
    from app.services.uninstaller import backup_configs

    all_items = detect_all()
    if component not in all_items:
        return jsonify({"success": False, "error": f"未知组件: {component}"})

    backup_configs()
    task_id = str(uuid.uuid4())[:8]
    _update_task(task_id, "preparing", 0, f"准备卸载 {component}...")

    def work(callback):
        result = uninstall_all([component], callback=callback)
        if result["success"]:
            _update_task(task_id, "complete", 100, f"{component} 卸载完成！", done=True)
        else:
            errs = "; ".join(result["errors"]) if result["errors"] else "卸载失败"
            _update_task(task_id, "error", 0, errs, done=True, error=errs)

    _bg(task_id, work)
    return jsonify({"success": True, "task_id": task_id})


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
                # 尝试解析 error 为 JSON，作为 error_detail 传递给前端
                if task.get("error"):
                    try:
                        data["error_detail"] = json.loads(task["error"])
                    except (json.JSONDecodeError, TypeError):
                        pass
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
