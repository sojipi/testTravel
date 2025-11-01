# MiniMax API 配置指南

## 📝 问题修复说明

刚才的错误是因为：
1. **函数返回值错误** - 已修复：现在每个函数都返回两个值（思考过程和最终结果）
2. **API配置更新** - 已更新：现在支持MiniMax和其他兼容OpenAI API的服务

## 🔧 MiniMax API 配置步骤

### 1. 复制环境变量文件
```bash
cp .env.example .env
```

### 2. 编辑 .env 文件
填入您的MiniMax API信息：

```bash
# MiniMax API密钥（必填）
MINIMAX_API_KEY=您的实际API密钥

# API Base URL（通常不需要修改）
API_BASE_URL=https://api.minimax.chat/v1

# 模型名称（根据您的套餐选择）
MODEL_NAME=abab6.5s-chat
# 常见模型：
# - abab6.5s-chat (推荐，速度快)
# - abab6.5g-chat (性能强)
# - abab6.5-chat (平衡型)
```

### 3. 获取API密钥
1. 访问 [MiniMax开放平台](https://api.minimax.chat/)
2. 注册/登录账户
3. 在控制台创建API密钥
4. 充值（如需要）

### 4. 启动应用
```bash
# Windows
start.bat

# 或使用PowerShell
.\start.ps1
```

## ⚙️ 自定义配置

### 修改模型
编辑 `.env` 文件中的 `MODEL_NAME`：
```bash
MODEL_NAME=abab6.5g-chat
```

### 修改端口
编辑 `travel_assistant.py` 最后部分：
```python
app.launch(
    server_port=8080,  # 修改为您想要的端口
    ...
)
```

### 使用其他API提供商
如果使用OpenAI、Claude等，只需修改 `.env`：
```bash
# OpenAI示例
API_BASE_URL=https://api.openai.com/v1
MINIMAX_API_KEY=sk-your-openai-key
MODEL_NAME=gpt-4

# Claude示例
API_BASE_URL=https://api.anthropic.com/v1
MINIMAX_API_KEY=sk-ant-your-claude-key
MODEL_NAME=claude-3-sonnet
```

## ❓ 常见问题

**Q: 提示"API key invalid"**
A: 检查 `.env` 文件中的 `MINIMAX_API_KEY` 是否正确填入

**Q: 提示"model not found"**
A: 检查 `MODEL_NAME` 是否为您有权访问的模型

**Q: 流式输出不显示思考过程**
A: 某些模型不支持思考过程输出，这是正常的

**Q: 图片生成失败**
A: 图片生成功能使用的是ModelScope API，如果您不使用该功能，可以忽略

## 🎯 测试配置

启动应用后：
1. 访问 http://localhost:7860
2. 在"目的地推荐"页面填写表单
3. 点击"推荐目的地"
4. 观察是否成功生成结果

如果成功：配置正确！🎉
如果失败：检查控制台错误信息和API配置

---
如有问题，请查看使用说明.md获取更多帮助
