#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图 Web UI
版本: 1.2.0
更新规则: 每次功能更新需递增版本号
"""

import os
import sys
import json

# 修复 Windows 命令行编码问题
# ... (保持原有的编码修复代码)
if sys.platform == 'win32':
    import io
    import ctypes
    # 启用 Windows 控制台 UTF-8 支持
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except:
        pass
    # 重新设置标准输出编码
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 检查 gradio 是否安装
try:
    import gradio as gr
except ImportError:
    print("❌ 请先安装 Gradio: pip install gradio")
    print("\n或者使用以下命令安装所有依赖:")
    print("  pip install requests gradio")
    sys.exit(1)

from bailian_image_gen import BailianImageGenerator

# 版本号
VERSION = "1.2.0"

# 全局生成器实例
generator = None
API_KEY_FILE = "api_key.txt"
MODELS_CONFIG_FILE = "models_config.json"

def load_models_config():
    """加载模型配置"""
    if os.path.exists(MODELS_CONFIG_FILE):
        try:
            with open(MODELS_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    # 默认配置
    default_config = {
        "image": {
            "通义万相-文生图V1": "wanx-v1",
            "通义万相2.6-文生图": "wan2.6-t2i",
            "通义万相2.1-Turbo": "wanx2.1-t2i-turbo",
            "通义千问-图像生成": "qwen-image",
            "Flux-Schnell": "flux-schnell"
        },
        "video": {
            "通义万相2.6-T2V": "wan2.6-t2v",
            "通义万相2.5-T2V预览": "wan2.5-t2v-preview"
        },
        "edit": {
            "通义千问-图像编辑Plus": "qwen-image-edit-plus",
            "通义千问-图像编辑Max": "qwen-image-edit-max"
        },
        "turbo": {
            "Z-IMAGE-turbo 极速生图": "z-image-turbo"
        },
        "i2v": {
            "通义万相2.6-I2V-Flash": "wan2.6-i2v-flash",
            "通义万相2.5-I2V预览": "wan2.5-i2v-preview"
        },
        "kf2v": {
            "通义万相2.2-KF2V-Flash": "wan2.2-kf2v-flash",
            "通义万相2.1-KF2V-Plus": "wanx2.1-kf2v-plus"
        }
    }
    # 保存默认配置
    save_models_config(default_config)
    return default_config

def save_models_config(config):
    """保存模型配置"""
    try:
        with open(MODELS_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"保存模型配置失败: {e}")

# 初始化模型列表
ALL_MODELS = load_models_config()

# 快捷引用字典（修复 NameError）
MODEL_CHOICES = ALL_MODELS["image"]
VIDEO_MODEL_CHOICES = ALL_MODELS["video"]
EDIT_MODEL_CHOICES = ALL_MODELS["edit"]
TURBO_MODEL_CHOICES = ALL_MODELS["turbo"]
I2V_MODEL_CHOICES = ALL_MODELS["i2v"]
KF2V_MODEL_CHOICES = ALL_MODELS["kf2v"]

def update_all_choices():
    """更新全局快捷引用"""
    global MODEL_CHOICES, VIDEO_MODEL_CHOICES, EDIT_MODEL_CHOICES, TURBO_MODEL_CHOICES, I2V_MODEL_CHOICES, KF2V_MODEL_CHOICES
    MODEL_CHOICES = ALL_MODELS["image"]
    VIDEO_MODEL_CHOICES = ALL_MODELS["video"]
    EDIT_MODEL_CHOICES = ALL_MODELS["edit"]
    TURBO_MODEL_CHOICES = ALL_MODELS["turbo"]
    I2V_MODEL_CHOICES = ALL_MODELS["i2v"]
    KF2V_MODEL_CHOICES = ALL_MODELS["kf2v"]

def get_choices(category):
    return list(ALL_MODELS.get(category, {}).keys())

def get_model_id(category, name):
    return ALL_MODELS.get(category, {}).get(name)

# 尺寸选项
SIZE_CHOICES = [
    "512*512",
    "768*768",
    "1024*1024",
    "1280*720",
    "1920*1080",
]

# 极速生图专用尺寸
TURBO_SIZE_CHOICES = [
    "1024*1024",
    "720*1280",
    "1280*720",
]

# 视频分辨率档位
RESOLUTION_CHOICES = ["480P", "720P", "1080P"]

def load_saved_api_key():
    """从本地文件加载保存的 API Key"""
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, "r", encoding="utf-8") as f:
                key = f.read().strip()
                if key:
                    return key
        except:
            pass
    return ""

def save_api_key(api_key):
    """保存 API Key 到本地文件"""
    try:
        with open(API_KEY_FILE, "w", encoding="utf-8") as f:
            f.write(api_key.strip())
    except Exception as e:
        print(f"保存 API Key 失败: {e}")

def init_generator(api_key):
    """初始化生成器"""
    global generator
    try:
        key_to_use = api_key.strip()
        if key_to_use:
            generator = BailianImageGenerator(key_to_use)
            # 保存到环境变量和本地文件
            os.environ["DASHSCOPE_API_KEY"] = key_to_use
            save_api_key(key_to_use)
            return "✅ API Key 设置成功并已保存到本地！", gr.update(visible=False), gr.update(visible=True)
        else:
            # 尝试从环境变量读取
            generator = BailianImageGenerator()
            return "✅ 已从环境变量读取 API Key", gr.update(visible=False), gr.update(visible=True)
    except ValueError as e:
        return f"❌ {str(e)}", gr.update(visible=True), gr.update(visible=False)
    except Exception as e:
        return f"❌ 初始化失败: {str(e)}", gr.update(visible=True), gr.update(visible=False)

def generate_video(prompt, model_name, size, duration, audio_url):
    """生成视频"""
    global generator

    if generator is None:
        return None, "❌ 请先设置 API Key"

    if not prompt.strip():
        return None, "❌ 请输入提示词"

    model = VIDEO_MODEL_CHOICES.get(model_name, "wan2.6-t2v")

    try:
        result = generator.generate_video(
            prompt=prompt.strip(),
            model=model,
            size=size,
            duration=duration,
            audio_url=audio_url if audio_url.strip() else None
        )

        if result["success"]:
            video_path = result["files"][0]
            if os.path.exists(video_path):
                return video_path, f"✅ 视频生成成功！\n\n保存位置: {video_path}"
            else:
                return None, "⚠️ 视频已生成但未能读取文件"
        else:
            return None, f"❌ 生成失败: {result.get('error', '未知错误')}"

    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


def generate_image(prompt, model_name, size, seed=None):
    """生成图片"""
    global generator

    if generator is None:
        return None, "❌ 请先设置 API Key"

    if not prompt.strip():
        return None, "❌ 请输入提示词"

    model = MODEL_CHOICES.get(model_name, "wanx-v1")

    # 处理 seed
    seed_val = None
    if seed is not None and seed != "":
        try:
            seed_val = int(seed)
        except:
            pass

    try:
        result = generator.generate_image(
            prompt=prompt.strip(),
            model=model,
            size=size,
            seed=seed_val
        )

        if result["success"]:
            # 读取生成的图片
            images = []
            for file_path in result["files"]:
                if os.path.exists(file_path):
                    images.append(file_path)

            if images:
                file_list = "\n".join([f"📁 {f}" for f in result["files"]])
                return images, f"✅ 生成成功！\n\n保存位置:\n{file_list}"
            else:
                return None, "⚠️ 图片已生成但未能读取文件"
        else:
            return None, f"❌ 生成失败: {result.get('error', '未知错误')}"

    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


def generate_turbo_image(prompt, model_name, size):
    """极速生成图片 (Z-IMAGE-turbo)"""
    global generator

    if generator is None:
        return None, "❌ 请先设置 API Key"

    if not prompt.strip():
        return None, "❌ 请输入提示词"

    model = TURBO_MODEL_CHOICES.get(model_name, "z-image-turbo")

    try:
        # 极速模型通常不支持 seed
        result = generator.generate_image(
            prompt=prompt.strip(),
            model=model,
            size=size
        )

        if result["success"]:
            images = [f for f in result["files"] if os.path.exists(f)]
            if images:
                file_list = "\n".join([f"📁 {f}" for f in result["files"]])
                return images, f"⚡ 极速生成成功！\n\n保存位置:\n{file_list}"
            else:
                return None, "⚠️ 图片已生成但未能读取文件"
        else:
            return None, f"❌ 生成失败: {result.get('error', '未知错误')}"

    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


def edit_image(prompt, image, model_name, size, seed=None):
    """编辑图片"""
    global generator
    
    if generator is None:
        return None, "❌ 请先设置 API Key"
    
    if not prompt.strip():
        return None, "❌ 请输入编辑指令"
    
    if image is None:
        return None, "❌ 请上传参考图片"
    
    model = EDIT_MODEL_CHOICES.get(model_name, "qwen-image-edit")
    
    # 处理 seed
    seed_val = None
    if seed is not None and seed != "":
        try:
            seed_val = int(seed)
        except:
            pass
    
    try:
        # image 是 Gradio 返回的图片路径
        result = generator.edit_image(
            prompt=prompt.strip(),
            image_path=image,
            model=model,
            size=size,
            seed=seed_val
        )
        
        if result["success"]:
            # 读取生成的图片
            images = []
            for file_path in result["files"]:
                if os.path.exists(file_path):
                    images.append(file_path)
            
            if images:
                file_list = "\n".join([f"📁 {f}" for f in result["files"]])
                return images, f"✅ 编辑成功！\n\n保存位置:\n{file_list}"
            else:
                return None, "⚠️ 图片已编辑但未能读取文件"
        else:
            return None, f"❌ 编辑失败: {result.get('error', '未知错误')}"
            
    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


def generate_i2v(prompt, image, model_name, resolution, duration, audio_url, shot_type, prompt_extend):
    """图生视频"""
    global generator

    if generator is None:
        return None, "❌ 请先设置 API Key"

    if image is None:
        return None, "❌ 请上传首帧图片"

    if not prompt.strip():
        return None, "❌ 请输入动态描述"

    model = I2V_MODEL_CHOICES.get(model_name, "wan2.6-i2v-flash")

    try:
        result = generator.image_to_video(
            prompt=prompt.strip(),
            image_path=image,
            model=model,
            resolution=resolution,
            duration=duration,
            audio_url=audio_url if audio_url.strip() else None,
            shot_type=shot_type,
            prompt_extend=prompt_extend
        )

        if result["success"]:
            video_path = result["files"][0]
            return video_path, f"✅ 图生视频成功！\n\n保存位置: {video_path}"
        else:
            return None, f"❌ 生成失败: {result.get('error', '未知错误')}"

    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


def generate_kf2v(prompt, first_img, last_img, model_name, resolution, prompt_extend, neg_prompt, template):
    """首尾帧生视频 / 视频特效"""
    global generator

    if generator is None:
        return None, "❌ 请先设置 API Key"

    if first_img is None:
        return None, "❌ 请至少上传首帧图片"

    model = KF2V_MODEL_CHOICES.get(model_name, "wan2.2-kf2v-flash")

    try:
        result = generator.frames_to_video(
            prompt=prompt.strip(),
            first_frame=first_img,
            last_frame=last_img if last_img else None,
            model=model,
            resolution=resolution,
            prompt_extend=prompt_extend,
            negative_prompt=neg_prompt.strip() if neg_prompt else None,
            template=template.strip() if template else None
        )

        if result["success"]:
            video_path = result["files"][0]
            return video_path, f"✅ 视频生成成功！\n\n保存位置: {video_path}"
        else:
            return None, f"❌ 生成失败: {result.get('error', '未知错误')}"

    except Exception as e:
        return None, f"❌ 错误: {str(e)}"


def create_ui():
    """创建Gradio界面"""
    
    # Gradio 6.0+ 主题参数移到launch中
    with gr.Blocks(title="阿里云百炼文生图") as demo:

        # 预加载保存的 API Key
        saved_key = load_saved_api_key()

        # 标题
        gr.Markdown(f"""
        # 🎨 阿里云百炼文生图工具

        **版本: {VERSION}** | 支持文生图、极速生图、文生视频、图生视频、首尾帧视频和图像编辑
        """)

        # API Key 设置区域
        with gr.Row() as api_row:
            with gr.Column():
                gr.Markdown("### 🔑 API Key 设置")
                gr.Markdown("请输入您的阿里云百炼 API Key（已自动加载保存的 Key）")
                api_key_input = gr.Textbox(
                    label="API Key",
                    placeholder="sk-xxxxxxxxxxxxxxxx",
                    value=saved_key,
                    type="password",
                    show_label=False
                )
                api_status = gr.Textbox(
                    label="状态",
                    interactive=False,
                    value="等待设置..." if not saved_key else "已读取保存的 Key，请点击“设置”以激活"
                )
                set_api_btn = gr.Button("设置 API Key", variant="primary")

        # 主界面（默认隐藏）- 使用Group替代Column
        with gr.Group(visible=False) as main_ui:
            
            gr.Markdown("---")
            gr.Markdown("""
            ### 🎯 功能选择
            
            本工具支持两种功能，请点击下方选项卡切换：
            """)
            
            # 使用 Tab 组件区分文生图和图像编辑
            with gr.Tabs() as tabs:
                
                # ========== 文生图选项卡 ==========
                with gr.TabItem("📝 文生图"):
                    gr.Markdown("**输入文字描述生成图片**")

                    with gr.Row():
                        with gr.Column(scale=2):
                            prompt_input = gr.Textbox(
                                label="提示词 (Prompt)",
                                placeholder="描述您想要生成的图片，例如：一只穿着宇航服的猫咪在月球上漫步",
                                lines=3,
                                max_lines=5
                            )

                        with gr.Column(scale=1):
                            model_dropdown = gr.Dropdown(
                                label="选择模型",
                                choices=list(MODEL_CHOICES.keys()),
                                value="通义万相-文生图V1"
                            )

                            size_dropdown = gr.Dropdown(
                                label="图片尺寸",
                                choices=SIZE_CHOICES,
                                value="1024*1024"
                            )

                            seed_input = gr.Number(
                                label="随机种子 (可选)",
                                value=None,
                                precision=0,
                                minimum=0,
                                maximum=999999999
                            )

                    generate_btn = gr.Button("🚀 生成图片", variant="primary", size="lg")

                    gr.Markdown("---")
                    gr.Markdown("### 🖼️ 生成结果")

                    with gr.Row():
                        with gr.Column():
                            output_gallery = gr.Gallery(
                                label="生成的图片",
                                show_label=True,
                                elem_id="gallery",
                                columns=2,
                                rows=2,
                                height="auto",
                                object_fit="contain"
                            )

                        with gr.Column():
                            output_status = gr.Textbox(
                                label="状态信息",
                                lines=10,
                                max_lines=15,
                                interactive=False
                            )

                    # 使用说明
                    gr.Markdown("""
                    ---
                    ### 💡 提示词技巧

                    - 使用详细的描述，包含主体、场景、风格、光线等
                    - 可以指定艺术风格，如"油画风格"、"水彩画"、"赛博朋克"等
                    - 支持中英文输入

                    **示例**:
                    - "一只可爱的橘猫坐在窗台上，阳光洒在身上，写实风格"
                    - "未来城市夜景，霓虹灯闪烁，赛博朋克风格，高清细节"
                    """)

                # ========== 极速生图选项卡 (Z-IMAGE-turbo) ==========
                with gr.TabItem("⚡ 极速生图"):
                    gr.Markdown("**亚秒级极速生成，即刻呈现**")

                    with gr.Row():
                        with gr.Column(scale=2):
                            turbo_prompt_input = gr.Textbox(
                                label="提示词 (Prompt)",
                                placeholder="输入您想要生成的画面描述...",
                                lines=3,
                                max_lines=5
                            )

                        with gr.Column(scale=1):
                            turbo_model_dropdown = gr.Dropdown(
                                label="选择模型",
                                choices=list(TURBO_MODEL_CHOICES.keys()),
                                value="Z-IMAGE-turbo 极速生图"
                            )

                            turbo_size_dropdown = gr.Dropdown(
                                label="图片尺寸",
                                choices=TURBO_SIZE_CHOICES,
                                value="1024*1024"
                            )

                    turbo_generate_btn = gr.Button("⚡ 极速生成", variant="primary", size="lg")

                    gr.Markdown("---")
                    gr.Markdown("### 🖼️ 生成结果")

                    with gr.Row():
                        with gr.Column():
                            turbo_output_gallery = gr.Gallery(
                                label="生成的图片",
                                show_label=True,
                                columns=1,
                                height="auto",
                                object_fit="contain"
                            )

                        with gr.Column():
                            turbo_output_status = gr.Textbox(
                                label="状态信息",
                                lines=10,
                                interactive=False
                            )

                    gr.Markdown("""
                    ---
                    ### ⚡ Z-IMAGE-turbo 特点
                    - **极速**: 亚秒级推理，无需长时间等待
                    - **高质量**: 支持 1024*1024 高清输出
                    - **双语**: 完美支持中文和英文指令
                    """)

                # ========== 图生视频选项卡 ==========
                with gr.TabItem("🎬 图生视频"):
                    gr.Markdown("**上传首帧图片并描述动作生成视频**")

                    with gr.Row():
                        with gr.Column(scale=1):
                            i2v_image_input = gr.Image(
                                label="上传首帧图片",
                                type="filepath",
                                height=300
                            )

                        with gr.Column(scale=2):
                            i2v_prompt_input = gr.Textbox(
                                label="动态描述 (Prompt)",
                                placeholder="描述图片中应该发生的动作，例如：人物转头微笑，背景云朵流动",
                                lines=3,
                                max_lines=5
                            )

                            i2v_audio_url = gr.Textbox(
                                label="音频URL (可选自动配音)",
                                placeholder="输入音频URL",
                                lines=1
                            )

                    with gr.Row():
                        with gr.Column():
                            i2v_model_dropdown = gr.Dropdown(
                                label="选择模型",
                                choices=list(I2V_MODEL_CHOICES.keys()),
                                value="通义万相2.6-I2V-Flash"
                            )

                        with gr.Column():
                            i2v_res_dropdown = gr.Dropdown(
                                label="分辨率档位",
                                choices=RESOLUTION_CHOICES,
                                value="720P"
                            )

                        with gr.Column():
                            i2v_duration = gr.Slider(
                                label="视频时长 (秒)",
                                minimum=2,
                                maximum=15,
                                value=5,
                                step=1
                            )

                    with gr.Row():
                        with gr.Column():
                            i2v_shot_type = gr.Radio(
                                label="镜头类型 (仅wan2.6)",
                                choices=["single", "multi"],
                                value="single"
                            )
                        with gr.Column():
                            i2v_extend = gr.Checkbox(
                                label="开启提示词智能改写",
                                value=True
                            )

                    i2v_generate_btn = gr.Button("🚀 生成视频", variant="primary", size="lg")

                    gr.Markdown("---")
                    gr.Markdown("### 🎬 生成结果")

                    with gr.Row():
                        with gr.Column():
                            i2v_video_output = gr.Video(
                                label="生成的视频",
                                show_label=True
                            )

                        with gr.Column():
                            i2v_output_status = gr.Textbox(
                                label="状态信息",
                                lines=10,
                                interactive=False
                            )

                # ========== 首尾帧视频选项卡 ==========
                with gr.TabItem("🎞️ 首尾帧视频"):
                    gr.Markdown("**上传起始和结束图片，生成中间过渡视频**")

                    with gr.Row():
                        with gr.Column():
                            kf2v_first_input = gr.Image(
                                label="上传首帧 (起始)",
                                type="filepath",
                                height=250
                            )
                        with gr.Column():
                            kf2v_last_input = gr.Image(
                                label="上传尾帧 (结束)",
                                type="filepath",
                                height=250
                            )

                    with gr.Row():
                        with gr.Column(scale=2):
                            kf2v_prompt_input = gr.Textbox(
                                label="过渡描述 (Prompt)",
                                placeholder="描述首帧到尾帧之间发生的动作...",
                                lines=3
                            )
                            with gr.Row():
                                kf2v_neg_prompt = gr.Textbox(
                                    label="反向提示词 (Negative)",
                                    placeholder="不希望出现的元素...",
                                    scale=1
                                )
                                kf2v_template = gr.Textbox(
                                    label="特效模板 (Template)",
                                    placeholder="例如: hanfu-1",
                                    scale=1
                                )
                        with gr.Column(scale=1):
                            kf2v_model_dropdown = gr.Dropdown(
                                label="选择模型",
                                choices=list(KF2V_MODEL_CHOICES.keys()),
                                value="通义万相2.2-KF2V-Flash"
                            )
                            kf2v_res_dropdown = gr.Dropdown(
                                label="分辨率档位",
                                choices=RESOLUTION_CHOICES,
                                value="480P"
                            )
                            kf2v_extend = gr.Checkbox(
                                label="开启提示词智能改写",
                                value=True
                            )

                    kf2v_generate_btn = gr.Button("🚀 生成过渡视频", variant="primary", size="lg")

                    gr.Markdown("---")
                    gr.Markdown("### 🎞️ 生成结果")

                    with gr.Row():
                        with gr.Column():
                            kf2v_video_output = gr.Video(
                                label="生成的视频",
                                show_label=True
                            )

                        with gr.Column():
                            kf2v_output_status = gr.Textbox(
                                label="状态信息",
                                lines=10,
                                interactive=False
                            )
                
                # ========== 文生视频选项卡 ==========
                with gr.TabItem("🎥 文生视频"):
                    gr.Markdown("**输入文字描述生成视频**")
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            video_prompt_input = gr.Textbox(
                                label="提示词 (Prompt)",
                                placeholder="描述您想要生成的视频，例如：一只穿着宇航服的猫咪在月球上漫步",
                                lines=3,
                                max_lines=5
                            )
                            
                            audio_url_input = gr.Textbox(
                                label="音频URL (可选)",
                                placeholder="输入音频URL，用于自动配音",
                                lines=1
                            )
                        
                        with gr.Column(scale=1):
                            video_model_dropdown = gr.Dropdown(
                                label="选择模型",
                                choices=list(VIDEO_MODEL_CHOICES.keys()),
                                value="通义万相2.6-T2V"
                            )
                            
                            video_size_dropdown = gr.Dropdown(
                                label="视频尺寸",
                                choices=["832*480", "1280*720", "1920*1080"],
                                value="1280*720"
                            )
                            
                            video_duration_input = gr.Number(
                                label="视频时长 (秒)",
                                value=5,
                                precision=0,
                                minimum=2,
                                maximum=15
                            )
                    
                    generate_video_btn = gr.Button("🚀 生成视频", variant="primary", size="lg")
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🎬 生成结果")
                    
                    with gr.Row():
                        with gr.Column():
                            video_output = gr.Video(
                                label="生成的视频",
                                show_label=True
                            )
                        
                        with gr.Column():
                            video_output_status = gr.Textbox(
                                label="状态信息",
                                lines=10,
                                max_lines=15,
                                interactive=False
                            )
                    
                    # 使用说明
                    gr.Markdown("""
                    ---
                    ### 💡 提示词技巧
                    
                    - 使用详细的描述，包含主体、场景、风格、光线等
                    - 可以指定艺术风格，如"油画风格"、"水彩画"、"赛博朋克"等
                    - 支持中英文输入
                    
                    **示例**: 
                    - "一只可爱的橘猫坐在窗台上，阳光洒在身上，写实风格"
                    - "未来城市夜景，霓虹灯闪烁，赛博朋克风格，高清细节"
                    """)
                
                # ========== 图像编辑选项卡 ==========
                with gr.TabItem("✏️ 图像编辑"):
                    gr.Markdown("**上传图片并进行智能编辑**")
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            edit_image_input = gr.Image(
                                label="上传参考图片",
                                type="filepath",
                                height=300
                            )
                        
                        with gr.Column(scale=2):
                            edit_prompt_input = gr.Textbox(
                                label="编辑指令 (Prompt)",
                                placeholder="描述您想要如何编辑图片，例如：把背景换成海滩，给人物戴上墨镜",
                                lines=3,
                                max_lines=5
                            )
                    
                    with gr.Row():
                        with gr.Column(scale=1):
                            edit_model_dropdown = gr.Dropdown(
                                label="选择编辑模型",
                                choices=list(EDIT_MODEL_CHOICES.keys()),
                                value="通义千问-图像编辑Plus"
                            )
                        
                        with gr.Column(scale=1):
                            edit_size_dropdown = gr.Dropdown(
                                label="输出尺寸",
                                choices=SIZE_CHOICES,
                                value="1024*1024"
                            )
                        
                        with gr.Column(scale=1):
                            edit_seed_input = gr.Number(
                                label="随机种子 (可选)",
                                value=None,
                                precision=0,
                                minimum=0,
                                maximum=999999999
                            )
                    
                    edit_btn = gr.Button("✏️ 编辑图片", variant="primary", size="lg")
                    
                    gr.Markdown("---")
                    gr.Markdown("### 🖼️ 编辑结果")
                    
                    with gr.Row():
                        with gr.Column():
                            edit_output_gallery = gr.Gallery(
                                label="编辑后的图片",
                                show_label=True,
                                elem_id="edit_gallery",
                                columns=2,
                                rows=2,
                                height="auto",
                                object_fit="contain"
                            )
                        
                        with gr.Column():
                            edit_output_status = gr.Textbox(
                                label="状态信息",
                                lines=10,
                                max_lines=15,
                                interactive=False
                            )
                    
                    # 使用说明
                    gr.Markdown("""
                    ---
                    ### 💡 编辑指令技巧

                    - 清晰描述您想要修改的内容
                    - 可以指定添加、删除、修改图像中的元素
                    - 支持风格转换、背景替换、局部修改等

                    **示例**:
                    - "把背景换成星空"
                    - "给人物穿上红色外套"
                    - "将图片转换成油画风格"
                    - "去掉图片中的水印"
                    """)

                # ========== ⚙️ 模型管理选项卡 ==========
                with gr.TabItem("⚙️ 模型管理"):
                    gr.Markdown("### 自定义模型列表管理")

                    with gr.Row():
                        with gr.Column():
                            cat_select = gr.Dropdown(
                                label="模型分类",
                                choices=[
                                    ("📝 文生图", "image"),
                                    ("⚡ 极速生图", "turbo"),
                                    ("🎥 文生视频", "video"),
                                    ("🎬 图生视频", "i2v"),
                                    ("🎞️ 首尾帧视频", "kf2v"),
                                    ("✏️ 图像编辑", "edit")
                                ],
                                value="image"
                            )

                            existing_models = gr.Dropdown(
                                label="现有模型",
                                choices=get_choices("image")
                            )

                            delete_btn = gr.Button("🗑️ 删除选中模型", variant="stop")

                        with gr.Column():
                            new_name = gr.Textbox(label="显示名称 (例如: 通义万相2.6)", placeholder="请输入名称")
                            new_id = gr.Textbox(label="模型 ID (例如: wan2.6-t2i)", placeholder="请输入百炼官方 ID")
                            add_btn = gr.Button("➕ 添加模型", variant="primary")

                    gr.Markdown("---")
                    save_config_btn = gr.Button("💾 保存配置并更新界面", variant="primary", size="lg")
                    manage_status = gr.Textbox(label="操作状态", interactive=False)

            # --- 模型管理内部逻辑 ---
            def on_cat_change(cat):
                return gr.update(choices=get_choices(cat), value=None)

            def on_add_model(cat, name, m_id):
                if not name or not m_id: return gr.update(choices=get_choices(cat)), "❌ 名称和 ID 不能为空"
                ALL_MODELS[cat][name] = m_id
                return gr.update(choices=get_choices(cat), value=name), f"✅ 已添加: {name}"

            def on_del_model(cat, name):
                if not name: return gr.update(choices=get_choices(cat)), "❌ 请先选择要删除的模型"
                if name in ALL_MODELS[cat]:
                    del ALL_MODELS[cat][name]
                return gr.update(choices=get_choices(cat), value=None), f"🗑️ 已删除: {name}"

            def on_save_all():
                save_models_config(ALL_MODELS)
                update_all_choices()
                # 返回所有下拉菜单的更新对象
                return [
                    "✅ 配置已保存，所有界面已刷新！",
                    gr.update(choices=get_choices("image")),
                    gr.update(choices=get_choices("turbo")),
                    gr.update(choices=get_choices("video")),
                    gr.update(choices=get_choices("i2v")),
                    gr.update(choices=get_choices("kf2v")),
                    gr.update(choices=get_choices("edit"))
                ]

            cat_select.change(on_cat_change, inputs=[cat_select], outputs=[existing_models])
            add_btn.click(on_add_model, inputs=[cat_select, new_name, new_id], outputs=[existing_models, manage_status])
            delete_btn.click(on_del_model, inputs=[cat_select, existing_models], outputs=[existing_models, manage_status])

            # 保存按钮触发全站刷新
            save_config_btn.click(
                on_save_all,
                outputs=[
                    manage_status, model_dropdown, turbo_model_dropdown,
                    video_model_dropdown, i2v_model_dropdown, kf2v_model_dropdown, edit_model_dropdown
                ]
            )

        # 事件绑定
        set_api_btn.click(
            fn=init_generator,
            inputs=[api_key_input],
            outputs=[api_status, api_row, main_ui]
        )
        
        # 文生图事件绑定
        generate_btn.click(
            fn=generate_image,
            inputs=[prompt_input, model_dropdown, size_dropdown, seed_input],
            outputs=[output_gallery, output_status]
        )
        
        # 图像编辑事件绑定
        edit_btn.click(
            fn=edit_image,
            inputs=[edit_prompt_input, edit_image_input, edit_model_dropdown, edit_size_dropdown, edit_seed_input],
            outputs=[edit_output_gallery, edit_output_status]
        )

        # 文生视频事件绑定
        generate_video_btn.click(
            fn=generate_video,
            inputs=[video_prompt_input, video_model_dropdown, video_size_dropdown, video_duration_input, audio_url_input],
            outputs=[video_output, video_output_status]
        )

        # 极速生图事件绑定
        turbo_generate_btn.click(
            fn=generate_turbo_image,
            inputs=[turbo_prompt_input, turbo_model_dropdown, turbo_size_dropdown],
            outputs=[turbo_output_gallery, turbo_output_status]
        )

        # 图生视频事件绑定
        i2v_generate_btn.click(
            fn=generate_i2v,
            inputs=[
                i2v_prompt_input, i2v_image_input, i2v_model_dropdown,
                i2v_res_dropdown, i2v_duration, i2v_audio_url,
                i2v_shot_type, i2v_extend
            ],
            outputs=[i2v_video_output, i2v_output_status]
        )

        # 首尾帧视频事件绑定
        kf2v_generate_btn.click(
            fn=generate_kf2v,
            inputs=[
                kf2v_prompt_input, kf2v_first_input, kf2v_last_input,
                kf2v_model_dropdown, kf2v_res_dropdown, kf2v_extend,
                kf2v_neg_prompt, kf2v_template
            ],
            outputs=[kf2v_video_output, kf2v_output_status]
        )

    return demo


def main():
    """主函数"""
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     阿里云百炼文生图 Web UI                              ║
    ║     版本: {VERSION}                                         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"✅ Gradio 版本: {gr.__version__}")
    
    # 创建并启动界面
    demo = create_ui()
    
    print("\n🚀 正在启动 Web UI...")
    print("📱 启动后会自动打开浏览器")
    print("⏹️  按 Ctrl+C 停止服务\n")
    
    # 尝试启动，如果7860端口被占用则尝试其他端口
    ports = [7860, 7861, 7862, 7863, 7864, 7870, 7880, 8000, 8080, 8090, 9000]
    
    for port in ports:
        try:
            print(f"  尝试端口: {port}...")
            
            # 设置环境变量禁用Gradio的telemetry和外部连接
            os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'
            os.environ['GRADIO_TELEMETRY_ENABLED'] = 'False'
            
            demo.launch(
                share=False,
                inbrowser=True,
                server_name="127.0.0.1",
                server_port=port,
                show_error=True,
                quiet=False,
                prevent_thread_lock=False
            )
            print(f"\n✅ Web UI 启动成功！")
            print(f"🌐 请访问: http://127.0.0.1:{port}")
            print("⏹️  按 Ctrl+C 停止服务\n")
            break
        except OSError as e:
            if "Port" in str(e) or "already in use" in str(e).lower() or "10048" in str(e):
                print(f"  端口 {port} 被占用，尝试下一个...")
                continue
            else:
                print(f"  端口 {port} 启动失败: {e}")
                continue
        except Exception as e:
            error_msg = str(e)
            print(f"  端口 {port} 错误: {error_msg}")
            if "localhost is not accessible" in error_msg.lower() or "shareable link" in error_msg.lower():
                print(f"\n⚠️  尝试共享链接模式...")
                try:
                    demo.launch(
                        share=True,
                        inbrowser=True,
                        server_name="127.0.0.1",
                        server_port=port,
                        show_error=True,
                        quiet=True
                    )
                    break
                except Exception as e2:
                    print(f"❌ 共享模式也失败了: {e2}")
                    print("\n⚠️  共享链接功能不可用，但本地访问应该可以工作")
                    print("\n建议解决方案:")
                    print("  1. 直接访问本地地址: http://127.0.0.1:7860")
                    print("  2. 如果浏览器无法访问，尝试使用不同浏览器")
                    print("  3. 检查Windows防火墙设置")
                    print("  4. 使用命令行模式: python bailian_image_gen.py")
                    
                    # 尝试不使用share参数启动
                    try:
                        print("\n🔄 尝试使用基本本地模式启动...")
                        # 重新创建demo实例以避免状态问题
                        demo_local = create_ui()
                        demo_local.launch(
                            share=False,
                            inbrowser=True,
                            server_name="0.0.0.0",
                            server_port=port,
                            show_error=True,
                            quiet=True
                        )
                        print(f"\n✅ Web UI 启动成功！")
                        print(f"🌐 本地访问: http://127.0.0.1:{port}")
                        print(f"🌐 网络访问: http://本机IP:{port} (如果在同一网络)")
                        print("⏹️  按 Ctrl+C 停止服务\n")
                    except Exception as e3:
                        print(f"\n❌ 本地模式也失败: {e3}")
                        print("\n最终建议:")
                        print("  1. 使用命令行模式: python bailian_image_gen.py")
                        print("  2. 检查Python和Gradio安装")
                        print("  3. 重启电脑后重试")
                        sys.exit(1)
            elif port == ports[-1]:
                print(f"\n❌ 无法启动Web UI: {e}")
                print("\n建议:")
                print("  1. 检查是否有其他程序占用了端口")
                print("  2. 检查防火墙设置")
                print("  3. 尝试重启电脑后再次运行")
                print("  4. 使用命令行模式: python bailian_image_gen.py")
                sys.exit(1)
            else:
                continue


if __name__ == "__main__":
    main()
