# 1shot-CC 开发记录

## v4.0.10 — 2026-05-15 · UI 对齐修复

### 修复
- callout 卡片居中修复：CSS 级联冲突（`.callout` shorthand margin 覆盖 `max-w-*` 的 auto-centering）
- 检测页文案修正："需要调整" → "按需调整"
- API 配置页 callout 宽度与 provider 六宫格统一


## v4.0.9 — 2026-05-15 · 两处对齐

### 修复
- 检测页 callout info 添加 `max-w-560` 居中
- API 配置页 success callout 添加 `max-w-560` 对齐


## v4.0.8 — 2026-05-15 · 宽度统一 + API 网格 + .lnk 修复

### 修复
- 全局宽度统一：`max-w-560` 同时约束左右 margin（`margin-left: auto; margin-right: auto`）
- CC-Switch `.lnk` 快捷方式改用 `os.startfile()` 启动
- API 配置页 provider 网格改为 3 列（`repeat(3, 1fr)`）
- custom 厂商默认模型设为 DeepSeek 系列

### 改进
- 全部 wizard 页面 callout/summary-box/cards-container 统一 `max-w-560` 居中


## v4.0.7 — 2026-05-15 · 检测状态修复 + CC Switch 启动

### 修复
- CC-Switch 检测改用开始菜单扫描（多名称匹配）
- CC-Switch 未安装状态降级为 ⚠️ 橙色警告
- 卸载检测与主检测引擎同步

### 改进
- wizard_check.html 结构重组：wizard-nav → summary-box → callout → loading → results


## v4.0.6 — 2026-05-15 · CC Switch 启动 + 指南按钮

### 新增
- 完成页新增「📖 使用指南」按钮

### 修复
- CC-Switch 启动逻辑修复（开始菜单 .lnk + `os.startfile`）


## v4.0.5 — 2026-05-15 · 错误温和化 + 多名称检测

### 修复
- 所有错误提示从 ❌ 红色改为 ⚠️ 橙色警告
- CC-Switch 开始菜单多名称检测（cc-switch / cc switch / ccswitch）


## v4.0.0 ~ v4.0.4 — 2026-05-14~15 · 9 步向导重构

### 新增
- 9 步渐进式安装向导：检测 → Node.js → Git → Claude → API → Switch → 美化 → 收尾 → 完成
- 收尾检查页（wizard_summary.html）
- 终端美化页（wizard_terminal.html）
- CC-Switch 安装引导页（wizard_ccswitch.html）
- 页面生命周期管理（page-open / page-closed / heartbeat）
- SSE 实时安装进度推送
- 检测结果 sessionStorage 缓存（5 分钟 TTL）

### 修复
- 6 个 wizard 页面导航链路全部修正
- 卡片样式统一：`border-left` 替代 `::before`
- 导航栏按钮风格全局统一

### 改进
- 开始菜单扫描替代纯注册表检测
- 卸载引擎与检测引擎同步


## v3.4 — 2026-05-15 · 图文教程 + Color-cc 修复 + 退出自动关标签

### 新增
- 完成页新增「操作步骤图解」卡片（3 张截图），图文并茂引导小白用户
- 退出程序后自动关闭浏览器标签页

### 修复
- Color-cc 回归官方 `irm | iex` 一键安装命令，删除冗余 Python 端逻辑
- 导航栏按钮风格完全统一（CSS class 替代行内样式）
- API 警告卡片宽度对齐
- 欢迎页跳转调整为 5 秒
- 操作步骤图解截图更新


## v3.3 — 2026-05-15 · Color-cc 主题下载修复

### 修复
- Color-cc 关键修复：Python 端直接从 Gitee 下载主题文件，绕过 install.ps1 网络假阳性
- 退出程序后 2 秒自动关闭标签页

### 改进
- 欢迎页跳转 6s → 5s
- 导航栏按钮风格完全统一
- Color-cc 双按钮统一 + 安装耗时提示


## v3.2 — 2026-05-15 · 检测强化 + 卸载缓存

### 修复
- Git / Node.js / CC-Switch / Claude 检测器全部新增注册表回退
- 卸载前强制实时检测（清除前后端缓存）
- CC-Switch 替换有效国内加速代理 URL

### 改进
- 导航栏欢迎页按钮样式统一
- Color-cc 新增 Gitee 镜像下载源
- 下载器连接超时 30s → 12s


## v3.1 — 2026-05-15 · 卸载缓存 + CC-Switch 国内代理

### 修复
- 卸载完成后自动清除前后端检测缓存
- CC-Switch 回退 URL 替换为国内 GitHub 加速代理
- 安装成功后自动刷新检测缓存


## v3.0 — 2026-05-15 · 全面升级

### 新增
- 欢迎页优化（独立 HTTP Server + 鼠标视差动效 + 6 秒展示）
- 统一检测缓存系统（前后端双重缓存，60s TTL）
- CC-Switch 三层下载回退、Node.js/Git 双镜像回退
- 全部组件版本检测覆盖（npm / claude_code / ccswitch）
- 导航栏新增欢迎页按钮

### 修复
- 页面追踪心跳失效 bug
- 自定义 provider base_url 传递
- config 写入整数字段
- 预检功能内置安装流程


## v2.2 — 2026-05-01 · 关键修复 + 开源准备

### 修复
- Color-cc: 重写安装器，改用官方 `install.ps1` 替代错误的 git clone + schemes 逻辑；安装前自动创建 `settings.json`；非零退出码正确报告失败；新增安装后验证
- Windows Terminal: winget 安装后等 3 秒重新验证，失败恢复按钮，避免误导用户
- CC-Switch: 新增 Tauri 注册表键查询（`HKCU\Software\farion1231\CC-Switch`）+ `DisplayIcon` 解析 + 文件系统三层 fallback；安装后自动清检测缓存
- 启动: `launcher.py` 新增 `_find_wt_exe()` 检测，优先使用 Windows Terminal，不可用时回退 PowerShell

### 改进
- API 配置页新增可折叠「高级模型选择」区域，显示默认推荐并可自定义覆盖
- DeepSeek 模型名更新为 `deepseek-v4-pro[1m]` / `deepseek-v4-flash[1m]`
- CC-Switch `registry_reader` 与 `launcher` 消除重复代码
- 新增中英文 README、软件截图

---

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
