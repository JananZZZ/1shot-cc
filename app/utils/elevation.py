# -*- coding: utf-8 -*-
"""管理员权限检测与提权"""
import ctypes
import os

from app.utils.logger import info, warning


def is_admin() -> bool:
    """检测当前进程是否以管理员身份运行"""
    try:
        result = ctypes.windll.shell32.IsUserAnAdmin() != 0
        info(f"管理员权限检测: {'是' if result else '否'}")
        return result
    except Exception as e:
        warning(f"管理员权限检测失败: {e}")
        return False


def get_user_display_name() -> str:
    """获取当前用户名"""
    return os.environ.get("USERNAME", "未知")


def get_require_admin_components() -> list:
    """返回需要用管理员权限安装的组件列表"""
    return ["nodejs", "git", "ccswitch-gui"]


def needs_admin_for(component: str) -> bool:
    """判断某组件是否需要管理员权限安装"""
    admin_components = get_require_admin_components()
    return component in admin_components


def format_admin_warning() -> str:
    """生成提权提示文本"""
    lines = [
        "当前未以管理员身份运行, 安装系统级软件 (Node.js, Git 等) 可能会失败.",
        "",
        "请关闭程序, 右键 1shot-CC.exe, 选择 '以管理员身份运行'.",
        "",
        "或者: 如果只想安装不需要管理员权限的组件, 可以跳过系统软件安装步骤.",
    ]
    return "\n".join(lines)
