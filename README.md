<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Release-v2.2-eb5e28.svg" alt="Release">
</p>

<h1 align="center">🚀 1shot-CC</h1>
<p align="center"><strong>Claude Code，装得明明白白</strong></p>
<p align="center">不用懂命令行 · 不用查教程 · 跟着点几下就好</p>

---

## 💡 这是什么

**1shot-CC** 是一个 Windows 桌面向导，帮助零命令行经验的用户一键完成 Claude Code 的完整环境搭建。

第一次接触 AI 编程，看到"终端"、"npm"、"环境变量"这些词就头疼？没关系，1shot-CC 把所有的复杂步骤变成了一个接一个的按钮。点点鼠标，十分钟搞定。

| 你只需要 | 1shot-CC 帮你做 |
|---------|---------------|
| 点一下 | 自动检查电脑缺什么 |
| 再点一下 | 从国内镜像下载安装 Node.js、Git |
| 再点一下 | 装好 Claude Code |
| 填上 Key | 自动配置 AI 服务（支持 5 家国内厂商） |
| 点开始 | 打开终端，开始你的第一次 Coding |

---

## 📸 界面预览

<p align="center">
  <img src="screenshots/01-home.png" alt="首页" width="49%">
  <img src="screenshots/04-config.png" alt="配置页" width="49%">
</p>

<p align="center">
  <img src="screenshots/02-check.png" alt="检测页" width="49%">
  <img src="screenshots/05-final.png" alt="完成页" width="49%">
</p>

---

## ✨ 它都能做什么

- 🔍 **智能环境检测** — 一键扫描 Node.js、Git、PowerShell 策略、npm 镜像源、Windows Terminal 等 9 项环境
- 📥 **从国内镜像安装** — 从 npmmirror 下载 Node.js 和 Git，速度飞快，不用科学上网
- 🤖 **Claude Code 一键安装** — 自动设置执行策略、配置淘宝镜像、跳过 onboarding 引导
- 🔀 **CC-Switch 安装** — 桌面板和命令行版任选，安装后自动引导使用
- ⚙️ **5 家国内 AI 服务商** — 智谱 GLM · DeepSeek · MiniMax · 小米 MiMo · 通义千问，还支持自定义 API 地址
- 🎨 **Color-cc 终端美化** — 一键安装 Oh My Posh 状态栏主题，让终端好看又好用
- 🖥️ **Windows Terminal 检测与安装** — 自动检测并支持 winget 一键安装
- 📖 **图文教程** — Claude Code 使用、API Key 获取、CC-Switch 配置、科学上网，每一步都有图
- 🎯 **模型推荐配置** — 根据每家厂商的当前推荐自动填写 Haiku/Sonnet/Opus 模型，也支持手动覆盖
- 🎉 **撒花庆祝** — 装完有好看的完成页，点一下就在 Windows Terminal 里启动 Claude Code

---

## 🏁 快速开始

### 给使用者

1. 从 [Releases](../../releases) 下载 `1shot-CC.exe`
2. 双击运行（Windows 可能会弹出安全提示，点"更多信息 → 仍要运行"）
3. 浏览器会自动打开向导页面
4. 跟着提示点点鼠标就完事了

> **提示**：程序会打开浏览器和本地网页，所有操作都在你自己的电脑上完成，不会上传任何数据。

### 给开发者

```bash
# 克隆仓库
git clone https://github.com/farion1231/1shot-cc.git
cd 1shot-cc

# 安装依赖
pip install flask

# 启动开发服务器
python main.py

# 打包为 exe
pip install pyinstaller
python -m PyInstaller build.spec --clean --noconfirm
# 输出: dist/1shot-CC.exe
```

---

## 📂 项目结构

```
1shot-cc/
├── main.py                      # 入口：Flask 应用 + 浏览器自动打开
├── app/
│   ├── config.py                # 配置常量（版本号、下载地址、供应商信息）
│   ├── routes/                  # API 路由层
│   │   ├── api_system.py        #   系统检测接口
│   │   ├── api_install.py       #   安装操作接口 + SSE 进度推送
│   │   ├── api_config.py        #   配置管理接口
│   │   └── api_tutorial.py      #   教程接口
│   ├── services/                # 业务逻辑层
│   │   ├── system_checker.py    #   环境检测
│   │   ├── node_installer.py    #   Node.js 下载安装
│   │   ├── git_installer.py     #   Git 下载安装
│   │   ├── claude_installer.py  #   Claude Code npm 安装
│   │   ├── ccswitch_installer.py#   CC-Switch 下载安装
│   │   ├── config_writer.py     #   settings.json 读写
│   │   ├── launcher.py          #   终端/应用启动器（Windows Terminal 优先）
│   │   ├── colorcc_installer.py #   Color-cc 终端美化
│   │   └── proxy_helper.py      #   npm 镜像源工具
│   ├── utils/                   # 工具函数
│   │   ├── downloader.py        #   文件下载（进度+重试）
│   │   ├── path_helper.py       #   路径处理
│   │   ├── registry_reader.py   #   Windows 注册表读取
│   │   └── subprocess_runner.py #   子进程管理
│   └── templates/               # Jinja2 前端模板
│       ├── index.html           #   首页
│       ├── wizard_check.html    #   系统检测页
│       ├── wizard_nodejs.html   #   Node.js 安装页
│       ├── wizard_git.html      #   Git 安装页
│       ├── wizard_claude.html   #   Claude Code 安装页
│       ├── wizard_ccswitch.html #   CC-Switch 安装页
│       ├── wizard_ccswitch_guide.html  # CC-Switch 使用引导
│       ├── wizard_config.html   #   API 配置页（含模型选择）
│       ├── wizard_final.html    #   完成页（撒花庆祝）
│       └── tutorial_*.html      #   图文教程页
├── static/                      # 静态资源
│   ├── css/                     #   样式表（含深色/浅色主题）
│   └── js/                      #   前端 API 封装 + 安装向导控制
├── tutorials/                   # 教程 Markdown 源文件
├── screenshots/                 # 软件截图
├── build.spec                   # PyInstaller 打包配置
└── requirements.txt             # Python 依赖
```

---

## 🔧 技术栈

| 层 | 技术 |
|---|------|
| Web 框架 | Flask 3.x + Jinja2 |
| 前端 | Vanilla JS + CSS Custom Properties（支持深浅色主题） |
| 实时推送 | Server-Sent Events (SSE) |
| 打包 | PyInstaller（单文件 exe，约 13MB） |
| 平台 | Windows 10/11 |

---

## 🤝 贡献

欢迎提 Issue 和 Pull Request。

如果你发现什么 bug，或者有好的想法想让这个工具更顺手，请直接 [新建 Issue](../../issues/new)。

贡献前请阅读：
- 代码风格：保持简单，函数 < 50 行，文件 < 800 行
- 错误消息：使用中文，面向小白用户
- 提交信息：使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/) 格式

---

## 📄 许可证

MIT © [1shot-CC Contributors](../../graphs/contributors)

---

## ☕ 赞助

为了让零命令行经验的朋友也能轻松上手 AI 编程，这个项目用掉了不少 token 来做测试和迭代。

如果你觉得它帮到了你，可以请我喝杯咖啡 👇

<p align="center">
  <img src="screenshots/sponsor-wx.png" alt="微信赞赏" width="260">
  <img src="screenshots/sponsor-alipay.png" alt="支付宝赞赏" width="260">
</p>

<p align="center">当然，给一颗 <strong>⭐ Star</strong> 也是很大的鼓励</p>

---

<p align="center">Made with ❤️ for everyone who wants to start coding with AI</p>
