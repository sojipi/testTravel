#!/bin/bash

# 银发族智能旅行助手启动脚本

echo "🧳 银发族智能旅行助手启动脚本"
echo "================================"

# 检查是否安装了Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查是否安装了pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误：未找到pip3，请先安装pip"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  警告：未找到.env文件"
    echo "请将.env.example复制为.env，并填入您的ModelScope Token"
    echo "cp .env.example .env"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""

# 虚拟环境检查
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "📦 安装依赖包..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🚀 启动应用..."
echo "访问地址：http://localhost:7860"
echo ""
echo "按 Ctrl+C 停止应用"
echo ""

python3 travel_assistant.py
