#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图 Web UI 快速启动器
"""

import os
import sys
import subprocess

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     阿里云百炼文生图 Web UI 快速启动器                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")

print("[INFO] 正在启动 Web UI...")
print("[INFO] 服务启动后会显示访问地址")
print("[INFO] 按 Ctrl+C 可以停止服务")
print()

# 直接启动bailian_webui.py，让它的输出直接显示
try:
    result = subprocess.run(
        [sys.executable, 'bailian_webui.py'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
except KeyboardInterrupt:
    print("\n[INFO] 服务已停止")
except Exception as e:
    print(f"\n[ERROR] 启动失败: {e}")
    input("按回车键退出...")
