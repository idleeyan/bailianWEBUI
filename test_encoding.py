#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

# 修复 Windows 命令行编码问题
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        print("✅ 编码修复已应用")
    except Exception as e:
        print(f"修复失败: {e}")

print("测试 emoji: 🚀 🎨 ✅ ❌")
print("测试中文: 阿里云百炼文生图")
