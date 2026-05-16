# 贡献指南

感谢你有兴趣为 1shot-CC 做出贡献！👋✨

1shot-CC 是一个面向**零命令行经验用户**的 Windows 桌面向导。在贡献前，请记住核心理念：**让一切变得简单**。

## 🛠️ 开发环境

```bash
git clone https://github.com/JananZZZ/1shot-cc.git
cd 1shot-cc
pip install flask
python main.py
```

## 📐 编码风格

- **Keep It Simple** — 函数 < 50 行，文件 < 800 行
- **命名清晰** — 变量和函数用描述性名称，小白用户也能猜到含义
- **少即是多** — 不引入超过当前任务所需的抽象
- **善用 emoji 表达** — 在 UI 文字中适当使用 emoji 帮助理解

## 🐛 Bug 修复

1. 先提 Issue 描述问题
2. 在 PR 中引用 Issue 编号
3. 确保错误对用户友好（中文，面向小白）

## ✨ 新功能

1. 先开 Issue 或 Discussion 讨论
2. 等待维护者反馈后再开始编码
3. 考虑新手用户体验 —— 多一个配置项就是多一个困惑点

## 💬 提交信息

使用 [约定式提交](https://www.conventionalcommits.org/zh-hans/) 格式：

```
feat: 新增某功能
fix: 修复某问题
docs: 更新文档
refactor: 重构某模块
```

## 🧪 测试

在提交 PR 前，请确保：

- [ ] `python main.py` 能正常启动
- [ ] 9 个 wizard 页面均可正常打开
- [ ] 安装 / 卸载流程无异常

---

再次感谢你的贡献！每一份力量都让 1shot-CC 变得更好 ❤️
