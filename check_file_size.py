#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查项目文件大小，预防大文件产生
符合项目规则文档中的要求
"""
import os
import sys

# 配置
MAX_FILE_SIZE = 500  # 最大允许行数
CHECK_EXTENSIONS = ['.py', '.md', '.txt']  # 需要检查的文件类型
EXCLUDE_DIRS = ['__pycache__', '.git', 'generated_images']  # 排除的目录


def get_file_lines(file_path):
    """获取文件行数"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return 0


def check_files():
    """检查所有文件"""
    issues = []
    
    for root, dirs, files in os.walk('.'):
        # 排除不需要检查的目录
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            # 检查文件扩展名
            ext = os.path.splitext(file)[1].lower()
            if ext not in CHECK_EXTENSIONS:
                continue
                
            file_path = os.path.join(root, file)
            lines = get_file_lines(file_path)
            
            if lines > MAX_FILE_SIZE:
                issues.append({
                    'path': file_path,
                    'lines': lines,
                    'max': MAX_FILE_SIZE
                })
    
    return issues


def print_issues(issues):
    """打印检查结果"""
    if not issues:
        print("✅ 所有文件符合大小要求！")
        return
    
    print(f"❌ 发现 {len(issues)} 个文件超过大小限制:")
    print("-" * 80)
    
    for issue in sorted(issues, key=lambda x: x['lines'], reverse=True):
        print(f"文件: {issue['path']}")
        print(f"行数: {issue['lines']} (最大允许: {issue['max']})")
        print(f"超过: {issue['lines'] - issue['max']} 行")
        print()
    
    print("建议：")
    print("1. 拆分大文件为多个模块")
    print("2. 将通用功能提取到独立文件")
    print("3. 参考项目规则文档中的模块化开发规范")


def main():
    """主函数"""
    print(f"📋 检查项目文件大小 (最大允许: {MAX_FILE_SIZE} 行)")
    print("-" * 80)
    
    issues = check_files()
    print_issues(issues)
    
    if issues:
        sys.exit(1)


if __name__ == '__main__':
    main()