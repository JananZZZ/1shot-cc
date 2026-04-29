"""Claude Code 安装服务"""
import json
import os
import sys
import subprocess

from app.utils.subprocess_runner import run_cmd, run_powershell
from app.utils.path_helper import get_claude_json_path, get_claude_config_dir


def fix_powershell_policy() -> dict:
    script = "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    r = run_powershell(script, timeout=15)
    return {"success": r["success"], "error": r["stderr"] if not r["success"] else ""}


def install_claude_code(callback=None) -> dict:
    if callback:
        callback(0, "正在设置 npm 淘宝镜像...")

    run_cmd("npm config set registry https://registry.npmmirror.com", timeout=10)

    if callback:
        callback(5, "正在安装 Claude Code（可能需要几分钟）...")

    cmd = "npm install -g @anthropic-ai/claude-code"
    try:
        env = os.environ.copy()
        env["npm_config_registry"] = "https://registry.npmmirror.com"
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

        output_lines = []
        for line in iter(process.stdout.readline, ""):
            if line:
                output_lines.append(line.rstrip())
                if callback and len(output_lines) % 5 == 0:
                    pct = min(10 + len(output_lines) * 0.5, 90)
                    callback(pct, line.rstrip()[:120])

        process.wait(timeout=600)
        if process.returncode == 0:
            if callback:
                callback(95, "写入配置文件...")
            write_onboarding_config()
            if callback:
                callback(100, "Claude Code 安装完成！")
            return {"success": True, "output": "\n".join(output_lines[-20:])}
        else:
            return {"success": False, "error": "\n".join(output_lines[-10:])}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "安装超时（超过10分钟）"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_onboarding_config() -> dict:
    path = get_claude_json_path()
    try:
        data = {}
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["hasCompletedOnboarding"] = True
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def install_zhipu_helper(callback=None) -> dict:
    if callback:
        callback(0, "正在运行智谱一键配置工具...")
    r = run_cmd("npx @z_ai/coding-helper", timeout=120)
    return {"success": r["success"], "output": r["stdout"], "error": r["stderr"]}
