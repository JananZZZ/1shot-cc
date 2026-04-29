"""子进程管理工具"""
import subprocess
import sys
import os
import time


def run_powershell(script: str, timeout: int = 120) -> dict:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "命令执行超时", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def run_cmd(command: str, timeout: int = 120, cwd: str = None) -> dict:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "命令执行超时", "returncode": -1}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def run_cmd_stream(cmd: str, cwd: str = None):
    """流式执行命令，逐行产出 stdout"""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=True,
            encoding="utf-8",
            errors="replace",
            cwd=cwd,
            bufsize=1,
        )
        for line in iter(process.stdout.readline, ""):
            if line:
                yield line.rstrip()
        process.stdout.close()
        process.wait()
        yield f"__EXIT_CODE__:{process.returncode}"
    except Exception as e:
        yield f"__ERROR__:{e}"
