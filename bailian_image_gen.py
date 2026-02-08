#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图简易调用程序
版本: 1.2.0
更新规则: 每次功能更新需递增版本号
"""

import requests
import json
import base64
import os
import time
from datetime import datetime


class BailianImageGenerator:
    """阿里云百炼文生图API调用类"""
    
    # API配置
    # 文生图 API
    API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    # 图生图（通义万相图像编辑）API
    IMAGE_EDIT_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
    # 千问图像编辑 API（多模态生成）
    MULTIModal_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks/"
    
    # 文生图模型列表
    MODELS = {
        # 文生图模型
        "1": ("wanx-v1", "通义万相-文生图V1（默认）"),
        "2": ("wanx2.1-t2i-turbo", "通义万相2.1-Turbo"),
        "3": ("wanx2.1-t2i-plus", "通义万相2.1-Plus"),
        "4": ("wan2.6-t2i", "通义万相2.6-文生图"),
        "5": ("wan2.5-t2i-preview", "通义万相2.5-文生图预览版"),
        "6": ("wan2.2-t2i-plus", "通义万相2.2-文生图Plus"),
        "7": ("wan2.2-t2i-flash", "通义万相2.2-文生图Flash"),
        "8": ("wan2.0-t2i-turbo", "通义万相2.0-Turbo"),
        "9": ("wanx2.0-t2i-turbo", "通义万相2.0-Turbo"),
        
        # Qwen图像模型
        "10": ("qwen-image", "通义千问-图像生成"),
        "11": ("qwen-image-plus", "通义千问-图像生成Plus"),
        "12": ("qwen-image-max", "通义千问-图像生成Max"),
        "13": ("qwen-image-turbo", "通义千问-图像生成Turbo"),
        "14": ("qwen-image-plus-2026-01-09", "通义千问-图像Plus(2026版)"),
        "15": ("qwen-image-max-2025-12-30", "通义千问-图像Max(2025版)"),
        
        # Flux模型
        "16": ("flux-schnell", "Flux-Schnell"),
        "17": ("flux-dev", "Flux-Dev"),
        "18": ("flux-merged", "Flux-Merged"),
        
        # 其他图像生成
        "19": ("wanx-sketch-to-image-lite", "通义万相-草图生图"),
        "20": ("wanx-x-painting", "通义万相-X绘画"),
        "21": ("wanx-style-repaint-v1", "通义万相-风格重绘"),
        "22": ("wanx-background-generation-v2", "通义万相-背景生成V2"),
        "23": ("wanx-poster-generation-v1", "通义万相-海报生成"),
        "24": ("wanx-virtualmodel", "通义万相-虚拟模特"),
        
        # 图像扩展/编辑
        "25": ("image-out-painting", "图像画面扩展"),
        "26": ("wanx2.1-imageedit", "通义万相2.1-图像编辑"),
        "27": ("wanx2.1-vace-plus", "通义万相2.1-VACE Plus"),
        "28": ("wan2.5-i2i-preview", "通义万相2.5-图生图"),
        
        # 艺术字
        "29": ("wordart-semantic", "艺术字-语义"),
        "30": ("wordart-texture", "艺术字-纹理"),
        
        # 虚拟试衣
        "31": ("aitryon", "虚拟试衣"),
        "32": ("aitryon-plus", "虚拟试衣Plus"),
        "33": ("aitryon-refiner", "虚拟试衣精修"),
        "34": ("aitryon-parsing-v1", "虚拟试衣解析"),
        
        # Emoji
        "35": ("emoji-v1", "Emoji生成"),
        "36": ("emoji-detect-v1", "Emoji检测"),
        
        # 多语言图像
        "37": ("qwen-mt-image", "通义千问-多语言图像"),
    }
    
    # 图像编辑模型列表（需要上传参考图片）
    EDIT_MODELS = {
        # 图像编辑模型
        "1": ("qwen-image-edit", "通义千问-图像编辑"),
        "2": ("qwen-image-edit-plus", "通义千问-图像编辑Plus"),
        "3": ("qwen-image-edit-max", "通义千问-图像编辑Max"),
        "4": ("qwen-image-edit-plus-2025-12-15", "图像编辑Plus(2025-12)"),
        "5": ("qwen-image-edit-plus-2025-10-30", "图像编辑Plus(2025-10)"),
        "6": ("qwen-image-edit-max-2026-01-16", "图像编辑Max(2026版)"),
    }
    
    def __init__(self, api_key=None):
        """
        初始化生成器
        
        Args:
            api_key: 阿里云百炼API Key，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请提供API Key或设置环境变量 DASHSCOPE_API_KEY")
    
    def list_models(self):
        """显示可用的模型列表"""
        print("\n可用的文生图模型列表:")
        print("-" * 50)
        for key, (model_id, desc) in self.MODELS.items():
            print(f"  [{key}] {model_id} - {desc}")
        print("-" * 50)
    
    def list_edit_models(self):
        """显示可用的图像编辑模型列表"""
        print("\n可用的图像编辑模型列表:")
        print("-" * 50)
        for key, (model_id, desc) in self.EDIT_MODELS.items():
            print(f"  [{key}] {model_id} - {desc}")
        print("-" * 50)
    
    def generate_image(self, prompt, model="wanx-v1", size="1024*1024", n=1, seed=None):
        """
        生成图片
        
        Args:
            prompt: 图片描述文本（必填）
            model: 模型名称，默认 wanx-v1
            size: 图片尺寸，默认 1024*1024，可选 512*512, 768*768, 1024*1024, 1280*720 等
            n: 生成图片数量，默认1张
            seed: 随机种子，可选
            
        Returns:
            dict: 包含生成结果的字典
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"  # 启用异步模式
        }
        
        payload = {
            "model": model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": size,
                "n": n
            }
        }
        
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        print(f"\n正在生成图片...")
        print(f"模型: {model}")
        print(f"提示词: {prompt}")
        print(f"尺寸: {size}")
        
        try:
            # 提交任务
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"任务已提交，任务ID: {task_id}")
                return self._wait_for_result(task_id)
            else:
                return {"success": False, "error": f"提交任务失败: {result}"}
                
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"请求异常: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}
    
    def edit_image(self, prompt, image_path, model="wanx2.1-imageedit", size="1024*1024", n=1, seed=None, edit_function="description_edit"):
        """
        编辑图片（图生图）- 使用通义万相 API
        参考文档: https://help.aliyun.com/zh/model-studio/wanx-image-edit
        
        Args:
            prompt: 编辑指令文本（必填）
            image_path: 参考图片路径（必填）
            model: 模型名称，默认 wanx2.1-imageedit
            size: 图片尺寸（对wanx2.1无效）
            n: 生成图片数量，默认1张
            seed: 随机种子，可选
            edit_function: 编辑功能类型，默认 description_edit（指令编辑）
            
        Returns:
            dict: 包含生成结果的字典
        """
        # 读取并编码图片
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return {"success": False, "error": f"读取图片失败: {str(e)}"}
        
        # 根据文件扩展名确定 MIME 类型
        ext = image_path.lower().split('.')[-1] if '.' in image_path else 'png'
        mime_type = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }.get(ext, 'image/png')
        
        # 构建通义万相图像编辑 API 的请求体
        # input.function: 编辑功能类型
        # input.prompt: 文本指令
        # input.base_image_url: 原图（支持base64）
        payload = {
            "model": model,
            "input": {
                "function": edit_function,
                "prompt": prompt,
                "base_image_url": f"data:{mime_type};base64,{image_data}"
            },
            "parameters": {
                "n": n
            }
        }
        
        # 添加可选参数
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        # 某些功能支持 strength 参数（编辑强度）
        if edit_function in ["description_edit", "stylization_all"]:
            payload["parameters"]["strength"] = 0.5
        
        # 使用异步模式
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }
        
        print(f"\n正在编辑图片（通义万相）...")
        print(f"模型: {model}")
        print(f"功能: {edit_function}")
        print(f"提示词: {prompt}")
        print(f"参考图片: {image_path}")
        print(f"图片 MIME 类型: {mime_type}")
        
        try:
            # 提交任务
            print(f"[DEBUG] 发送请求到: {self.IMAGE_EDIT_URL}")
            print(f"[DEBUG] Payload: {json.dumps(payload, ensure_ascii=False)[:500]}...")
            
            response = requests.post(self.IMAGE_EDIT_URL, headers=headers, json=payload, timeout=30)
            
            print(f"[DEBUG] 响应状态码: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            
            print(f"[DEBUG] 响应内容: {json.dumps(result, ensure_ascii=False)[:500]}")
            
            # 异步模式，获取 task_id 并等待结果
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"任务已提交，任务ID: {task_id}")
                return self._wait_for_edit_result(task_id)
            
            # 检查是否有错误
            if "code" in result:
                return {"success": False, "error": f"API错误: {result.get('code')} - {result.get('message', '未知错误')}"}
            
            return {"success": False, "error": f"未知的响应格式: {result}"}
                
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_response = response.json()
                error_detail = f" - 详细错误: {error_response}"
            except:
                error_detail = f" - 响应内容: {response.text[:200]}"
            return {"success": False, "error": f"HTTP错误: {str(e)}{error_detail}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"请求异常: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}
    
    def _wait_for_edit_result(self, task_id, max_retries=60, interval=2):
        """
        等待图像编辑任务完成并获取结果
        
        Args:
            task_id: 任务ID
            max_retries: 最大重试次数
            interval: 检查间隔（秒）
            
        Returns:
            dict: 任务结果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        url = f"{self.TASK_URL}{task_id}"
        
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                if "output" in result:
                    task_status = result["output"].get("task_status")
                    
                    if task_status == "SUCCEEDED":
                        print("\n✅ 图片编辑成功！")
                        # 图像编辑的结果格式与文生图不同
                        if "results" in result["output"]:
                            image_urls = []
                            for item in result["output"]["results"]:
                                if "url" in item:
                                    image_urls.append(item["url"])
                            
                            if image_urls:
                                files = self._download_images(image_urls)
                                return {"success": True, "files": files}
                        return {"success": False, "error": "未获取到编辑后的图片"}
                    elif task_status == "FAILED":
                        error_msg = result["output"].get("message", "未知错误")
                        return {"success": False, "error": f"任务失败: {error_msg}"}
                    elif task_status in ["PENDING", "RUNNING"]:
                        if i % 5 == 0:  # 每5次显示一次进度
                            print(f"  正在编辑中... ({i * interval}秒)")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"  查询状态出错: {str(e)}")
                time.sleep(interval)
        
        return {"success": False, "error": "等待任务完成超时"}
    
    def _download_images(self, image_urls):
        """
        从 URL 下载图片
        
        Args:
            image_urls: 图片 URL 列表
            
        Returns:
            list: 下载的图片文件路径列表
        """
        files = []
        output_dir = "generated_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for i, url in enumerate(image_urls):
            try:
                print(f"  正在下载图片 {i+1}/{len(image_urls)}...")
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                # 生成文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"edited_{timestamp}_{i+1}.png"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                files.append(filepath)
                print(f"  ✅ 已保存: {filepath}")
            except Exception as e:
                print(f"  ❌ 下载图片 {i+1} 失败: {str(e)}")
        
        return files
    
    def _wait_for_result(self, task_id, max_retries=60, interval=2):
        """
        等待任务完成并获取结果
        
        Args:
            task_id: 任务ID
            max_retries: 最大重试次数
            interval: 检查间隔（秒）
            
        Returns:
            dict: 任务结果
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        url = f"{self.TASK_URL}{task_id}"
        
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                
                if "output" in result:
                    task_status = result["output"].get("task_status")
                    
                    if task_status == "SUCCEEDED":
                        print("\n✅ 图片生成成功！")
                        return self._save_images(result["output"])
                    elif task_status == "FAILED":
                        error_msg = result["output"].get("message", "未知错误")
                        return {"success": False, "error": f"任务失败: {error_msg}"}
                    elif task_status in ["PENDING", "RUNNING"]:
                        if i % 5 == 0:  # 每5次显示一次进度
                            print(f"  正在生成中... ({i * interval}秒)")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"  查询状态出错: {str(e)}")
                time.sleep(interval)
        
        return {"success": False, "error": "等待超时，请稍后手动查询任务结果"}
    
    def _save_images(self, output):
        """
        保存生成的图片
        
        Args:
            output: API返回的输出数据
            
        Returns:
            dict: 保存结果
        """
        results = []
        saved_files = []
        
        # 创建输出目录
        output_dir = "generated_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 获取图片数据
        if "results" in output:
            for idx, item in enumerate(output["results"]):
                if "url" in item:
                    # 通过URL下载图片
                    img_url = item["url"]
                    try:
                        img_response = requests.get(img_url, timeout=60)
                        img_response.raise_for_status()
                        
                        # 生成文件名
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{output_dir}/image_{timestamp}_{idx+1}.png"
                        
                        with open(filename, "wb") as f:
                            f.write(img_response.content)
                        
                        saved_files.append(filename)
                        results.append({"url": img_url, "file": filename})
                        print(f"  已保存: {filename}")
                        
                    except Exception as e:
                        print(f"  下载图片失败: {str(e)}")
                        results.append({"url": img_url, "error": str(e)})
        
        return {
            "success": len(saved_files) > 0,
            "files": saved_files,
            "results": results
        }


def interactive_mode():
    """交互式模式"""
    print("=" * 60)
    print("   阿里云百炼文生图工具")
    print("   版本: 1.2.0")
    print("=" * 60)
    
    # 获取API Key
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("\n请输入您的阿里云百炼API Key:")
        print("(获取方式: https://bailian.console.aliyun.com/?apiKey=1)")
        api_key = input("> ").strip()
        if not api_key:
            print("❌ API Key不能为空")
            return
    
    try:
        generator = BailianImageGenerator(api_key)
    except ValueError as e:
        print(f"❌ {e}")
        return
    
    while True:
        print("\n" + "=" * 60)
        print("主菜单:")
        print("  [1] 生成图片（文生图）")
        print("  [2] 编辑图片（图生图）")
        print("  [3] 查看支持的模型")
        print("  [4] 退出")
        print("=" * 60)
        
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            # 生成图片
            print("\n请输入图片描述（提示词）:")
            prompt = input("> ").strip()
            if not prompt:
                print("❌ 提示词不能为空")
                continue
            
            # 选择模型
            generator.list_models()
            model_choice = input("请选择模型 (1-37，默认1): ").strip() or "1"
            model = generator.MODELS.get(model_choice, generator.MODELS["1"])[0]
            
            # 选择尺寸
            print("\n可选尺寸:")
            sizes = ["512*512", "768*768", "1024*1024", "1280*720", "1920*1080"]
            for i, s in enumerate(sizes, 1):
                print(f"  [{i}] {s}")
            size_choice = input("请选择尺寸 (1-5，默认3): ").strip() or "3"
            try:
                size = sizes[int(size_choice) - 1]
            except:
                size = "1024*1024"
            
            # 生成图片
            result = generator.generate_image(prompt, model=model, size=size)
            
            if result["success"]:
                print(f"\n✅ 成功生成 {len(result['files'])} 张图片")
                for f in result["files"]:
                    print(f"   📁 {f}")
            else:
                print(f"\n❌ 生成失败: {result.get('error', '未知错误')}")
        
        elif choice == "2":
            # 编辑图片
            print("\n请输入参考图片路径:")
            image_path = input("> ").strip()
            if not image_path:
                print("❌ 图片路径不能为空")
                continue
            if not os.path.exists(image_path):
                print(f"❌ 图片文件不存在: {image_path}")
                continue
            
            print("\n请输入编辑指令（提示词）:")
            prompt = input("> ").strip()
            if not prompt:
                print("❌ 编辑指令不能为空")
                continue
            
            # 选择编辑模型
            generator.list_edit_models()
            model_choice = input("请选择模型 (1-6，默认2): ").strip() or "2"
            model = generator.EDIT_MODELS.get(model_choice, generator.EDIT_MODELS["2"])[0]
            
            # 选择尺寸
            print("\n可选尺寸:")
            sizes = ["512*512", "768*768", "1024*1024", "1280*720", "1920*1080"]
            for i, s in enumerate(sizes, 1):
                print(f"  [{i}] {s}")
            size_choice = input("请选择尺寸 (1-5，默认3): ").strip() or "3"
            try:
                size = sizes[int(size_choice) - 1]
            except:
                size = "1024*1024"
            
            # 编辑图片
            result = generator.edit_image(prompt, image_path=image_path, model=model, size=size)
            
            if result["success"]:
                print(f"\n✅ 成功编辑图片，生成 {len(result['files'])} 张图片")
                for f in result["files"]:
                    print(f"   📁 {f}")
            else:
                print(f"\n❌ 编辑失败: {result.get('error', '未知错误')}")
        
        elif choice == "3":
            print("\n--- 文生图模型 ---")
            generator.list_models()
            print("\n--- 图像编辑模型 ---")
            generator.list_edit_models()
        
        elif choice == "4":
            print("\n感谢使用，再见！")
            break
        
        else:
            print("❌ 无效的选择，请重新输入")


def quick_generate(prompt, api_key=None, model="wanx-v1", size="1024*1024"):
    """
    快速生成图片（命令行模式）
    
    Args:
        prompt: 图片描述
        api_key: API Key（可选，默认从环境变量读取）
        model: 模型名称
        size: 图片尺寸
    """
    try:
        generator = BailianImageGenerator(api_key)
        result = generator.generate_image(prompt, model=model, size=size)
        
        if result["success"]:
            print(f"\n✅ 图片生成成功！")
            for f in result["files"]:
                print(f"   📁 {f}")
            return True
        else:
            print(f"\n❌ 生成失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 命令行模式
        prompt = " ".join(sys.argv[1:])
        quick_generate(prompt)
    else:
        # 交互式模式
        interactive_mode()
