#!/bin/bash

echo "==============================================="
echo "          阿里云百炼文生图 Web UI"
echo "==============================================="
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到Python，请先安装Python"
    echo "下载地址：https://www.python.org/downloads/"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🚀 激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
if ! pip list | grep -E "(gradio|requests)" &> /dev/null; then
    echo "📦 安装依赖包..."
    pip install requests gradio
fi

# 启动WebUI
echo "🎯 启动WebUI..."
python bailian_webui.py

echo
echo "🛑 WebUI已停止"