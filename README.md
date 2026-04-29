# 1shot-CC — Claude Code 一键安装向导

帮助 Windows 小白用户（零命令行经验）一键完成 Claude Code 完整环境搭建。

## 功能

- 🔍 **智能检测** — Node.js、Git、PowerShell 策略、npm 镜像源等
- ⬇️ **一键安装** — 从国内镜像下载安装 Node.js、Git、Claude Code、CC-Switch
- ⚙️ **API 配置** — 内置智谱/DeepSeek/MiniMax/MiMo/通义千问等供应商预设
- 📚 **图文教程** — Claude Code 使用、API 获取、CC-Switch、科学上网指南

## 运行

```bash
pip install flask
python main.py
```

浏览器自动打开 → 跟随向导操作即可。

## 打包为 exe

```bash
pip install pyinstaller
pyinstaller build.spec --clean --noconfirm
```

生成 `dist/1shot-CC.exe`，约 15-25MB。

## 项目结构

```
1shot-cc/
├── main.py                    # 入口
├── app/
│   ├── config.py              # 配置常量
│   ├── routes/                # API 路由
│   ├── services/              # 业务逻辑
│   ├── utils/                 # 工具函数
│   └── templates/             # 前端页面
├── static/                    # CSS/JS/图片
├── tutorials/                 # 教程源文件
└── build.spec                 # PyInstaller 配置
```

## 许可证

MIT
