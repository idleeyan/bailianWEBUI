#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图简易调用程序
版本: 1.2.3
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
    # 首尾帧生视频 API
    KF2V_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
    # 文生视频 API
    VIDEO_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
    # 千问图像编辑 API（多模态生成）
    MULTIModal_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    TASK_URL = "https://dashscope.aliyuncs.com/api/v1/tasks/"

    # 文生图模型列表
    MODELS = {
        "1": ("wan2.6-t2i", "通义万相2.6-文生图"),
        "2": ("wan2.5-t2i-preview", "通义万相2.5-文生图预览"),
        "3": ("wan2.2-t2i-plus", "通义万相2.2-文生图Plus"),
        "4": ("wan2.2-t2i-flash", "通义万相2.2-文生图Flash"),
        "5": ("wanx2.1-t2i-turbo", "通义万相2.1-Turbo"),
        "6": ("wanx2.1-t2i-plus", "通义万相2.1-Plus"),
        "7": ("wanx-v1", "通义万相-文生图V1"),
        "8": ("wan2.0-t2i-turbo", "通义万相2.0-Turbo"),
        "9": ("wanx2.0-t2i-turbo", "通义万相2.0-Turbo"),
        "10": ("qwen-image", "通义千问-图像"),
        "11": ("qwen-image-plus", "通义千问-图像Plus"),
        "12": ("qwen-image-max", "通义千问-图像Max"),
        "13": ("qwen-image-turbo", "通义千问-图像Turbo"),
        "14": ("qwen-image-plus-2026-01-09", "通义千问-图像Plus(2026)"),
        "15": ("qwen-image-max-2025-12-30", "通义千问-图像Max(2025)"),
        "16": ("flux-schnell", "Flux-Schnell"),
        "17": ("flux-dev", "Flux-Dev"),
        "18": ("flux-merged", "Flux-Merged"),
        "19": ("wan2.6-i2v-flash", "通义万相2.6-I2V-Flash"),
        "20": ("wan2.6-i2v", "通义万相2.6-I2V"),
        "21": ("wan2.5-i2v-preview", "通义万相2.5-I2V预览"),
        "22": ("z-image-turbo", "Z-Image-Turbo"),
        "23": ("wan2.2-i2v-plus", "通义万相2.2-I2V-Plus"),
        "24": ("qwen-mt-image", "通义千问-多语言图像"),
        "25": ("wan2.5-t2i-preview", "通义万相2.5-T2I预览"),
        "26": ("wan2.2-kf2v-flash", "通义万相2.2-KF2V-Flash"),
        "27": ("wan2.2-animate-mix", "通义万相2.2-Animate-Mix"),
        "28": ("wan2.2-animate-move", "通义万相2.2-Animate-Move"),
        "29": ("wan2.6-image", "通义万相2.6-图像"),
        "30": ("wan2.2-s2v", "通义万相2.2-S2V"),
        "31": ("wan2.2-s2v-detect", "通义万相2.2-S2V-Detect"),
        "32": ("wan2.2-i2v-flash", "通义万相2.2-I2V-Flash"),
        "33": ("wan2.5-i2i-preview", "通义万相2.5-I2I预览"),
        "34": ("wan2.2-t2i-plus", "通义万相2.2-文生图Plus"),
        "35": ("wan2.2-t2i-flash", "通义万相2.2-文生图Flash"),
        "36": ("wanx2.1-kf2v-plus", "通义万相2.1-KF2V-Plus"),
        "37": ("wan2.6-r2v-flash", "通义万相2.6-R2V-Flash"),
        "38": ("wan2.6-r2v", "通义万相2.6-R2V"),
        "39": ("wanx2.1-i2v-plus", "通义万相2.1-I2V-Plus"),
        "40": ("wanx2.1-t2i-plus", "通义万相2.1-T2I-Plus"),
        "41": ("wanx2.1-t2i-turbo", "通义万相2.1-T2I-Turbo"),
        "42": ("aitryon-plus", "虚拟试衣Plus"),
        "43": ("aitryon", "虚拟试衣"),
        "44": ("wanx2.1-i2v-turbo", "通义万相2.1-I2V-Turbo"),
        "45": ("aitryon-parsing-v1", "虚拟试衣解析"),
        "46": ("emoji-v1", "Emoji生成"),
        "47": ("emoji-detect-v1", "Emoji检测"),
        "48": ("animate-anyone-gen2", "Animate-Anyone-Gen2"),
        "49": ("animate-anyone-template-gen2", "Animate-Anyone-Template"),
        "50": ("animate-anyone-detect-gen2", "Animate-Anyone-Detect"),
        "51": ("videoretalk", "VideoRetalk"),
        "52": ("emo-v1", "EMO-V1"),
        "53": ("video-style-transform", "视频风格转换"),
        "54": ("emo-detect-v1", "EMO-Detect"),
        "55": ("liveportrait", "LivePortrait"),
        "56": ("liveportrait-detect", "LivePortrait-Detect"),
        "57": ("wanx2.1-vace-plus", "通义万相2.1-VACE Plus"),
        "58": ("aitryon-refiner", "虚拟试衣精修"),
        "59": ("wanx-virtualmodel", "通义万相-虚拟模特"),
        "60": ("wanx-poster-generation-v1", "通义万相-海报生成"),
        "61": ("wanx-sketch-to-image-lite", "通义万相-草图生图"),
        "62": ("wanx-x-painting", "通义万相-X绘画"),
        "63": ("image-out-painting", "图像画面扩展"),
        "64": ("wordart-semantic", "艺术字-语义"),
        "65": ("wordart-texture", "艺术字-纹理"),
        "66": ("wanx-background-generation-v2", "通义万相-背景生成V2"),
        "67": ("wanx-style-repaint-v1", "通义万相-风格重绘"),
    }
    
    # 文生视频模型列表
    VIDEO_MODELS = {
        "1": ("wan2.6-t2v", "通义万相2.6-T2V"),
        "2": ("wan2.5-t2v-preview", "通义万相2.5-T2V预览"),
        "3": ("wan2.2-t2v-plus", "通义万相2.2-T2V-Plus"),
        "4": ("wanx2.1-t2v-plus", "通义万相2.1-T2V-Plus"),
        "5": ("wanx2.1-t2v-turbo", "通义万相2.1-T2V-Turbo"),
    }

    # 图像编辑模型列表（带有edit标识）
    EDIT_MODELS = {
        "1": ("qwen-image-edit-plus", "通义千问-图像编辑Plus"),
        "2": ("qwen-image-edit", "通义千问-图像编辑"),
        "3": ("qwen-image-edit-plus-2025-12-15", "图像编辑Plus(2025-12)"),
        "4": ("qwen-image-edit-plus-2025-10-30", "图像编辑Plus(2025-10)"),
        "5": ("qwen-image-edit-max-2026-01-16", "图像编辑Max(2026)"),
        "6": ("qwen-image-edit-max", "通义千问-图像编辑Max"),
        "7": ("wanx2.1-imageedit", "通义万相2.1-图像编辑"),
    }

    # 图片翻译模型列表
    TRANSLATE_MODELS = {
        "1": ("qwen-mt-image", "通义千问-多语言图像翻译"),
    }

    def translate_image(self, image_path, target_lang="zh", model="qwen-mt-image"):
        """
        图片翻译
        参考文档: https://help.aliyun.com/zh/model-studio/developer-reference/image-translation-api-details

        Args:
            image_path: 待翻译图片路径
            target_lang: 目标语言 (例如: zh, en, ja, ko)
            model: 模型名称，默认 qwen-mt-image
        """
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return {"success": False, "error": f"读取图片失败: {str(e)}"}

        ext = image_path.lower().split('.')[-1] if '.' in image_path else 'png'
        mime_type = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext, 'image/png')

        # 构造翻译 API 请求
        # 注意：图片翻译 API 结构与文生图略有不同
        payload = {
            "model": model,
            "input": {
                "image_url": f"data:{mime_type};base64,{image_data}"
            },
            "parameters": {
                "translation": {
                    "target_language": target_lang
                }
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }

        print(f"\n正在提交图片翻译任务...")
        try:
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"翻译任务已提交，任务ID: {task_id}")
                return self._wait_for_result(task_id) # 复用已有的等待逻辑
            return {"success": False, "error": f"提交任务失败: {result}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}

    def generate_video(self, prompt, model="wan2.6-t2v", size="1280*720", duration=5, audio_url=None, negative_prompt=None):
        """
        生成视频
        参考文档: 文生视频构建说明.txt
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": size
            }
        }

        if audio_url:
            payload["input"]["audio_url"] = audio_url

        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt

        # 根据模型限制时长
        if model == "wan2.6-t2v":
            payload["parameters"]["duration"] = max(2, min(15, int(duration)))
        elif model in ["wan2.5-t2v-preview"]:
            payload["parameters"]["duration"] = 10 if int(duration) >= 10 else 5

        # 某些模型支持 prompt_extend
        if "wan" in model:
            payload["parameters"]["prompt_extend"] = True

        print(f"\n正在提交文生视频任务 (异步)...")
        print(f"模型: {model}")
        print(f"提示词: {prompt}")

        try:
            response = requests.post(self.VIDEO_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"视频任务已提交，任务ID: {task_id}")
                return self._wait_for_video_result(task_id)
            else:
                return {"success": False, "error": f"提交任务失败: {result}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}

    def image_to_video(self, prompt, image_path, model="wan2.6-i2v-flash", resolution="720P", duration=5, audio_url=None, negative_prompt=None, shot_type="single", prompt_extend=True):
        """
        图生视频
        参考文档: 图生视频构建说明.txt
        """
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return {"success": False, "error": f"读取图片失败: {str(e)}"}

        ext = image_path.lower().split('.')[-1] if '.' in image_path else 'png'
        mime_type = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext, 'image/png')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": model,
            "input": {
                "prompt": prompt,
                "img_url": f"data:{mime_type};base64,{image_data}"
            },
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend
            }
        }

        if audio_url:
            payload["input"]["audio_url"] = audio_url
        if negative_prompt:
            payload["input"]["negative_prompt"] = negative_prompt

        # 处理 wan2.6 的镜头类型
        if "wan2.6" in model:
            payload["parameters"]["shot_type"] = shot_type

        # 根据模型限制时长
        if model in ["wan2.6-i2v-flash", "wan2.6-i2v"]:
            payload["parameters"]["duration"] = max(2, min(15, int(duration)))
        elif model in ["wan2.5-i2v-preview"]:
            payload["parameters"]["duration"] = 10 if int(duration) >= 10 else 5
        elif model == "wanx2.1-i2v-turbo":
            payload["parameters"]["duration"] = max(3, min(5, int(duration)))

        print(f"\n正在提交图生视频任务 (异步)...")
        try:
            response = requests.post(self.VIDEO_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            if "output" in result and "task_id" in result["output"]:
                return self._wait_for_video_result(result["output"]["task_id"])
            return {"success": False, "error": f"提交失败: {result}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}

    def frames_to_video(self, prompt, first_frame, last_frame=None, model="wan2.2-kf2v-flash", resolution="480P", prompt_extend=True, negative_prompt=None, template=None):
        """
        首尾帧生视频 / 视频特效
        """
        def get_b64(path):
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
                ext = path.lower().split('.')[-1] if '.' in path else 'png'
                mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png'}.get(ext, 'image/png')
                return f"data:{mime};base64,{data}"

        try:
            first_b64 = get_b64(first_frame)
            last_b64 = get_b64(last_frame) if last_frame else None
        except Exception as e:
            return {"success": False, "error": f"读取图片失败: {str(e)}"}

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-DashScope-Async": "enable"
        }

        payload = {
            "model": model,
            "input": {
                "first_frame_url": first_b64
            },
            "parameters": {
                "resolution": resolution,
                "prompt_extend": prompt_extend
            }
        }

        # 根据模式填充 input
        if template:
            payload["input"]["template"] = template
        else:
            if last_b64:
                payload["input"]["last_frame_url"] = last_b64
            if prompt:
                payload["input"]["prompt"] = prompt
            if negative_prompt:
                payload["input"]["negative_prompt"] = negative_prompt

        print(f"\n正在提交首尾帧/特效视频任务 (异步)...")
        try:
            response = requests.post(self.KF2V_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            if "output" in result and "task_id" in result["output"]:
                return self._wait_for_video_result(result["output"]["task_id"])
            return {"success": False, "error": f"提交失败: {result}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}

    def _wait_for_video_result(self, task_id, max_retries=300, interval=5):
        """等待视频生成结果，视频生成较慢，增加超时时间"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.TASK_URL}{task_id}"

        output_dir = "generated_videos"
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        print("等待视频生成中，请稍候...")
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                if "output" in result:
                    task_status = result["output"].get("task_status")
                    if task_status == "SUCCEEDED":
                        video_url = result["output"].get("video_url")
                        if video_url:
                            try:
                                print(f"视频生成成功，正在下载: {video_url}")
                                v_res = requests.get(video_url, timeout=120)
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filepath = os.path.join(output_dir, f"video_{timestamp}.mp4")
                                with open(filepath, "wb") as f: f.write(v_res.content)
                                return {"success": True, "files": [filepath]}
                            except Exception as e:
                                return {"success": False, "error": f"下载视频失败: {str(e)}", "url": video_url}
                        return {"success": False, "error": "未获取到视频URL"}
                    elif task_status == "FAILED":
                        return {"success": False, "error": result["output"].get("message", "未知错误")}

                    if i % 2 == 0:
                        progress = result["output"].get("task_progress", 0)
                        print(f"生成进度: {progress}%")

                time.sleep(interval)
            except Exception as e:
                print(f"轮询状态出错: {e}")
                time.sleep(interval)
        return {"success": False, "error": "等待视频生成超时"}

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
        # 按编号数字排序
        sorted_keys = sorted(self.MODELS.keys(), key=lambda x: int(x))
        for key in sorted_keys:
            model_id, desc = self.MODELS[key]
            print(f"  [{key}] {model_id} - {desc}")
        print("-" * 50)

    def list_edit_models(self):
        """显示可用的图像编辑模型列表"""
        print("\n可用的图像编辑模型列表:")
        print("-" * 50)
        sorted_keys = sorted(self.EDIT_MODELS.keys(), key=lambda x: int(x))
        for key in sorted_keys:
            model_id, desc = self.EDIT_MODELS[key]
            print(f"  [{key}] {model_id} - {desc}")
        print("-" * 50)

    def generate_image(self, prompt, model="wanx-v1", size="1024*1024", n=1, seed=None):
        """生成图片"""
        # z-image-turbo 使用多模态生成接口，逻辑略有不同
        if model == "z-image-turbo":
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                },
                "parameters": {
                    "prompt_extend": False,
                    "size": size
                }
            }
            url = self.MULTIModal_URL
            print(f"\n正在调用极速生图 (z-image-turbo)...环境: 同步")
        else:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-DashScope-Async": "enable"
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
            url = self.API_URL
            print(f"\n正在提交文生图任务 (异步)...")

        print(f"模型: {model}")
        print(f"提示词: {prompt}")

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            # 处理极速版同步结果
            if model == "z-image-turbo":
                if "output" in result and "choices" in result["output"]:
                    # 适配新的返回格式
                    output_data = {
                        "results": []
                    }
                    for choice in result["output"]["choices"]:
                        if "message" in choice and "content" in choice["message"]:
                            for content in choice["message"]["content"]:
                                if "image" in content:
                                    output_data["results"].append({
                                        "url": content["image"].strip()
                                    })
                    return self._save_images(output_data)
                return {"success": False, "error": f"同步生成失败: {result}"}

            # 处理标准版异步结果
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"任务已提交，任务ID: {task_id}")
                return self._wait_for_result(task_id)
            else:
                return {"success": False, "error": f"提交任务失败: {result}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}

    def edit_image(self, prompt, image_path, model="wanx2.1-imageedit", size="1024*1024", n=1, seed=None, edit_function="description_edit"):
        """编辑图片（图生图）"""
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            return {"success": False, "error": f"读取图片失败: {str(e)}"}

        ext = image_path.lower().split('.')[-1] if '.' in image_path else 'png'
        mime_type = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'gif': 'image/gif', 'webp': 'image/webp'
        }.get(ext, 'image/png')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            # 处理新版 multimodal 模型
            if model.startswith("qwen-image-edit"):
                # 使用 multimodal API 端点
                url = self.MULTIModal_URL
                payload = {
                    "model": model,
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "image": f"data:{mime_type};base64,{image_data}"
                                    },
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ]
                    },
                    "parameters": {
                        "n": n,
                        "size": size,
                        "prompt_extend": True,
                        "watermark": False
                    }
                }
                print(f"使用 multimodal API 调用新版编辑模型...")
                response = requests.post(url, headers=headers, json=payload, timeout=30)
            else:
                # 旧版模型使用原 API
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
                if seed is not None:
                    payload["parameters"]["seed"] = seed

                if edit_function in ["description_edit", "stylization_all"]:
                    payload["parameters"]["strength"] = 0.5

                headers["X-DashScope-Async"] = "enable"
                response = requests.post(self.IMAGE_EDIT_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                return self._wait_for_edit_result(task_id)
            elif "output" in result and "choices" in result["output"]:
                # 处理新版 multimodal 同步结果
                output_data = {
                    "results": []
                }
                for choice in result["output"]["choices"]:
                    if "message" in choice and "content" in choice["message"]:
                        for content in choice["message"]["content"]:
                            if "image" in content:
                                output_data["results"].append({
                                    "url": content["image"].strip()
                                })
                return self._save_images(output_data)
            return {"success": False, "error": f"未知的响应格式: {result}"}
        except Exception as e:
            return {"success": False, "error": f"异常: {str(e)}"}

    def _wait_for_edit_result(self, task_id, max_retries=60, interval=2):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.TASK_URL}{task_id}"

        for i in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                if "output" in result:
                    task_status = result["output"].get("task_status")
                    if task_status == "SUCCEEDED":
                        if "results" in result["output"]:
                            image_urls = [item["url"] for item in result["output"]["results"] if "url" in item]
                            if image_urls:
                                files = self._download_images(image_urls)
                                return {"success": True, "files": files}
                        return {"success": False, "error": "未获取到编辑后的图片"}
                    elif task_status == "FAILED":
                        return {"success": False, "error": result["output"].get("message", "未知错误")}
                time.sleep(interval)
            except:
                time.sleep(interval)
        return {"success": False, "error": "等待任务完成超时"}

    def _download_images(self, image_urls):
        files = []
        output_dir = "generated_images"
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        for i, url in enumerate(image_urls):
            try:
                response = requests.get(url, timeout=60)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = os.path.join(output_dir, f"edited_{timestamp}_{i+1}.png")
                with open(filepath, "wb") as f: f.write(response.content)
                files.append(filepath)
            except: pass
        return files

    def _wait_for_result(self, task_id, max_retries=60, interval=2):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = f"{self.TASK_URL}{task_id}"
        for i in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                result = response.json()
                if "output" in result:
                    task_status = result["output"].get("task_status")
                    if task_status == "SUCCEEDED":
                        return self._save_images(result["output"])
                    elif task_status == "FAILED":
                        return {"success": False, "error": result["output"].get("message", "未知错误")}
                time.sleep(interval)
            except:
                time.sleep(interval)
        return {"success": False, "error": "等待超时"}

    def _save_images(self, output):
        saved_files = []
        output_dir = "generated_images"
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        if "results" in output:
            for idx, item in enumerate(output["results"]):
                if "url" in item:
                    try:
                        img_response = requests.get(item["url"], timeout=60)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{output_dir}/image_{timestamp}_{idx+1}.png"
                        with open(filename, "wb") as f: f.write(img_response.content)
                        saved_files.append(filename)
                    except: pass
        return {"success": len(saved_files) > 0, "files": saved_files}


def interactive_mode():
    print("=" * 60)
    print("   阿里云百炼文生图工具")
    print("=" * 60)
    api_key = os.environ.get("DASHSCOPE_API_KEY") or input("\n请输入您的 API Key: ").strip()
    if not api_key: return
    try:
        generator = BailianImageGenerator(api_key)
    except Exception as e:
        print(f"❌ {e}")
        return

    while True:
        print("\n[1] 生成图片 [2] 编辑图片 [3] 查看模型 [4] 退出")
        choice = input("选择: ").strip()
        if choice == "1":
            prompt = input("提示词: ").strip()
            generator.list_models()
            m = input("模型编号: ").strip() or "1"
            model = generator.MODELS.get(m, generator.MODELS["1"])[0]
            result = generator.generate_image(prompt, model=model)
            if result["success"]: print(f"✅ 已保存: {result['files']}")
        elif choice == "2":
            path = input("图片路径: ").strip()
            prompt = input("编辑指令: ").strip()
            generator.list_edit_models()
            m = input("模型编号: ").strip() or "1"
            model = generator.EDIT_MODELS.get(m, generator.EDIT_MODELS["1"])[0]
            result = generator.edit_image(prompt, image_path=path, model=model)
            if result["success"]: print(f"✅ 已保存: {result['files']}")
        elif choice == "3":
            generator.list_models()
            generator.list_edit_models()
        elif choice == "4": break

if __name__ == "__main__":
    interactive_mode()
