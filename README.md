<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Release-v4.0.14-eb5e28.svg" alt="Release">
</p>

<h1 align="center">🚀 1shot-CC</h1>
<p align="center"><strong>Claude Code，装得明明白白</strong></p>
<p align="center">不用懂命令行 · 不用查教程 · 跟着点几下就好 ✨</p>

---

## 💡 这是什么

**1shot-CC** 是一个 Windows 桌面向导，帮零命令行经验的你用鼠标点几下，就能把 Claude Code 完整环境搭好。

第一次看到"终端"、"npm"、"环境变量"这些词就头疼？没关系～ 1shot-CC 把所有复杂步骤变成了一个接一个的友好按钮。点点鼠标，十分钟搞定 🎯

| 你只需要 | 1shot-CC 帮你做 |
|---------|---------------|
| 🖱️ 点一下 | 自动检查电脑缺什么 |
| 🖱️ 再点一下 | 从国内镜像装好 Node.js、Git |
| 🖱️ 再点一下 | 一键安装 Claude Code |
| 🔑 填上 Key | 自动配置 AI 服务（支持 5 家国内厂商）|
| 🚀 点开始 | 打开终端，开始你的第一次 AI 编程 |

---

## 📸 软件截图

### 🌟 欢迎页
<p align="center"><img src="assets/1-欢迎页.png" width="80%"></p>

### 🏠 首页
<p align="center"><img src="assets/2-介绍页.png" width="80%"></p>

### 🔍 环境检测
<p align="center"><img src="assets/3-检测页.png" width="80%"></p>

### 📥 一键安装 Node.js / Git / Claude Code
<p align="center"><img src="assets/4-安装页.png" width="80%"></p>

### ⚙️ API 配置 · 5 家国内厂商随心选
<p align="center"><img src="assets/5-api配置页.png" width="80%"></p>

### 🔀 CC-Switch + 🎨 终端美化
<p align="center"><img src="assets/6-完成页.png" width="80%"></p>

### 🎉 完成撒花
<p align="center"><img src="assets/6-完成页.png" width="80%"></p>

### 📖 内置图文教程
<p align="center">
  <img src="assets/7-教程1.png" width="24%">
  <img src="assets/7-教程2.png" width="24%">
  <img src="assets/7-教程3.png" width="24%">
  <img src="assets/7-教程4.png" width="24%">
</p>

### 🗑️ 一键卸载
<p align="center"><img src="assets/8-卸载页.png" width="80%"></p>

---

## ✨ 它都能做什么

- 🧭 **9 步向导** — 检测 → Node.js → Git → Claude → API → Switch → 美化 → 收尾 → 完成，一条龙
- 🔍 **智能环境检测** — 13 项全方位扫描，注册表 + 开始菜单 + 文件系统三重回退
- 📥 **多源下载回退** — 国内 CDN 代理加速，自动切换可用源，不用操心网络问题
- 🤖 **Claude Code 一键安装** — 自动配好执行策略、国内镜像，跳过繁琐引导
- 🔀 **CC-Switch 桌面版** — 任务栏小图标，多家 AI 服务一键切换
- ⚙️ **5 家国内 AI 厂商** — DeepSeek · 智谱 GLM · MiniMax · 小米 MiMo · 通义千问，也支持自己填地址
- 🎨 **Color-cc 终端美化** — Oh My Posh 主题，让终端也赏心悦目
- 📖 **图文教程** — 4 篇保姆级教程，每步都有截图
- 🗑️ **一键卸载** — 装错了？一键全部卸干净，配置自动备份
- 🖥️ **Windows Terminal 检测** — 自动检测，支持一键安装微软官方终端
- 🎯 **版本更新提醒** — 所有组件版本自动比对，一键升级
- 🎉 **完成撒花** — 加上操作步骤图解，小白也能看懂

---

## 🏁 快速开始

### 👋 给使用者

1. 从 [Releases](../../releases) 下载 `1shot-CC.exe`
2. **右键 → 以管理员身份运行**（装软件需要权限）
3. 浏览器会自动打开欢迎页，几秒后进入主页
4. 跟着提示一步步来就好，超简单～

> 💡 所有操作都在你自己的电脑上完成，**不会上传任何数据**，放心用。

### 🛠️ 给开发者

```bash
git clone https://github.com/JananZZZ/1shot-cc.git
cd 1shot-cc
pip install flask
python main.py

# 打包为 exe
pip install pyinstaller
python -m PyInstaller build.spec --clean --noconfirm
```

---

## 📂 项目结构

```
1shot-cc/
├── main.py                      # 入口：欢迎页 + Flask 应用
├── app/
│   ├── config.py                # 配置常量
│   ├── routes/                  # API 路由层
│   │   ├── api_system.py        #   系统检测 + 页面生命周期
│   │   ├── api_install.py       #   安装操作 + SSE 进度推送
│   │   ├── api_config.py        #   配置管理
│   │   └── api_tutorial.py      #   教程接口
│   ├── services/                # 业务逻辑层
│   │   ├── detector.py          #   统一检测引擎
│   │   ├── error_resolver.py    #   错误诊断知识库
│   │   ├── uninstaller.py       #   卸载引擎
│   │   ├── node_installer.py    #   Node.js 安装（双镜像）
│   │   ├── git_installer.py     #   Git 安装（双镜像）
│   │   ├── claude_installer.py  #   Claude Code 安装
│   │   ├── ccswitch_installer.py#   CC-Switch 安装（智能回退）
│   │   ├── colorcc_installer.py #   Color-cc 终端美化
│   │   ├── config_writer.py     #   配置文件读写
│   │   └── launcher.py          #   终端/应用启动器
│   ├── utils/                   # 工具函数
│   │   ├── downloader.py        #   文件下载（快速失效策略）
│   │   ├── registry_reader.py   #   Windows 注册表读取
│   │   └── ...
│   └── templates/               # Jinja2 前端模板
├── static/                      # 静态资源（CSS + JS）
├── tutorials/                   # 教程 Markdown 源文件
├── assets/                      # 软件截图
├── build.spec                   # PyInstaller 打包配置
└── requirements.txt             # Python 依赖
```

---

## 🔧 技术栈

| 层 | 技术 |
|---|------|
| Web 框架 | Flask 3.x + Jinja2 |
| 前端 | Vanilla JS + CSS Custom Properties（暖白主题 ☀️）|
| 实时推送 | Server-Sent Events (SSE) |
| 打包 | PyInstaller（单文件 exe，约 46MB）|
| 平台 | Windows 10 / 11 |
| 欢迎页 | 独立 HTTP Server + 鼠标视差动效 ✨ |

---

## 🤝 贡献

欢迎提 Issue 和 Pull Request ❤️

- 代码风格：保持简单，函数 < 50 行，文件 < 800 行
- 错误消息：中文提示，面向小白用户
- 提交信息：使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/) 格式

---

## 📄 许可证

MIT © [1shot-CC Contributors](../../graphs/contributors)

---

## ☕ 请作者喝杯咖啡

如果这个项目帮到了你，欢迎请作者喝杯咖啡～ **0.88 元即可！** 一分也是爱 😭💕

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <b>💚 微信</b><br><br>
        <img src="assets/wechat-donate.png" width="220"><br>
        <sub>微信扫码 → 0.88</sub>
      </td>
      <td align="center" width="50%">
        <b>💙 支付宝</b><br><br>
        <img src="assets/alipay-donate.jpg" width="220"><br>
        <sub>支付宝扫码 → 0.88</sub>
      </td>
    </tr>
  </table>
</div>

> 💭 完全自愿，无任何功能限制。好用的话给个 Star ⭐ 就很开心啦～

---

<p align="center">Made with ❤️ for everyone who wants to start coding with AI</p>
