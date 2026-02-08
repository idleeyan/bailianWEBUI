# Web UI Startup Guide

## Method 1: Double-click to run (Recommended)
Double-click `start_webui.bat` file

## Method 2: Run in Command Line
Open Command Prompt (cmd) or PowerShell:
```bash
cd "E:\work\comfyui应用"
python bailian_webui.py
```

## Access Address
After startup, open in browser:
- http://127.0.0.1:7860

If port is occupied, it will try: 7861, 7862, 7870, 8000, 8080

## Stop Service
Press `Ctrl+C` in the running window to stop

## Troubleshooting

**Q: Window flashes and disappears when double-clicking**
A: Run in cmd first to see the error:
```bash
cd "E:\work\comfyui应用"
python bailian_webui.py
```

**Q: Python not found**
A: Make sure Python is installed and added to PATH

**Q: Missing gradio module**
A: Install dependencies:
```bash
pip install gradio requests
```
