"""诊断日志系统 — 记录到 %TEMP%\1shot-cc\1shot-cc.log"""
import os
import sys
import time
import traceback
import threading

_LOG_DIR = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "1shot-cc")
_LOG_FILE = os.path.join(_LOG_DIR, "1shot-cc.log")
_MAX_SIZE = 2 * 1024 * 1024  # 2MB 轮转
_lock = threading.Lock()
_started = False


def init() -> str:
    """初始化日志目录和文件，返回日志文件路径"""
    global _started
    os.makedirs(_LOG_DIR, exist_ok=True)

    # 轮转：超过 2MB 时备份旧日志
    if os.path.exists(_LOG_FILE) and os.path.getsize(_LOG_FILE) > _MAX_SIZE:
        bak = _LOG_FILE + ".old"
        if os.path.exists(bak):
            os.remove(bak)
        os.rename(_LOG_FILE, bak)

    _started = True
    info("=" * 60)
    info("1shot-CC 诊断日志已启动")
    info(f"日志路径: {_LOG_FILE}")
    _log_system_info()
    return _LOG_FILE


def get_log_path() -> str:
    return _LOG_FILE


def get_log_dir() -> str:
    return _LOG_DIR


def _log_system_info():
    """记录系统环境信息"""
    import platform
    info(f"操作系统: {platform.platform()}")
    info(f"Windows 版本: {platform.win32_ver()[0] if sys.platform == 'win32' else 'N/A'}")
    info(f"系统架构: {platform.machine()}")
    info(f"Python 版本: {sys.version}")
    info(f"当前工作目录: {os.getcwd()}")

    # PyInstaller 打包检测
    if getattr(sys, 'frozen', False):
        info(f"运行模式: PyInstaller 打包 (路径: {sys._MEIPASS})")
    else:
        info("运行模式: 源码直跑")

    # 管理员权限
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        info(f"管理员权限: {'是' if is_admin else '否'}")
    except Exception:
        info("管理员权限: 无法检测")

    # 磁盘空间
    try:
        import shutil
        for label, path in [("TEMP", _LOG_DIR), ("系统盘", "C:\\")]:
            try:
                usage = shutil.disk_usage(path)
                free_gb = usage.free / (1024 ** 3)
                info(f"磁盘剩余 ({label}): {free_gb:.1f} GB")
            except Exception:
                pass
    except Exception:
        pass

    # 环境变量
    for var in ["APPDATA", "LOCALAPPDATA", "TEMP", "USERNAME", "COMPUTERNAME"]:
        val = os.environ.get(var, "")
        info(f"环境变量 {var}: {val}")


def _write(level: str, msg: str):
    if not _started:
        return
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}\n"
    try:
        with _lock:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line)
    except Exception:
        pass


def debug(msg: str):
    _write("DEBUG", msg)


def info(msg: str):
    _write("INFO", msg)


def warning(msg: str):
    _write("WARN", msg)


def error(msg: str, exc_info: bool = False):
    _write("ERROR", msg)
    if exc_info:
        _write("ERROR", traceback.format_exc())


def exception(msg: str):
    """记录异常消息 + 完整堆栈"""
    _write("ERROR", f"{msg}\n{traceback.format_exc()}")
