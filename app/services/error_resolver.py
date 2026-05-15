"""错误知识库 — 将原始错误码翻译为可操作的诊断和修复方案"""
import re

from app.utils.logger import info, warning


# ─── MSI 安装错误 ───
MSI_ERRORS = {
    1602: {
        "title": "安装被用户取消",
        "causes": ["用户点击了取消按钮", "另一个程序终止了安装"],
        "auto_fix": [],
        "manual_fix": ["重新点击安装按钮即可"],
    },
    1603: {
        "title": "安装程序遇到致命错误",
        "causes": [
            "磁盘空间不足（系统盘需要至少 2GB 剩余空间）",
            "当前没有管理员权限",
            "杀毒软件（Windows Defender / 360 等）拦截了安装程序",
            "之前装过同款软件但没有卸载干净，注册表有残留",
        ],
        "auto_fix": ["clean_temp", "fix_msi_service"],
        "manual_fix": [
            "1. 右键 1shot-CC.exe, 选择 '以管理员身份运行'",
            "2. 临时关闭杀毒软件再试",
            "3. 去[控制面板 -> 程序和功能]卸载旧的 Node.js / Git",
            "4. 手动下载安装包: https://nodejs.org (选 LTS 版本)",
            "5. 如果还不行, 开始菜单搜索 cmd, 右键以管理员运行, 输入: msiexec /unregister 回车, 再输入: msiexec /regserver 回车",
        ],
    },
    1612: {
        "title": "安装源文件损坏",
        "causes": ["下载的安装包不完整或损坏", "网络传输过程中数据丢失"],
        "auto_fix": ["recreate_temp_dir", "reinstall_web_view2"],
        "manual_fix": [
            "1. 程序会自动重新下载，请点击重试",
            "2. 如果多次失败，尝试手动从官网下载对应软件安装",
        ],
    },
    1618: {
        "title": "已有另一个安装程序在运行",
        "causes": ["另一个软件正在安装中", "上一个安装还没完全结束"],
        "auto_fix": [],
        "manual_fix": [
            "1. 等待当前安装完成",
            "2. 如果确认没有其他安装，重启电脑后再试",
        ],
    },
    1619: {
        "title": "无法打开安装包文件",
        "causes": ["安装包文件被删除或移动", "临时目录权限异常", "杀毒软件删除了安装包"],
        "auto_fix": ["recreate_temp_dir"],
        "manual_fix": [
            "1. 临时关闭杀毒软件后重试",
            "2. 检查 C 盘是否有足够空间",
        ],
    },
    1620: {
        "title": "安装包与系统不匹配（32/64位）",
        "causes": ["系统是 32 位但下载了 64 位安装包"],
        "auto_fix": [],
        "manual_fix": ["1. 确认你的 Windows 是 64 位系统（右键此电脑→属性）",
                       "2. 如果是 32 位系统，需要手动下载 32 位版本的软件"],
    },
    1638: {
        "title": "已安装另一个版本",
        "causes": ["此软件已有另一个版本安装在电脑上"],
        "auto_fix": [],
        "manual_fix": [
            "1. 去「控制面板 → 程序和功能」卸载已有的 Node.js",
            "2. 或者：如果版本差距不大，可以跳过此安装步骤",
        ],
    },
    1641: {
        "title": "安装被 Windows 安装服务中断",
        "causes": ["Windows Installer 服务异常"],
        "auto_fix": ["fix_msi_service"],
        "manual_fix": [
            "1. 重启电脑后再试",
            "2. 以管理员身份打开 cmd，运行: sfc /scannow",
        ],
    },
    3010: {
        "title": "安装成功，但需要重启电脑",
        "causes": ["安装程序修改了系统核心组件，需要重启才能生效"],
        "auto_fix": [],
        "manual_fix": [
            "1. 保存当前工作，重启电脑",
            "2. 重启后 Node.js 即可正常使用",
        ],
    },
}

# ─── 通用错误 ───
GENERAL_ERRORS = {
    "disk_space": {
        "title": "磁盘空间不足",
        "causes": ["系统盘剩余空间太少"],
        "auto_fix": ["clean_temp"],
        "manual_fix": [
            "1. 清理回收站",
            "2. 删除临时文件: 打开文件管理器 → 地址栏输入 %TEMP% → 全选删除",
            "3. 卸载不用的软件",
        ],
    },
    "temp_dir": {
        "title": "临时目录无法使用",
        "causes": ["%TEMP% 目录不存在或无法写入"],
        "auto_fix": ["recreate_temp_dir"],
        "manual_fix": [
            "1. 打开文件管理器 → 地址栏输入 %TEMP% → 确认能进入",
            "2. 如果不能进入，创建一个新文件夹 C:\\Temp",
            "3. 右键此电脑→属性→高级系统设置→环境变量→将 TEMP 改为 C:\\Temp",
        ],
    },
    "no_admin": {
        "title": "缺少管理员权限",
        "causes": ["安装系统级软件需要管理员权限"],
        "auto_fix": [],
        "manual_fix": [
            "1. 关闭程序, 右键 1shot-CC.exe, 选择 '以管理员身份运行'",
        ],
    },
    "antivirus": {
        "title": "杀毒软件可能正在拦截",
        "causes": ["Windows Defender 或第三方杀毒软件实时扫描可能阻断安装"],
        "auto_fix": [],
        "manual_fix": [
            "1. 临时关闭 Windows Defender 的实时保护",
            "2. 关闭路径: 开始→设置→更新和安全→Windows安全中心→病毒和威胁防护→管理设置→关闭实时保护",
            "3. 安装完成后记得重新开启",
        ],
    },
    "network": {
        "title": "网络连接异常",
        "causes": ["无法连接到下载服务器", "DNS 解析失败", "防火墙拦截"],
        "auto_fix": [],
        "manual_fix": [
            "1. 检查电脑是否能正常上网",
            "2. 尝试切换网络（如手机热点）",
            "3. 如果用了代理/VPN，尝试关闭后重试",
            "4. 手动从官网下载安装包: https://nodejs.org",
        ],
    },
}


def resolve(error_str: str) -> dict:
    """
    解析错误信息，返回结构化诊断：
    {title, causes: [str], auto_fix: [str], manual_fix: [str], raw_error: str}
    """
    info(f"解析错误: {error_str[:200]}")

    # 1) 尝试匹配 MSI 返回码
    m = re.search(r'返回码[:\s]*(\d+)', error_str)
    if m:
        code = int(m.group(1))
        if code in MSI_ERRORS:
            entry = MSI_ERRORS[code]
            return {**entry, "raw_error": error_str, "error_code": code, "category": "msi"}

    # 2) 尝试匹配 MSI 错误码在 stderr/stdout 中
    m = re.search(r'(?:error|failed|failure).*?(\d{4})', error_str, re.IGNORECASE)
    if m:
        code = int(m.group(1))
        if code in MSI_ERRORS:
            entry = MSI_ERRORS[code]
            return {**entry, "raw_error": error_str, "error_code": code, "category": "msi"}

    # 3) 按关键词匹配通用错误
    lower = error_str.lower()
    if any(kw in lower for kw in ("disk", "space", "enough space", "no space", "磁盘空间", "空间不足")):
        return {**GENERAL_ERRORS["disk_space"], "raw_error": error_str, "category": "system"}
    if any(kw in lower for kw in ("temp", "临时", "tmp", "permission denied")):
        return {**GENERAL_ERRORS["temp_dir"], "raw_error": error_str, "category": "system"}
    if any(kw in lower for kw in ("admin", "permission", "elevation", "access denied", "权限", "管理员")):
        return {**GENERAL_ERRORS["no_admin"], "raw_error": error_str, "category": "system"}
    if any(kw in lower for kw in ("antivirus", "defender", "blocked", "quarantine", "杀毒", "拦截")):
        return {**GENERAL_ERRORS["antivirus"], "raw_error": error_str, "category": "system"}
    if any(kw in lower for kw in ("timeout", "timed out", "host", "dns", "resolve", "超时", "连接失败",
                                   "connection refused", "network", "unreachable")):
        return {**GENERAL_ERRORS["network"], "raw_error": error_str, "category": "network"}

    # 4) 默认 fallback
    info(f"未匹配到已知错误模式，使用默认诊断: {error_str[:100]}")
    return {
        "title": "安装出错了",
        "causes": [
            "可能是系统环境差异导致",
            "网络不稳定导致下载失败",
            "权限不足导致安装被阻止",
        ],
        "auto_fix": [],
        "manual_fix": [
            "1. 右键 1shot-CC.exe → 以管理员身份运行",
            "2. 检查网络连接是否正常",
            "3. 重启电脑后再来一次",
            "4. 查看日志文件获取更多信息",
        ],
        "raw_error": error_str,
        "category": "unknown",
    }


def try_auto_fix(fix_names: list[str]) -> dict:
    """执行自动修复，返回 {fixed: [str], failed: [str]}"""
    fixed = []
    failed = []

    for name in fix_names:
        try:
            if name == "clean_temp":
                _auto_clean_temp()
                fixed.append("已清理临时文件")
            elif name == "recreate_temp_dir":
                _auto_recreate_temp_dir()
                fixed.append("已重建临时目录")
            elif name == "fix_msi_service":
                _auto_fix_msi_service()
                fixed.append("已重置 Windows Installer 服务")
            elif name == "retry_as_admin":
                failed.append("请右键 1shot-CC.exe → 以管理员身份运行后重试")
            else:
                failed.append(f"未知的自动修复类型: {name}")
        except Exception as e:
            warning(f"自动修复 [{name}] 失败: {e}")
            failed.append(f"{name}: {e}")

    return {"fixed": fixed, "failed": failed}


def _auto_clean_temp():
    """清理临时目录中的安装残留"""
    import tempfile
    import os as _os
    tmpdir = tempfile.gettempdir()
    patterns = ["nodejs-installer", "git-installer", "cc-switch-installer"]
    for f in _os.listdir(tmpdir):
        for pat in patterns:
            if pat in f.lower():
                try:
                    _os.remove(_os.path.join(tmpdir, f))
                    info(f"已清理: {f}")
                except Exception:
                    pass


def _auto_recreate_temp_dir():
    """确保临时目录存在且可写"""
    import tempfile
    import os as _os
    tmpdir = tempfile.gettempdir()
    _os.makedirs(tmpdir, exist_ok=True)
    # 尝试写入测试文件
    test_file = _os.path.join(tmpdir, "1shot-cc-test.tmp")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        _os.remove(test_file)
    except Exception:
        # 尝试备用临时目录
        alt_tmp = _os.path.join(_os.environ.get("USERPROFILE", "C:\\"), "1shot-cc-temp")
        _os.makedirs(alt_tmp, exist_ok=True)
        _os.environ["TEMP"] = alt_tmp
        _os.environ["TMP"] = alt_tmp
        info(f"临时目录已切换到: {alt_tmp}")


def _auto_fix_msi_service():
    """重置 Windows Installer 服务"""
    import subprocess
    cmds = [
        "msiexec /unregister",
        "msiexec /regserver",
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            info(f"MSI 服务命令已执行: {cmd}")
        except Exception as e:
            warning(f"MSI 服务命令失败 [{cmd}]: {e}")
