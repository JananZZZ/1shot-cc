# 1shot-CC 开发记录

## v2.1 — 2026-04-30 · Light主题重构

### 新功能
- Light 暖白主题 (Warm Editorial): 赤陶土+橄榄绿配色, Noto Serif SC 衬线标题
- CC-Switch 安装后配置引导页 (wizard_ccswitch_guide.html), 3步图解+自动启动
- Windows Terminal 环境检测 (第9项), winget 一键静默安装
- 导航栏教程下拉改用 JS click toggle (修复选择困难)

### 修复
- CC-Switch 下载备用链接: GitHub releases HTML → MSI 直链
- 自定义 API 提供商后端支持 (custom base_url)
- Color-cc 安装前检测 Windows Terminal

### 已知问题
- winget 在某些 Windows 10 版本可能不存在, 需从 Microsoft Store 安装 App Installer
- CC-Switch 启动依赖注册表扫描, 如果安装路径非常规可能找不到
- PowerShell 启动脚本的编码在非 UTF-8 系统上可能出现乱码

---

## v2.0 — 2026-04-30 · 深色主题重构

### 新功能
- Soft Tech 深色主题: 毛玻璃导航栏, 氛围光背景, 粒子动画
- 一键启动 PowerShell + Claude Code (launch_powershell/launch_claude)
- 一键安装 Color-cc 终端美化
- 一键启动 CC-Switch (launch_ccswitch)
- 首页粒子背景 + 完成页撒花庆祝

### 修复
- PowerShell 启动窗口不显示 (CREATE_NO_WINDOW → CREATE_NEW_CONSOLE)
- 文案全面亲民化

---

## v1.0 — 2026-04-30 · 初始版本

### 核心功能
- 系统环境检测 (Node.js/Git/PowerShell/npm/Claude/CC-Switch)
- 一键安装 Node.js LTS / Git / Claude Code / CC-Switch
- SSE 实时进度推送
- 5 家 API 供应商配置预设
- 4 篇 HTML 图文教程
