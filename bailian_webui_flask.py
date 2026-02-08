#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图 Web UI - Flask版本
支持API密钥保存和完整模型列表
"""
import os
import sys
import time
import webbrowser
import threading
import json
from flask import Flask, render_template_string, request, jsonify, send_from_directory
from flask_cors import CORS

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

try:
    from bailian_image_gen import BailianImageGenerator
except ImportError:
    print("[错误] 未找到 bailian_image_gen 模块！")
    input("按回车键退出...")
    sys.exit(1)

VERSION = "1.2.1"
UPDATE_RULES = "每次功能更新需递增版本号，本次更新添加了增强的终端信息显示功能，包括请求统计、API调用监控和系统状态"
app = Flask(__name__)
CORS(app)
generator = None

# 导入日志模块
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 请求计数器
request_count = 0
generate_count = 0
edit_count = 0
error_count = 0
success_count = 0

# API调用统计
api_call_stats = {
    'total_calls': 0,
    'success_calls': 0,
    'failed_calls': 0,
    'total_time': 0,
    'avg_time': 0
}

# 启动时间
start_time = time.time()

# 最后活动时间
last_activity_time = time.time()

# 配置文件路径
CONFIG_FILE = 'webui_config.json'

# 经过验证的文生图模型列表（避免400错误）
MODEL_CHOICES = [
    "wanx-v1",                          # 最稳定的基础模型（推荐）
    "wanx2.1-t2i-turbo",               # 通义万相2.1-Turbo（推荐）
    "wanx2.1-t2i-plus",                # 通义万相2.1-Plus
    "qwen-image",                      # 通义千问-图像
    "qwen-image-plus",                 # 通义千问-图像Plus
    "flux-schnell",                    # Flux-Schnell
    "flux-dev",                        # Flux-Dev
]

# 图像编辑模型列表（已验证可用）
# 参考文档: https://help.aliyun.com/zh/model-studio/developer-reference/image-edit-api
EDIT_MODEL_CHOICES = [
    "wanx2.1-imageedit",      # 通义万相图像编辑 (推荐)
]

SIZE_CHOICES = ["512*512", "768*768", "1024*1024", "1280*720", "1920*1080"]

def print_stats():
    """打印运行统计信息"""
    global request_count, generate_count, edit_count, error_count, success_count
    global api_call_stats, start_time, last_activity_time
    
    uptime = time.time() - start_time
    idle_time = time.time() - last_activity_time
    
    print()
    print("=" * 60)
    print("   📊 运行统计信息")
    print("=" * 60)
    print(f"   ⏱️  运行时间: {uptime/60:.1f} 分钟")
    print(f"   🕐 最后活动: {idle_time:.1f} 秒前")
    print("-" * 60)
    print(f"   📈 总请求数: {request_count}")
    print(f"   ✅ 成功请求: {success_count}")
    print(f"   ❌ 失败请求: {error_count}")
    if request_count > 0:
        success_rate = (success_count / request_count) * 100
        print(f"   📊 成功率: {success_rate:.1f}%")
    print("-" * 60)
    print(f"   🎨 图片生成: {generate_count} 次")
    print(f"   ✏️  图像编辑: {edit_count} 次")
    print("-" * 60)
    print(f"   🔌 API总调用: {api_call_stats['total_calls']} 次")
    print(f"   ✅ API成功: {api_call_stats['success_calls']} 次")
    print(f"   ❌ API失败: {api_call_stats['failed_calls']} 次")
    if api_call_stats['total_calls'] > 0:
        api_success_rate = (api_call_stats['success_calls'] / api_call_stats['total_calls']) * 100
        print(f"   📊 API成功率: {api_success_rate:.1f}%")
    if api_call_stats['avg_time'] > 0:
        print(f"   ⏱️  API平均耗时: {api_call_stats['avg_time']:.1f} 秒")
    print("=" * 60)
    print()

def update_activity():
    """更新最后活动时间"""
    global last_activity_time
    last_activity_time = time.time()

def update_api_stats(success, elapsed_time):
    """更新API调用统计"""
    global api_call_stats
    api_call_stats['total_calls'] += 1
    if success:
        api_call_stats['success_calls'] += 1
    else:
        api_call_stats['failed_calls'] += 1
    api_call_stats['total_time'] += elapsed_time
    api_call_stats['avg_time'] = api_call_stats['total_time'] / api_call_stats['total_calls']

def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"[警告] 保存配置失败: {e}")
        return False

def init_generator(api_key):
    global generator
    try:
        if api_key and api_key.strip():
            generator = BailianImageGenerator(api_key.strip())
        else:
            generator = BailianImageGenerator()
        return True, "API Key 设置成功！"
    except Exception as e:
        return False, f"错误: {str(e)}"

def generate_image(prompt, model_name, size, seed=None):
    global generator
    if generator is None:
        return None, "错误: 请先设置 API Key"
    if not prompt.strip():
        return None, "错误: 请输入提示词"
    
    logger.info(f"[生成图片] 参数: model={model_name}, size={size}, seed={seed}")
    logger.info(f"[生成图片] 提示词: {prompt.strip()[:100]}...")
    
    try:
        seed_val = int(seed) if seed and str(seed).strip() else None
        api_start_time = time.time()
        
        result = generator.generate_image(
            prompt=prompt.strip(),
            model=model_name,
            size=size,
            seed=seed_val
        )
        
        api_elapsed_time = time.time() - api_start_time
        
        if result['success']:
            images = [os.path.basename(f) for f in result['files'] if os.path.exists(f)]
            logger.info(f"[生成图片] ✅ API调用成功，耗时 {api_elapsed_time:.2f} 秒")
            update_api_stats(True, api_elapsed_time)
            return images, f"成功生成 {len(images)} 张图片！"
        else:
            error_msg = result.get('error', '未知错误')
            logger.error(f"[生成图片] ❌ API调用失败，耗时 {api_elapsed_time:.2f} 秒，错误: {error_msg}")
            update_api_stats(False, api_elapsed_time)
            return None, f"错误: {error_msg}"
    except Exception as e:
        logger.exception(f"[生成图片] ❌ 发生异常: {str(e)}")
        update_api_stats(False, 0)
        return None, f"错误: {str(e)}"

def edit_image(prompt, image_path, model_name, size, seed=None):
    global generator
    if generator is None:
        return None, "错误: 请先设置 API Key"
    if not prompt.strip():
        return None, "错误: 请输入编辑指令"
    if not os.path.exists(image_path):
        return None, "错误: 图片文件不存在"
    
    logger.info(f"[图像编辑] 参数: model={model_name}, size={size}, seed={seed}")
    logger.info(f"[图像编辑] 图片路径: {image_path}")
    logger.info(f"[图像编辑] 图片大小: {os.path.getsize(image_path)} bytes")
    logger.info(f"[图像编辑] 编辑指令: {prompt.strip()[:100]}...")
    
    try:
        seed_val = int(seed) if seed and str(seed).strip() else None
        api_start_time = time.time()
        
        # 调用通义万相图像编辑 API
        result = generator.edit_image(
            prompt=prompt.strip(),
            image_path=image_path,
            model=model_name,
            size=size,
            n=1,
            seed=seed_val,
            edit_function="description_edit"
        )
        
        api_elapsed_time = time.time() - api_start_time
        
        if result['success']:
            images = [os.path.basename(f) for f in result['files'] if os.path.exists(f)]
            logger.info(f"[图像编辑] ✅ API调用成功，耗时 {api_elapsed_time:.2f} 秒")
            update_api_stats(True, api_elapsed_time)
            return images, f"成功编辑 {len(images)} 张图片！"
        else:
            error_msg = result.get('error', '未知错误')
            logger.error(f"[图像编辑] ❌ API调用失败，耗时 {api_elapsed_time:.2f} 秒，错误: {error_msg}")
            update_api_stats(False, api_elapsed_time)
            # 更详细的错误信息
            if "400 Client Error" in error_msg:
                if "url error" in error_msg.lower():
                    return None, f"错误: API端点或模型不可用。可能原因：1. 该模型尚未开通权限 2. 阿里云账号未开通图像编辑服务。请在阿里云控制台检查服务开通状态。详细错误: {error_msg}"
                return None, f"错误: 请求参数错误。可能原因：API Key无效、模型选择错误、尺寸不匹配或图片格式错误。详细错误: {error_msg}"
            elif "401 Unauthorized" in error_msg:
                return None, f"错误: API Key无效或未授权，请检查您的API Key是否正确。详细错误: {error_msg}"
            elif "403 Forbidden" in error_msg:
                return None, f"错误: 没有权限使用该模型或API调用次数超限。详细错误: {error_msg}"
            elif "500 Server Error" in error_msg:
                return None, f"错误: 服务器内部错误，请稍后重试。详细错误: {error_msg}"
            else:
                return None, f"错误: {error_msg}"
    except Exception as e:
        logger.exception(f"[图像编辑] ❌ 发生异常: {str(e)}")
        update_api_stats(False, 0)
        return None, f"错误: {str(e)}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>阿里云百炼文生图 v{{ version }}</title>
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🎨%3C/text%3E%3C/svg%3E">
    <style>
        body {
            font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 {
            color: white;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.9);
            margin-bottom: 30px;
            font-size: 14px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .section {
            margin-bottom: 25px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            background: #fafafa;
        }
        .section h3 {
            margin-top: 0;
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #555;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            border-color: #007bff;
            outline: none;
        }
        select {
            height: 45px;
            background: white;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
            font-weight: bold;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        button:active {
            transform: translateY(0);
        }
        button.secondary {
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }
        button.secondary:hover {
            box-shadow: 0 5px 15px rgba(108, 117, 125, 0.4);
        }
        .status {
            margin-top: 15px;
            padding: 12px;
            border-radius: 6px;
            font-weight: 500;
        }
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .images {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
        }
        .images img {
            max-width: 300px;
            border-radius: 8px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            transition: transform 0.3s;
        }
        .images img:hover {
            transform: scale(1.05);
        }
        #loading {
            display: none;
            text-align: center;
            padding: 30px;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .checkbox-container {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        .checkbox-container input[type="checkbox"] {
            width: auto;
            margin-right: 8px;
        }
        .checkbox-container label {
            margin: 0;
            font-weight: normal;
        }
    </style>
</head>
<body>
    <h1>🎨 阿里云百炼文生图</h1>
    <p class="subtitle">版本: {{ version }} | 基于阿里云百炼大模型</p>
    
    <div class="container">
        <div class="section" id="api-section">
            <h3>🔑 API 密钥设置</h3>
            <label>API Key:</label>
            <input type="password" id="api_key" placeholder="请输入您的阿里云百炼 API Key">
            <div class="checkbox-container">
                <input type="checkbox" id="save_api_key" checked>
                <label for="save_api_key">下次自动填充</label>
            </div>
            <div>
                <button onclick="setApiKey()">设置 API Key</button>
                <button onclick="clearApiKey()" class="secondary">清除已保存的密钥</button>
            </div>
            <div id="api-status" class="status"></div>
        </div>
        
        <div class="section" id="gen-section" style="display: none;">
            <h3>🖼️ 图片生成</h3>
            <label>提示词 (Prompt):</label>
            <textarea id="prompt" rows="4" placeholder="描述您想要生成的图片内容，例如：一只可爱的猫咪在草地上玩耍"></textarea>
            
            <label>选择模型:</label>
            <select id="model">
                {% for model in models %}
                <option value="{{ model }}" {% if loop.first %}selected{% endif %}>{{ model }}</option>
                {% endfor %}
            </select>
            
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 12px; margin: 10px 0; border-radius: 4px; font-size: 13px;">
                <strong>💡 使用提示：</strong><br>
                • 推荐模型：<strong>wanx-v1</strong>（最稳定）或 <strong>wanx2.1-t2i-turbo</strong>（快速）<br>
                • 如果出现400错误，请检查API Key权限和模型可用性<br>
                • 批量生成建议每次1-3张，避免请求过于频繁
            </div>
            
            <label>图片尺寸:</label>
            <select id="size">
                <option value="512*512">512 × 512</option>
                <option value="768*768">768 × 768</option>
                <option value="1024*1024" selected>1024 × 1024 (推荐)</option>
                <option value="1280*720">1280 × 720 (横屏)</option>
                <option value="1920*1080">1920 × 1080 (高清)</option>
            </select>
            
            <label>随机种子 (可选):</label>
            <input type="number" id="seed" placeholder="留空则随机生成">
            
            <div style="border-top: 2px solid #e0e0e0; margin: 20px 0; padding-top: 20px;">
                <h4 style="margin-top: 0; color: #667eea;">📦 批量生成设置</h4>
                <label>生成数量 (1-10张):</label>
                <input type="number" id="batch_count" min="1" max="10" value="1">
                
                <div class="checkbox-container">
                    <input type="checkbox" id="random_seeds" checked>
                    <label for="random_seeds" style="margin: 0; font-weight: normal;">每张使用不同随机种子（生成多样化图片）</label>
                </div>
            </div>
            
            <button onclick="generateImage()">🚀 开始生成</button>
            
            <div id="loading">
                <div class="spinner"></div>
                <p id="loading-text">正在生成图片，请稍候...</p>
                <p id="progress-text" style="margin-top: 10px; color: #666; font-weight: bold;"></p>
            </div>
            
            <div id="result-status" class="status"></div>
            <div id="images" class="images"></div>
        </div>
        
        <div class="section" id="edit-section" style="display: none;">
            <h3>✏️ 图像编辑</h3>
            <label>上传参考图片:</label>
            <input type="file" id="image_file" accept="image/*">
            
            <label>编辑指令 (Prompt):</label>
            <textarea id="edit_prompt" rows="4" placeholder="描述您想要如何编辑图片，例如：把背景换成海滩，给人物戴上墨镜"></textarea>
            
            <label>选择编辑模型:</label>
            <select id="edit_model">
                {% for model in edit_models %}
                <option value="{{ model }}" {% if loop.first %}selected{% endif %}>{{ model }}</option>
                {% endfor %}
            </select>
            
            <label>输出尺寸:</label>
            <select id="edit_size">
                <option value="512*512">512 × 512</option>
                <option value="768*768">768 × 768</option>
                <option value="1024*1024" selected>1024 × 1024 (推荐)</option>
                <option value="1280*720">1280 × 720 (16:9)</option>
                <option value="1920*1080">1920 × 1080 (16:9)</option>
            </select>
            
            <label>随机种子 (可选):</label>
            <input type="number" id="edit_seed" placeholder="留空则随机生成">
            
            <button onclick="editImage()">✏️ 编辑图片</button>
            
            <div id="edit_loading" style="display: none;">
                <div class="spinner"></div>
                <div id="edit_loading-text">正在编辑图片，请稍候...</div>
            </div>
            
            <div id="edit_result-status" class="status"></div>
            <div id="edit_images" class="images"></div>
        </div>
    </div>
    
    <script>
        // 页面加载时自动加载保存的API Key
        fetch('/api/load_config')
        .then(r => r.json())
        .then(data => {
            if (data.api_key) {
                document.getElementById('api_key').value = data.api_key;
                document.getElementById('api-status').textContent = '✓ 已加载保存的 API Key';
                document.getElementById('api-status').className = 'status info';
            }
        }).catch(err => {
            console.error('加载配置失败:', err);
        });
        
        // 定义setApiKey函数
        function setApiKey() {
            console.log('[DEBUG] setApiKey 被调用');
            const apiKey = document.getElementById('api_key').value;
            const saveKey = document.getElementById('save_api_key').checked;
            console.log('[DEBUG] API Key:', apiKey ? '已输入' : '未输入');

            if (!apiKey) {
                document.getElementById('api-status').textContent = '请输入API Key';
                document.getElementById('api-status').className = 'status error';
                return;
            }
            
            fetch('/api/set_key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({api_key: apiKey, save: saveKey})
            })
            .then(r => {
                if (!r.ok) throw new Error('服务器错误: ' + r.status);
                return r.json();
            })
            .then(data => {
                document.getElementById('api-status').textContent = data.message;
                document.getElementById('api-status').className = 'status ' + (data.success ? 'success' : 'error');
                if (data.success) {
                    document.getElementById('api-section').style.display = 'none';
                    document.getElementById('gen-section').style.display = 'block';
                    document.getElementById('edit-section').style.display = 'block';
                }
            })
            .catch(err => {
                document.getElementById('api-status').textContent = '网络错误: ' + err.message;
                document.getElementById('api-status').className = 'status error';
            });
        }
        
        // 定义clearApiKey函数
        function clearApiKey() {
            fetch('/api/clear_config', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'}
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('api_key').value = '';
                document.getElementById('api-status').textContent = data.message;
                document.getElementById('api-status').className = 'status info';
            }).catch(err => {
                document.getElementById('api-status').textContent = '清除配置失败: ' + err.message;
                document.getElementById('api-status').className = 'status error';
            });
        }
        
        // 定义generateImage函数
        async function generateImage() {
            const prompt = document.getElementById('prompt').value;
            const model = document.getElementById('model').value;
            const size = document.getElementById('size').value;
            const seed = document.getElementById('seed').value;
            const batchCount = parseInt(document.getElementById('batch_count').value) || 1;
            const useRandomSeeds = document.getElementById('random_seeds').checked;
            
            if (!prompt) {
                alert('请输入提示词');
                return;
            }
            
            if (batchCount < 1 || batchCount > 10) {
                alert('批量生成数量必须在 1-10 之间');
                return;
            }
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result-status').textContent = '';
            document.getElementById('images').innerHTML = '';
            document.getElementById('loading-text').textContent = batchCount > 1 ? `正在批量生成 ${batchCount} 张图片...` : '正在生成图片，请稍候...';
            
            const allImages = [];
            const errors = [];
            
            for (let i = 0; i < batchCount; i++) {
                const currentSeed = useRandomSeeds ? '' : seed;
                const progressText = batchCount > 1 ? `正在生成第 ${i + 1}/${batchCount} 张...` : '';
                document.getElementById('progress-text').textContent = progressText;
                
                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({prompt, model, size, seed: currentSeed})
                    });
                    
                    if (!response.ok) throw new Error('服务器错误: ' + response.status);
                    
                    const data = await response.json();
                    
                    if (data.success && data.images) {
                        allImages.push(...data.images);
                    } else {
                        errors.push(`第 ${i + 1} 张: ${data.message}`);
                    }
                } catch (err) {
                    errors.push(`第 ${i + 1} 张: ${err.message}`);
                }
                
                // 添加小延迟避免请求过快
                if (i < batchCount - 1) {
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }
            
            document.getElementById('loading').style.display = 'none';
            document.getElementById('progress-text').textContent = '';
            
            if (allImages.length > 0) {
                document.getElementById('result-status').textContent = `成功生成 ${allImages.length} 张图片！${errors.length > 0 ? ' (失败: ' + errors.length + ' 张)' : ''}`;
                document.getElementById('result-status').className = 'status success';
                
                const container = document.getElementById('images');
                allImages.forEach(img => {
                    const imgElem = document.createElement('img');
                    imgElem.src = '/image/' + img;
                    imgElem.title = img;
                    container.appendChild(imgElem);
                });
            } else {
                let errorMsg = errors.length > 0 ? errors[0] : '未知错误';
                let diagnosis = '';
                
                // 错误诊断
                if (errorMsg.includes('400')) {
                    diagnosis = '<br><br>【400错误诊断】';
                    diagnosis += '<br>1. 尝试使用推荐模型：wanx-v1 或 wanx2.1-t2i-turbo';
                    diagnosis += '<br>2. 使用标准尺寸：1024×1024';
                    diagnosis += '<br>3. 简化提示词，避免特殊字符';
                    diagnosis += '<br>4. 检查API Key是否有图像生成权限';
                }
                
                document.getElementById('result-status').innerHTML = '生成失败: ' + errorMsg + diagnosis;
                document.getElementById('result-status').className = 'status error';
            }
        }

        // 定义editImage函数
        async function editImage() {
            const fileInput = document.getElementById('image_file');
            const prompt = document.getElementById('edit_prompt').value;
            const model = document.getElementById('edit_model').value;
            const size = document.getElementById('edit_size').value;
            const seed = document.getElementById('edit_seed').value;

            if (!fileInput.files || fileInput.files.length === 0) {
                alert('请上传参考图片');
                return;
            }

            if (!prompt) {
                alert('请输入编辑指令');
                return;
            }

            document.getElementById('edit_loading').style.display = 'block';
            document.getElementById('edit_result-status').textContent = '';
            document.getElementById('edit_images').innerHTML = '';

            const formData = new FormData();
            formData.append('image', fileInput.files[0]);
            formData.append('prompt', prompt);
            formData.append('model', model);
            formData.append('size', size);
            formData.append('seed', seed);

            try {
                const response = await fetch('/api/edit', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) throw new Error('服务器错误: ' + response.status);

                const data = await response.json();

                if (data.success && data.images) {
                    document.getElementById('edit_result-status').textContent = data.message;
                    document.getElementById('edit_result-status').className = 'status success';

                    const container = document.getElementById('edit_images');
                    container.innerHTML = ''; // 清空之前的结果
                    data.images.forEach(img => {
                        const imgElem = document.createElement('img');
                        imgElem.src = '/image/' + img;
                        imgElem.title = img;
                        container.appendChild(imgElem);
                    });
                } else {
                    let errorMsg = data.message || '未知错误';
                    let diagnosis = '';

                    // 错误诊断
                    if (errorMsg.includes('400')) {
                        diagnosis = '<br><br>【400错误诊断】';
                        diagnosis += '<br>1. 图像编辑仅支持特定格式：PNG, JPG, JPEG';
                        diagnosis += '<br>2. 图片大小建议不超过 5MB';
                        diagnosis += '<br>3. 使用推荐的编辑模型：qwen-image-edit';
                        diagnosis += '<br>4. 确保API Key有图像编辑权限';
                    }

                    document.getElementById('edit_result-status').innerHTML = '编辑失败: ' + errorMsg + diagnosis;
                    document.getElementById('edit_result-status').className = 'status error';
                }
            } catch (err) {
                document.getElementById('edit_result-status').textContent = '网络错误: ' + err.message;
                document.getElementById('edit_result-status').className = 'status error';
            } finally {
                document.getElementById('edit_loading').style.display = 'none';
                // 确保加载状态被隐藏
                setTimeout(() => {
                    document.getElementById('edit_loading').style.display = 'none';
                }, 100);
            }
        }

        // 确保所有函数都已定义后，再处理可能的事件
        if (typeof setApiKey !== 'function') {
            console.error('setApiKey function is not defined!');
        }
        if (typeof clearApiKey !== 'function') {
            console.error('clearApiKey function is not defined!');
        }
        if (typeof generateImage !== 'function') {
            console.error('generateImage function is not defined!');
        }
        if (typeof editImage !== 'function') {
            console.error('editImage function is not defined!');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, version=VERSION, models=MODEL_CHOICES, edit_models=EDIT_MODEL_CHOICES)

@app.route('/api/load_config', methods=['GET'])
def load_config_endpoint():
    """加载配置"""
    config = load_config()
    return jsonify({'api_key': config.get('api_key', '')})

@app.route('/api/set_key', methods=['POST'])
def set_key():
    global generator
    data = request.json
    api_key = data.get('api_key', '').strip()
    save = data.get('save', True)
    
    success, message = init_generator(api_key)
    
    if success and save:
        config = load_config()
        config['api_key'] = api_key
        save_config(config)
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/clear_config', methods=['POST'])
def clear_config():
    """清除配置"""
    config = load_config()
    if 'api_key' in config:
        del config['api_key']
        save_config(config)
    return jsonify({'success': True, 'message': '已清除保存的 API Key'})

@app.route('/api/generate', methods=['POST'])
def generate():
    global generator, generate_count, request_count, success_count, error_count
    update_activity()
    request_count += 1
    
    if generator is None:
        logger.warning("[生成图片] 拒绝请求：未设置 API Key")
        error_count += 1
        return jsonify({'success': False, 'message': '请先设置 API Key'})
    
    data = request.json
    prompt = data.get('prompt', '').strip()
    model = data.get('model', MODEL_CHOICES[0])
    size = data.get('size', '1024*1024')
    seed = data.get('seed', '')
    
    logger.info(f"[生成图片] 模型: {model}, 尺寸: {size}, 提示词: {prompt[:50]}...")
    
    if not prompt:
        logger.warning("[生成图片] 拒绝请求：提示词为空")
        error_count += 1
        return jsonify({'success': False, 'message': '请输入提示词'})
    
    generate_count += 1
    logger.info(f"[生成图片] 开始生成第 {generate_count} 张图片...")
    
    start_time = time.time()
    images, message = generate_image(prompt, model, size, seed)
    elapsed_time = time.time() - start_time
    
    if images:
        success_count += 1
        logger.info(f"[生成图片] ✅ 成功生成 {len(images)} 张图片，耗时 {elapsed_time:.1f} 秒")
        return jsonify({
            'success': True, 
            'message': message,
            'images': images
        })
    else:
        error_count += 1
        logger.error(f"[生成图片] ❌ 生成失败: {message}")
        return jsonify({'success': False, 'message': message})

@app.route('/api/edit', methods=['POST'])
def edit():
    global generator, edit_count, request_count, success_count, error_count
    update_activity()
    request_count += 1
    
    if generator is None:
        logger.warning("[图像编辑] 拒绝请求：未设置 API Key")
        error_count += 1
        return jsonify({'success': False, 'message': '请先设置 API Key'})
    
    # 处理文件上传
    if 'image' not in request.files:
        logger.warning("[图像编辑] 拒绝请求：未上传图片")
        error_count += 1
        return jsonify({'success': False, 'message': '请上传图片文件'})
    
    image_file = request.files['image']
    if image_file.filename == '':
        logger.warning("[图像编辑] 拒绝请求：图片文件名为空")
        error_count += 1
        return jsonify({'success': False, 'message': '请选择图片文件'})
    
    prompt = request.form.get('prompt', '').strip()
    model = request.form.get('model', EDIT_MODEL_CHOICES[0])
    size = request.form.get('size', '1024*1024')
    seed = request.form.get('seed', '')
    
    logger.info(f"[图像编辑] 模型: {model}, 提示词: {prompt[:50]}...")
    logger.info(f"[图像编辑] 上传文件: {image_file.filename}, 类型: {image_file.content_type}")
    
    if not prompt:
        logger.warning("[图像编辑] 拒绝请求：编辑指令为空")
        error_count += 1
        return jsonify({'success': False, 'message': '请输入编辑指令'})
    
    # 保存上传的图片
    import uuid
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    filename = f"{uuid.uuid4().hex}_{image_file.filename}"
    image_path = os.path.join(upload_dir, filename)
    image_file.save(image_path)
    
    # 检查文件类型和大小
    file_size = os.path.getsize(image_path)
    logger.info(f"[图像编辑] 保存文件: {image_path}, 大小: {file_size/1024:.1f} KB")
    
    edit_count += 1
    logger.info(f"[图像编辑] 开始第 {edit_count} 次编辑...")
    
    start_time = time.time()
    try:
        images, message = edit_image(prompt, image_path, model, size, seed)
        elapsed_time = time.time() - start_time
        
        if images:
            success_count += 1
            logger.info(f"[图像编辑] ✅ 成功编辑图片，耗时 {elapsed_time:.1f} 秒")
            return jsonify({
                'success': True, 
                'message': message,
                'images': images
            })
        else:
            error_count += 1
            logger.error(f"[图像编辑] ❌ 编辑失败: {message}")
            return jsonify({'success': False, 'message': message})
    finally:
        # 删除临时文件
        if os.path.exists(image_path):
            os.remove(image_path)
            logger.debug(f"[图像编辑] 删除临时文件: {image_path}")

@app.route('/image/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory('generated_images', filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取运行统计信息"""
    global request_count, generate_count, edit_count, error_count, success_count
    global api_call_stats, start_time, last_activity_time
    
    uptime = time.time() - start_time
    idle_time = time.time() - last_activity_time
    
    success_rate = (success_count / request_count * 100) if request_count > 0 else 0
    api_success_rate = (api_call_stats['success_calls'] / api_call_stats['total_calls'] * 100) if api_call_stats['total_calls'] > 0 else 0
    
    return jsonify({
        'success': True,
        'stats': {
            'uptime_seconds': round(uptime, 1),
            'uptime_minutes': round(uptime / 60, 1),
            'idle_seconds': round(idle_time, 1),
            'total_requests': request_count,
            'successful_requests': success_count,
            'failed_requests': error_count,
            'success_rate': round(success_rate, 1),
            'generate_count': generate_count,
            'edit_count': edit_count,
            'api_stats': {
                'total_calls': api_call_stats['total_calls'],
                'success_calls': api_call_stats['success_calls'],
                'failed_calls': api_call_stats['failed_calls'],
                'success_rate': round(api_success_rate, 1),
                'avg_time': round(api_call_stats['avg_time'], 2)
            }
        }
    })

def main():
    print("=" * 50)
    print("   阿里云百炼文生图 Web UI")
    print(f"   版本: {VERSION}")
    print("=" * 50)
    print()
    
    ports = [7860, 7861, 7862, 7870, 7880, 8000, 8080, 5000]
    port = None
    
    import socket
    for p in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', p))
            sock.close()
            port = p
            break
        except:
            continue
    
    if port is None:
        print("[错误] 未找到可用端口！")
        input("按回车键退出...")
        return
    
    print(f"[信息] 正在启动服务器，端口: {port}...")
    print()
    print("=" * 50)
    print("   服务器运行中！")
    print(f"   访问地址: http://127.0.0.1:{port}")
    print("=" * 50)
    print()
    print("[信息] 正在打开浏览器...")
    print("[信息] 按 Ctrl+C 停止服务")
    print()
    
    # 打开浏览器
    def open_browser():
        time.sleep(2)
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
        except:
            pass
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        app.run(host='127.0.0.1', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n[信息] 服务器已停止")
        print_stats()

if __name__ == '__main__':
    main()
