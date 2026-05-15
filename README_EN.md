<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Release-v3.4-eb5e28.svg" alt="Release">
</p>

<h1 align="center">🚀 1shot-CC</h1>
<p align="center"><strong>Claude Code, made effortless</strong></p>
<p align="center">No command lines · No tutorials · Just a few clicks</p>

---

## 💡 What Is This

**1shot-CC** is a Windows desktop wizard that helps users with zero command-line experience set up a complete Claude Code development environment in one go.

New to AI coding? Overwhelmed by "terminal", "npm", "environment variables"? Don't worry — 1shot-CC turns all those complicated steps into friendly buttons. Click, click, done.

| You Just | 1shot-CC Handles |
|----------|-----------------|
| Click | Automatically checks what's missing |
| Click again | Downloads & installs Node.js & Git from CDN mirrors |
| Click again | Installs Claude Code globally |
| Paste your Key | Configures your AI provider (5 Chinese providers) |
| Click start | Opens terminal, begin your first coding session |

---

## 📸 Screenshots

### 1. Welcome Page
<p align="center"><img src="assets/1-欢迎页.png" width="80%"></p>

### 2. Home
<p align="center"><img src="assets/2-介绍页.png" width="80%"></p>

### 3. System Check
<p align="center"><img src="assets/3-检测页.png" width="80%"></p>

### 4. One-Click Install (Node.js / Git / Claude Code)
<p align="center"><img src="assets/4-安装页.png" width="80%"></p>

### 5. API Configuration (5 Chinese providers)
<p align="center"><img src="assets/5-api配置页.png" width="80%"></p>

### 6. Finish Page
<p align="center"><img src="assets/6-完成页.png" width="80%"></p>

### 7. Built-in Tutorials
<p align="center">
  <img src="assets/7-教程1.png" width="24%">
  <img src="assets/7-教程2.png" width="24%">
  <img src="assets/7-教程3.png" width="24%">
  <img src="assets/7-教程4.png" width="24%">
</p>

### 8. One-Click Uninstall
<p align="center"><img src="assets/8-卸载页.png" width="80%"></p>

---

## ✨ Features

- 🔍 **Smart Environment Check** — 13-item full scan with CLI + registry dual fallback
- 📥 **Multi-Layer Download Fallback** — CC-Switch 3-layer fallback, Node.js/Git dual mirrors
- 🤖 **One-Click Claude Code** — Auto-configures execution policy, mirror registry, onboarding
- 🔀 **CC-Switch Integration** — Desktop or CLI version with pre/post-install checks
- ⚙️ **5 AI Providers Built-in** — DeepSeek · Zhipu GLM · MiniMax · Xiaomi MiMo · Tongyi Qwen
- 🎨 **Color-cc Terminal Theme** — Official `irm | iex` one-liner with GitHub→Gitee auto-fallback
- 📖 **Illustrated Tutorials** — 4 complete guides with screenshots
- 🗑️ **One-Click Uninstall** — Pre-uninstall detection, config backup, clean removal
- 🎯 **Version Outdated Detection** — All components with upgrade support
- 🎉 **Finish Page** — Confetti celebration + visual step-by-step guide

---

## 🏁 Quick Start

### For Users

1. Download `1shot-CC.exe` from [Releases](../../releases)
2. **Right-click → Run as Administrator**
3. Browser opens welcome page, auto-redirects to main app
4. Follow the prompts — that's it!

> **Note**: Everything runs locally. No data is ever uploaded.

### For Developers

```bash
git clone https://github.com/JananZZZ/1shot-cc.git
cd 1shot-cc
pip install flask
python main.py

# Build exe
pip install pyinstaller
python -m PyInstaller build.spec --clean --noconfirm
```

---

## 📂 Project Structure

```
1shot-cc/
├── main.py                      # Entry: welcome page + Flask + watchdog
├── app/
│   ├── config.py                # Constants
│   ├── routes/                  # API route layer
│   │   ├── api_system.py        #   System check + page lifecycle
│   │   ├── api_install.py       #   Install + SSE + uninstall
│   │   ├── api_config.py        #   Config management
│   │   └── api_tutorial.py      #   Tutorial endpoints
│   ├── services/                # Business logic
│   │   ├── detector.py          #   Unified detection engine (13 items)
│   │   ├── error_resolver.py    #   Error diagnostic KB
│   │   ├── uninstaller.py       #   Uninstall engine
│   │   ├── node_installer.py    #   Node.js install (dual mirrors)
│   │   ├── git_installer.py     #   Git install (dual mirrors)
│   │   ├── claude_installer.py  #   Claude Code npm install
│   │   ├── ccswitch_installer.py#   CC-Switch install (3-layer fallback)
│   │   ├── colorcc_installer.py #   Color-cc terminal theme
│   │   ├── config_writer.py     #   settings.json read/write
│   │   └── launcher.py          #   Terminal/app launcher
│   ├── utils/                   # Utilities
│   │   ├── downloader.py        #   File download (progress+retry+SHA256)
│   │   ├── elevation.py         #   Admin privilege detection
│   │   ├── logger.py            #   Diagnostic logging
│   │   └── subprocess_runner.py #   Subprocess management
│   └── templates/               # Jinja2 frontend templates
├── static/                      # Static assets (CSS + JS + images)
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
| Frontend | Vanilla JS + CSS Custom Properties (warm light theme) |
| Real-time | Server-Sent Events (SSE) |
| Packaging | PyInstaller (single exe, ~47MB) |
| Platform | Windows 10/11 |
| Welcome Page | Standalone HTTP Server + parallax effects |

---

## 🤝 Contributing

Issues and pull requests are welcome! [Open an Issue](../../issues/new)

- Keep it simple — functions < 50 lines, files < 800 lines
- User-facing errors in Chinese

---

## 📄 License

MIT © [1shot-CC Contributors](../../graphs/contributors)

---

## ☕ Buy Me a Coffee

If this project helped you, consider buying the author a coffee. **Just ¥0.88!**

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

> 💭 Completely voluntary. A ⭐ Star means just as much!

---

<p align="center">Made with ❤️ for everyone who wants to start coding with AI</p>
