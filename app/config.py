"""全局配置常量"""

# Node.js LTS 版本（国内镜像）
NODEJS_VERSION = "20.18.0"
NODEJS_DOWNLOAD_URL = (
    f"https://npmmirror.com/mirrors/node/v{NODEJS_VERSION}/node-v{NODEJS_VERSION}-x64.msi"
)

# Git for Windows 版本
GIT_VERSION = "2.47.1"
GIT_DOWNLOAD_URL = (
    f"https://npmmirror.com/mirrors/git-for-windows/v{GIT_VERSION}.windows.1/"
    f"Git-{GIT_VERSION}-64-bit.exe"
)

# npm 淘宝镜像
NPM_REGISTRY = "https://registry.npmmirror.com"

# CC-Switch GitHub
CCSWITCH_REPO = "farion1231/cc-switch"
CCSWITCH_RELEASES_API = f"https://api.github.com/repos/{CCSWITCH_REPO}/releases/latest"

# Claude Code npm 包
CLAUDE_CODE_PACKAGE = "@anthropic-ai/claude-code"

# API 提供商预设
PROVIDERS = {
    "zhipu": {
        "name": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/anthropic",
        "default_haiku": "glm-4.5",
        "default_sonnet": "glm-4.7",
        "default_opus": "glm-4.7",
        "register_url": "https://open.bigmodel.cn",
        "api_key_url": "https://bigmodel.cn/usercenter/proj-mgmt/apikeys",
        "docs_url": "https://docs.bigmodel.cn/cn/coding-plan/tool/claude",
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/anthropic",
        "default_haiku": "deepseek-v4-flash[1m]",
        "default_sonnet": "deepseek-v4-pro[1m]",
        "default_opus": "deepseek-v4-pro[1m]",
        "register_url": "https://platform.deepseek.com",
        "api_key_url": "https://platform.deepseek.com/api_keys",
        "docs_url": "https://api-docs.deepseek.com/zh-cn/",
    },
    "minimax": {
        "name": "MiniMax",
        "base_url": "https://api.minimaxi.com/anthropic",
        "default_haiku": "MiniMax-M1-40k",
        "default_sonnet": "MiniMax-M2",
        "default_opus": "MiniMax-M2",
        "register_url": "https://platform.minimaxi.com",
        "api_key_url": "https://platform.minimaxi.com/user-center/basic-information/interface-key",
        "docs_url": "https://platform.minimaxi.com/docs",
    },
    "mimo": {
        "name": "小米 MiMo",
        "base_url": "https://api.xiaomimimo.com/anthropic",
        "default_haiku": "mimo-v2-flash",
        "default_sonnet": "mimo-v2-flash",
        "default_opus": "mimo-v2-flash",
        "register_url": "https://platform.xiaomimimo.com",
        "api_key_url": "https://platform.xiaomimimo.com/#/console/api-keys",
        "docs_url": "https://github.com/XiaomiMiMo",
    },
    "qwen": {
        "name": "通义千问 Qwen",
        "base_url": "https://dashscope.aliyuncs.com/apps/anthropic",
        "default_haiku": "qwen3.6-flash",
        "default_sonnet": "qwen3.6-plus",
        "default_opus": "qwen3.6-plus",
        "register_url": "https://bailian.console.aliyun.com",
        "api_key_url": "https://bailian.console.aliyun.com/#/api-key",
        "docs_url": "https://www.aliyun.com/product/bailian",
    },
}

# 教程列表
TUTORIALS = {
    "claude": {"id": "claude", "title": "Claude Code 使用指南", "icon": "📘"},
    "apikey": {"id": "apikey", "title": "获取 API 密钥教程", "icon": "🔑"},
    "ccswitch": {"id": "ccswitch", "title": "CC-Switch 使用教程", "icon": "🔀"},
    "proxy": {"id": "proxy", "title": "科学上网指南", "icon": "🌐"},
}
