"""npm 镜像源和代理配置工具"""
from app.utils.subprocess_runner import run_cmd


def set_npm_mirror() -> dict:
    return run_cmd(
        "npm config set registry https://registry.npmmirror.com",
        timeout=15,
    )


def get_npm_registry() -> str:
    r = run_cmd("npm config get registry", timeout=10)
    return r["stdout"] if r["success"] else ""


def restore_npm_registry() -> dict:
    return run_cmd("npm config delete registry", timeout=15)


def check_github_access() -> dict:
    """检测是否能访问 GitHub，用于判断 CC-Switch 下载策略"""
    r = run_cmd('curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://github.com', timeout=10)
    return {"accessible": r["success"] and "200" in r["stdout"]}
