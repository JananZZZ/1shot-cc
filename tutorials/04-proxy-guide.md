# 科学上网简明指南

## 我需要科学上网吗？
- 使用国内 AI 供应商 API → **不需要**
- npm 使用淘宝镜像 → **不需要**
- 访问 GitHub → 有时需要
- 使用 Anthropic 官方 API → 需要

## Clash for Windows
- 下载: https://clashmetas.com.cn/clash-for-windows
- 配置: 添加订阅链接 → 下载配置 → 选择节点
- 模式: Rule（规则）模式，国内直连、国外代理

## 服务平台
- 魔戒等网络加速服务
- 选择运营时间长、口碑好的服务商
- 先月付试用，不要一次性长期购买

## npm 镜像（无需代理）
```
npm config set registry https://registry.npmmirror.com
```

## 安全提示
- 勿在代理环境登录敏感账户
- 使用开源客户端，避免不明来源的"定制版"
- 不使用代理时关闭客户端
