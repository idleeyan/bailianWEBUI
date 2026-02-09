@echo off
chcp 65001 >nul
title ComfyUI 应用快速启动
cd /d "%~dp0"

:: 检查是否存在虚拟环境 (通常命名为 venv 或 .venv)
if exist "venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 正在激活虚拟环境...
    call .venv\Scripts\activate.bat
)

echo 正在启动 ComfyUI WebUI...
python bailian_webui.py

pause