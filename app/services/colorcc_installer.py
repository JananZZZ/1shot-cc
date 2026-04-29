"""Color-cc 终端美化安装器
Color-cc 是 JananZZZ 的 Windows Terminal 美化项目
仓库: https://github.com/JananZZZ/Color-cc
"""
import os
import subprocess
import tempfile


def check_windows_terminal() -> dict:
    """检测 Windows Terminal 是否已安装"""
    wt_paths = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "wt.exe"),
        r"C:\Program Files\WindowsApps\Microsoft.WindowsTerminal_8wekyb3d8bbwe\wt.exe",
    ]
    # 也尝试直接运行
    try:
        r = subprocess.run(["where", "wt"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and r.stdout.strip():
            return {"installed": True, "path": r.stdout.strip().split("\n")[0]}
    except Exception:
        pass

    for p in wt_paths:
        if os.path.exists(p):
            return {"installed": True, "path": p}

    return {"installed": False, "path": ""}


def install_colorcc(callback=None) -> dict:
    """安装 Color-cc
    1. git clone 到临时目录
    2. 用户手动复制配置文件，或自动拷贝到 Windows Terminal 配置目录
    """
    wt_check = check_windows_terminal()
    if not wt_check["installed"]:
        if callback:
            callback(0, "未检测到 Windows Terminal，请先从 Microsoft Store 安装")
        return {"success": False, "error": "未检测到 Windows Terminal。请先在 Microsoft Store 搜索并安装 Windows Terminal。"}

    tmpdir = tempfile.gettempdir()
    colorcc_dir = os.path.join(tmpdir, "Color-cc")

    # 如果已存在，先删除
    if os.path.exists(colorcc_dir):
        if callback:
            callback(5, "清理旧的 Color-cc 目录...")
        try:
            subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", colorcc_dir], capture_output=True, timeout=30)
        except Exception:
            import shutil
            shutil.rmtree(colorcc_dir, ignore_errors=True)

    if callback:
        callback(10, "正在从 GitHub 下载 Color-cc...")

    # 克隆仓库
    clone_result = subprocess.run(
        ["git", "clone", "--depth", "1", "https://github.com/JananZZZ/Color-cc.git", colorcc_dir],
        capture_output=True, text=True, timeout=120,
        encoding="utf-8", errors="replace",
    )

    if clone_result.returncode != 0:
        # 尝试 Gitee 镜像
        if callback:
            callback(10, "GitHub 连接失败，尝试国内镜像...")
        clone_result = subprocess.run(
            ["git", "clone", "--depth", "1", "https://gitee.com/JananZZZ/Color-cc.git", colorcc_dir],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )

    if clone_result.returncode != 0:
        error_msg = clone_result.stderr[:300] if clone_result.stderr else "Git clone 失败"
        if callback:
            callback(0, f"下载失败: {error_msg}")
        return {"success": False, "error": error_msg}

    if callback:
        callback(40, "正在查找配置文件...")

    # 查找 Windows Terminal settings.json
    wt_settings_dir = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Packages",
    )
    settings_path = None

    # 扫描 Packages 目录找到 Windows Terminal 的 settings.json
    try:
        for root, dirs, files in os.walk(wt_settings_dir):
            if "Microsoft.WindowsTerminal" in root and "LocalState" in root:
                candidate = os.path.join(root, "settings.json")
                if os.path.exists(candidate):
                    settings_path = candidate
                    break
            if len(root) > 300:
                dirs.clear()
    except Exception:
        pass

    if not settings_path:
        # 提供手动指导
        if callback:
            callback(80, "未找到 Windows Terminal 配置文件，请手动配置")
        return {
            "success": True,
            "partial": True,
            "message": (
                "Color-cc 已下载到: " + colorcc_dir + "\n"
                "请手动操作：\n"
                "1. 打开 Windows Terminal\n"
                "2. 按 Ctrl+, 打开设置\n"
                "3. 点击左下角「打开 JSON 文件」\n"
                "4. 参考 Color-cc 目录中的 schemes 文件夹进行配置"
            ),
            "colorcc_dir": colorcc_dir,
        }

    if callback:
        callback(70, "正在备份原配置...")

    # 备份原配置
    import shutil
    bak_path = settings_path + ".1shotcc.bak"
    try:
        shutil.copy2(settings_path, bak_path)
    except Exception:
        if callback:
            callback(0, "备份原配置失败，请检查文件权限")
        return {"success": False, "error": "备份原配置失败，请检查文件权限"}

    if callback:
        callback(85, "正在应用 Color-cc 配色方案...")

    # 查找 Color-cc 的配色 JSON
    import json
    schemes = []
    schemes_dir = os.path.join(colorcc_dir, "schemes")
    if not os.path.isdir(schemes_dir):
        # 可能直接是 JSON 文件
        for f in os.listdir(colorcc_dir):
            fp = os.path.join(colorcc_dir, f)
            if f.endswith(".json") and os.path.isfile(fp):
                try:
                    with open(fp, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        if isinstance(data, dict) and "schemes" in data:
                            schemes = data["schemes"]
                        elif isinstance(data, list):
                            schemes = data
                except Exception:
                    pass
    else:
        for f in os.listdir(schemes_dir):
            fp = os.path.join(schemes_dir, f)
            if f.endswith(".json") and os.path.isfile(fp):
                try:
                    with open(fp, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        if isinstance(data, list):
                            schemes.extend(data)
                        elif isinstance(data, dict) and "schemes" in data:
                            schemes.extend(data["schemes"])
                except Exception:
                    pass

    if not schemes:
        if callback:
            callback(0, "未找到 Color-cc 配色方案文件")
        return {"success": False, "error": "未找到 Color-cc 的配色方案文件，请手动配置。"}

    # 写入 settings.json
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            wt_settings = json.load(f)
    except Exception:
        wt_settings = {}

    existing_schemes = wt_settings.get("schemes", [])
    existing_names = {s.get("name", "") for s in existing_schemes}

    added = 0
    for scheme in schemes:
        if scheme.get("name", "") not in existing_names:
            existing_schemes.append(scheme)
            added += 1

    wt_settings["schemes"] = existing_schemes

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(wt_settings, f, indent=2, ensure_ascii=False)

    if callback:
        callback(100, f"Color-cc 安装完成！已添加 {added} 个配色方案。")

    return {
        "success": True,
        "message": f"Color-cc 安装完成！已添加 {added} 个新配色方案。\n请打开 Windows Terminal → 设置 → 配色方案 选择你喜欢的主题。\n原配置已备份到: {bak_path}",
        "added_schemes": added,
        "backup_path": bak_path,
    }


def launch_colorcc_guide() -> dict:
    """启动 Color-cc 的 GitHub 页面让用户手动参考"""
    import webbrowser
    try:
        webbrowser.open("https://github.com/JananZZZ/Color-cc")
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
