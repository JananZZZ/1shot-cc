<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Release-v4.0.14-eb5e28.svg" alt="Release">
</p>

<h1 align="center">🚀 1shot-CC</h1>
<p align="center"><strong>Claude Code, made effortless</strong></p>
<p align="center">No command lines · No tutorials · Just a few clicks ✨</p>

---

## 💡 What Is This

**1shot-CC** is a Windows desktop wizard that helps absolute beginners set up a complete Claude Code development environment — all with just a few mouse clicks.

New to AI coding? Overwhelmed by words like "terminal", "npm", and "environment variables"? Don't worry! 1shot-CC turns every complicated step into a friendly button. Click, click, done 🎯

| You Just | 1shot-CC Handles |
|----------|-----------------|
| 🖱️ Click | Automatically checks what's missing |
| 🖱️ Click again | Installs Node.js & Git from CDN mirrors |
| 🖱️ Click again | Installs Claude Code globally |
| 🔑 Paste your Key | Sets up AI provider (5 Chinese providers built-in) |
| 🚀 Click start | Opens terminal — time for your first AI coding session |

---

## 📸 Screenshots

### 🌟 Welcome
<p align="center"><img src="assets/1-欢迎页.png" width="80%"></p>

### 🏠 Home
<p align="center"><img src="assets/2-介绍页.png" width="80%"></p>

### 🔍 System Check
<p align="center"><img src="assets/3-检测页.png" width="80%"></p>

### 📥 One-Click Install — Node.js / Git / Claude Code
<p align="center"><img src="assets/4-安装页.png" width="80%"></p>

### ⚙️ API Config · 5 AI Providers
<p align="center"><img src="assets/5-api配置页.png" width="80%"></p>

### 🎉 Finish & Celebrate
<p align="center"><img src="assets/6-完成页.png" width="80%"></p>

### 📖 Built-in Tutorials
<p align="center">
  <img src="assets/7-教程1.png" width="24%">
  <img src="assets/7-教程2.png" width="24%">
  <img src="assets/7-教程3.png" width="24%">
  <img src="assets/7-教程4.png" width="24%">
</p>

### 🗑️ One-Click Uninstall
<p align="center"><img src="assets/8-卸载页.png" width="80%"></p>

---

## ✨ Features

- 🧭 **9-Step Wizard** — Check → Node.js → Git → Claude → API → Switch → Terminal → Summary → Done
- 🔍 **Smart Detection** — 13 items scanned with registry + Start Menu + filesystem triple fallback
- 📥 **Multi-Source Downloads** — CDN proxy acceleration with automatic failover, no network headaches
- 🤖 **One-Click Claude Code** — Auto-configures execution policy, registry mirror, and skips onboarding
- 🔀 **CC-Switch Desktop** — System tray icon for instant AI provider switching
- ⚙️ **5 AI Providers Built-in** — DeepSeek · Zhipu GLM · MiniMax · Xiaomi MiMo · Tongyi Qwen，plus custom endpoint
- 🎨 **Color-cc Terminal Theme** — Oh My Posh theme that makes your terminal beautiful
- 📖 **Illustrated Guides** — 4 step-by-step tutorials with screenshots
- 🗑️ **One-Click Uninstall** — Clean removal with automatic config backup
- 🖥️ **Windows Terminal** — Auto-detection with one-click Microsoft Store install
- 🎯 **Version Checks** — Automatic version comparison for all components
- 🎉 **Celebration Page** — Confetti + visual walkthrough for absolute beginners

---

## 🏁 Quick Start

### 👋 For Users

1. Download `1shot-CC.exe` from [Releases](../../releases)
2. **Right-click → Run as Administrator** (needed for installing software)
3. Your browser opens a welcome page, then auto-redirects to the main app
4. Follow the prompts — it's that easy!

> 💡 Everything runs locally on your own computer. **No data is ever uploaded.** Your privacy is safe.

### 🛠️ For Developers

```bash
git clone https://github.com/JananZZZ/1shot-cc.git
cd 1shot-cc
pip install flask
python main.py

# Build standalone exe
pip install pyinstaller
python -m PyInstaller build.spec --clean --noconfirm
```

---

## 📂 Project Structure

```
1shot-cc/
├── main.py                      # Entry: welcome page + Flask app
├── app/
│   ├── config.py                # Constants
│   ├── routes/                  # API route layer
│   │   ├── api_system.py        #   System check + page lifecycle
│   │   ├── api_install.py       #   Install ops + SSE progress
│   │   ├── api_config.py        #   Config management
│   │   └── api_tutorial.py      #   Tutorial endpoints
│   ├── services/                # Business logic
│   │   ├── detector.py          #   Unified detection engine
│   │   ├── error_resolver.py    #   Error diagnostic KB
│   │   ├── uninstaller.py       #   Uninstall engine
│   │   ├── node_installer.py    #   Node.js installer (dual mirrors)
│   │   ├── git_installer.py     #   Git installer (dual mirrors)
│   │   ├── claude_installer.py  #   Claude Code installer
│   │   ├── ccswitch_installer.py#   CC-Switch installer (smart fallback)
│   │   ├── colorcc_installer.py #   Color-cc terminal theme
│   │   ├── config_writer.py     #   Settings file read/write
│   │   └── launcher.py          #   Terminal/app launcher
│   ├── utils/                   # Utilities
│   │   ├── downloader.py        #   File download (fast-fail strategy)
│   │   ├── registry_reader.py   #   Windows registry reader
│   │   └── ...
│   └── templates/               # Jinja2 frontend templates
├── static/                      # Static assets (CSS + JS)
├── tutorials/                   # Tutorial markdown sources
├── assets/                      # Screenshots
├── build.spec                   # PyInstaller config
└── requirements.txt             # Python dependencies
```

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | Flask 3.x + Jinja2 |
| Frontend | Vanilla JS + CSS Custom Properties (warm light theme ☀️) |
| Real-time | Server-Sent Events (SSE) |
| Packaging | PyInstaller (single exe, ~46MB) |
| Platform | Windows 10 / 11 |
| Welcome Page | Standalone HTTP Server + parallax effects ✨ |

---

## 🤝 Contributing

Issues and Pull Requests welcome! ❤️

- Keep it simple — functions < 50 lines, files < 800 lines
- User-facing messages in Chinese (Chinese user base)
- Use [Conventional Commits](https://www.conventionalcommits.org/) format

---

## 📄 License

MIT © [1shot-CC Contributors](../../graphs/contributors)

---

## ☕ Buy Me a Coffee

If 1shot-CC helped you out, consider buying the author a coffee — **just ¥0.88!** Every bit of support means the world 😭💕

<div align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <b>💚 WeChat</b><br><br>
        <img src="assets/wechat-donate.png" width="220"><br>
        <sub>Scan with WeChat → ¥0.88</sub>
      </td>
      <td align="center" width="50%">
        <b>💙 Alipay</b><br><br>
        <img src="assets/alipay-donate.jpg" width="220"><br>
        <sub>Scan with Alipay → ¥0.88</sub>
      </td>
    </tr>
  </table>
</div>

> 💭 Completely voluntary — no features are locked. A ⭐ Star means just as much!

---

<p align="center">Made with ❤️ for everyone who wants to start coding with AI</p>
