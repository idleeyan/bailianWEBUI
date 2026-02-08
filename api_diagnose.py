#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API诊断工具 - 用于排查400错误
"""
import os
import sys
import json

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

def diagnose_api_error(error_message, model, size, prompt):
    """诊断API错误"""
    suggestions = []
    
    if "400" in error_message:
        suggestions.append("【错误代码 400】请求参数错误，可能原因：")
        
        # 检查模型
        if model.startswith("wan2.") or model.startswith("wanx2."):
            suggestions.append(f"  1. 模型 '{model}' 可能不支持尺寸 '{size}'")
            suggestions.append("     建议尝试: 1024*1024, 512*512, 768*768")
        
        if "wan2.6" in model or "wan2.5" in model or "wan2.2" in model:
            suggestions.append(f"  2. 模型 '{model}' 是较新的模型，可能：")
            suggestions.append("     - 需要特定格式的prompt")
            suggestions.append("     - 不支持某些尺寸")
            suggestions.append("     - 需要开通服务")
        
        if "qwen-image" in model:
            suggestions.append(f"  3. Qwen图像模型 '{model}' 可能需要：")
            suggestions.append("     - 确保已开通阿里云百炼的图像生成服务")
            suggestions.append("     - 检查账户额度是否充足")
        
        suggestions.append("  4. 通用解决方案：")
        suggestions.append("     - 确认 API Key 有效且有权限")
        suggestions.append("     - 使用标准尺寸: 1024*1024")
        suggestions.append("     - 使用简单prompt测试")
        suggestions.append("     - 检查模型是否在支持列表中")
    
    if "401" in error_message:
        suggestions.append("【错误代码 401】API Key 无效或已过期")
        suggestions.append("  - 请检查 API Key 是否正确")
        suggestions.append("  - 在阿里云百炼控制台重新生成 API Key")
    
    if "429" in error_message:
        suggestions.append("【错误代码 429】请求过于频繁")
        suggestions.append("  - 请稍后再试")
        suggestions.append("  - 降低批量生成的数量")
    
    return "\n".join(suggestions)

# 常用且稳定的模型推荐
RECOMMENDED_MODELS = {
    "文生图推荐": [
        ("wanx-v1", "通义万相V1 - 最稳定"),
        ("wanx2.1-t2i-turbo", "通义万相2.1-Turbo - 快速"),
        ("qwen-image", "通义千问-图像 - 通用"),
    ],
    "编辑图片推荐": [
        ("qwen-image-edit", "通义千问-图像编辑"),
    ]
}

if __name__ == "__main__":
    print("=" * 60)
    print("  阿里云百炼API诊断工具")
    print("=" * 60)
    print()
    print("推荐的稳定模型：")
    print()
    
    for category, models in RECOMMENDED_MODELS.items():
        print(f"【{category}】")
        for model_id, desc in models:
            print(f"  - {model_id}")
            print(f"    {desc}")
        print()
    
    print("=" * 60)
    print("常见400错误解决方案：")
    print("=" * 60)
    print("""
1. 模型不支持该尺寸
   - 尝试使用标准尺寸: 1024*1024
   - 或 512*512, 768*768

2. 模型ID错误
   - 请从推荐列表中选择模型
   - 确保拼写完全正确

3. 账户权限不足
   - 登录阿里云百炼控制台
   - 确认已开通图像生成服务
   - 检查账户余额/额度

4. Prompt格式问题
   - 使用简单中文或英文描述
   - 避免特殊字符
   - 长度建议 10-200 字符

5. 如果是批量生成失败
   - 减少批量数量（建议1-3张）
   - 增加请求间隔时间
""")
