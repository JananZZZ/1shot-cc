"""启动健康检查 — 在 Flask 应用启动前运行，检测潜在问题"""
import os
import shutil
import tempfile
import platform

from app.utils.logger import info, warning


def run_startup_checks() -> list[dict]:
    """运行所有启动检查，返回问题列表 [{level, check, message, detail}]"""
    results = []

    results.append(_check_windows_version())
    results.append(_check_disk_space())
    results.append(_check_temp_dir())
    results.append(_check_admin())
    results.append(_check_vcredist())
    results.append(_check_chinese_path())

    problems = [r for r in results if r.get("level") in ("error", "warning")]
    ok_count = len(results) - len(problems)
    info(f"启动检查完成: {ok_count} 通过, {len(problems)} 问题")
    for p in problems:
        warning(f"启动问题 [{p['check']}]: {p['message']}")

    return results


def _check_windows_version() -> dict:
    info("启动检查: Windows 版本...")
    result = {"check": "windows_version", "level": "ok", "message": ""}
    try:
        ver = platform.win32_ver()
        if ver[0]:
            try:
                major = int(ver[0].split(".")[0]) if ver[0] else 0
            except ValueError:
                major = 10
            info(f"Windows 版本: {ver[0]} (major={major})")
            if major < 10:
                result["level"] = "error"
                result["message"] = "你的 Windows 版本过低"
                result["detail"] = (
                    f"当前系统: Windows {ver[0]}\n"
                    "1shot-CC 需要 Windows 10 或更高版本。\n"
                    "请升级系统后再使用。"
                )
                return result
        result["message"] = f"Windows {ver[0]}" if ver[0] else "Windows (版本未知)"
        return result
    except Exception as e:
        warning(f"Windows 版本检测失败: {e}")
        result["message"] = "无法检测 Windows 版本"
        return result


def _check_disk_space() -> dict:
    info("启动检查: 磁盘空间...")
    result = {"check": "disk_space", "level": "ok", "message": ""}
    try:
        tmp = os.environ.get("TEMP", "C:\\")
        usage = shutil.disk_usage(tmp)
        free_gb = usage.free / (1024 ** 3)
        info(f"磁盘剩余 (TEMP): {free_gb:.1f} GB")
        if free_gb < 1.0:
            result["level"] = "error"
            result["message"] = f"磁盘空间严重不足（仅剩 {free_gb:.1f} GB）"
            result["detail"] = (
                f"系统盘剩余空间: {free_gb:.1f} GB\n"
                "安装 Node.js + Git + Claude Code 需要至少 2GB 空间。\n"
                "请清理磁盘后再使用本工具。\n\n"
                "快速清理方法:\n"
                "1. 清空回收站\n"
                "2. 打开文件管理器 → 地址栏输入 %TEMP% → 全选删除\n"
                "3. 打开设置 → 系统 → 存储 → 删除临时文件"
            )
        elif free_gb < 2.0:
            result["level"] = "warning"
            result["message"] = f"磁盘空间偏少（{free_gb:.1f} GB），建议清理"
            result["detail"] = f"剩余 {free_gb:.1f} GB，安装过程可能空间不足。建议清理后使用。"
        else:
            result["message"] = f"可用 {free_gb:.0f} GB"
        return result
    except Exception as e:
        warning(f"磁盘检测失败: {e}")
        result["message"] = "无法检测磁盘空间"
        return result


def _check_temp_dir() -> dict:
    info("启动检查: TEMP 目录...")
    result = {"check": "temp_dir", "level": "ok", "message": ""}
    try:
        tmp = tempfile.gettempdir()
        if not os.path.isdir(tmp):
            result["level"] = "error"
            result["message"] = f"临时目录不存在: {tmp}"
            result["detail"] = (
                "系统临时文件目录异常。\n"
                "请尝试：右键此电脑 → 属性 → 高级系统设置 → 环境变量\n"
                "确认 TEMP 和 TMP 变量指向了有效的目录。"
            )
            return result
        # 测试可写
        test = os.path.join(tmp, "1shot-cc-health-check.tmp")
        try:
            with open(test, "w") as f:
                f.write("ok")
            os.remove(test)
        except (IOError, OSError):
            result["level"] = "error"
            result["message"] = f"临时目录无法写入: {tmp}"
            result["detail"] = (
                "程序无法在临时目录创建文件，安装过程将无法下载安装包。\n"
                "请检查 TEMP 目录权限或磁盘是否已满。"
            )
            return result
        result["message"] = f"TEMP 正常 ({tmp})"
        return result
    except Exception as e:
        warning(f"TEMP 检测失败: {e}")
        result["message"] = "无法检测 TEMP 目录"
        return result


def _check_admin() -> dict:
    info("启动检查: 管理员权限...")
    result = {"check": "admin", "level": "ok", "message": ""}
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin:
            result["message"] = "已获取管理员权限"
        else:
            result["level"] = "warning"
            result["message"] = "未以管理员身份运行（安装系统软件可能失败）"
            result["detail"] = (
                "要安装 Node.js、Git 等系统级软件, 建议以管理员身份运行。\n\n"
                "操作步骤: 关闭程序, 右键 1shot-CC.exe, 选择 '以管理员身份运行'\n\n"
                "如果不需要安装这些系统软件, 可以忽略此提示继续使用。"
            )
        return result
    except Exception as e:
        warning(f"管理员检测失败: {e}")
        result["message"] = "无法检测管理员权限"
        return result


def _check_vcredist() -> dict:
    info("启动检查: VC++ Redistributable...")
    result = {"check": "vcredist", "level": "ok", "message": ""}
    vc_keys = [
        r"HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
        r"HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
    ]
    import subprocess
    found = False
    for key in vc_keys:
        try:
            proc = subprocess.run(
                ["reg", "query", key, "/v", "Version", "/reg:64"],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode == 0:
                found = True
                info(f"VC++ Redist 已安装: {key}")
                break
        except Exception:
            pass
    if found:
        result["message"] = "VC++ 运行时已安装"
    else:
        result["level"] = "warning"
        result["message"] = "未检测到 VC++ 运行时（可能影响 Node.js 运行）"
        result["detail"] = (
            "部分软件需要 Visual C++ Redistributable 才能运行。\n"
            "下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe\n"
            "下载后双击安装即可。"
        )
    return result


def _check_chinese_path() -> dict:
    info("启动检查: 中文路径...")
    result = {"check": "chinese_path", "level": "ok", "message": ""}
    from app.utils.path_helper import check_appdata_path
    path_result = check_appdata_path()
    issues = path_result.get("issues", [])
    if issues:
        paths = [f"{i['var']}: {i['path']}" for i in issues]
        result["level"] = "warning"
        result["message"] = f"用户路径含中文字符: {', '.join(p for p in paths)}"
        result["detail"] = (
            "你的 Windows 用户名含中文，可能导致部分命令行工具运行异常。\n"
            "建议创建一个英文用户名的 Windows 账户来使用开发工具。\n\n"
            "如果当前能正常使用，可以忽略此警告。"
        )
    else:
        result["message"] = "路径正常（无中文）"
    return result
