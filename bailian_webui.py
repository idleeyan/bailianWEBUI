#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图 Web UI
版本: 1.2.0
更新规则: 每次功能更新需递增版本号
"""

import os
import sys

# 修复 Windows 命令行编码问题
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

# 文生图模型选项
MODEL_CHOICES = {
    # 文生图模型
    "通义万相-文生图V1": "wanx-v1",
    "通义万相2.1-Turbo": "wanx2.1-t2i-turbo",
    "通义万相2.1-Plus": "wanx2.1-t2i-plus",
    "通义万相2.6-文生图": "wan2.6-t2i",
    "通义万相2.5-文生图预览": "wan2.5-t2i-preview",
    "通义万相2.2-文生图Plus": "wan2.2-t2i-plus",
    "通义万相2.2-文生图Flash": "wan2.2-t2i-flash",
    "通义万相2.0-Turbo": "wan2.0-t2i-turbo",

    # Qwen图像模型
    "通义千问-图像生成": "qwen-image",
    "通义千问-图像Plus": "qwen-image-plus",
    "通义千问-图像Max": "qwen-image-max",
    "通义千问-图像Turbo": "qwen-image-turbo",
    "通义千问-图像Plus(2026)": "qwen-image-plus-2026-01-09",
    "通义千问-图像Max(2025)": "qwen-image-max-2025-12-30",

    # Flux模型
    "Flux-Schnell": "flux-schnell",
    "Flux-Dev": "flux-dev",
    "Flux-Merged": "flux-merged",

    # 其他图像生成
    "通义万相-草图生图": "wanx-sketch-to-image-lite",
    "通义万相-X绘画": "wanx-x-painting",
    "通义万相-风格重绘": "wanx-style-repaint-v1",
    "通义万相-背景生成V2": "wanx-background-generation-v2",
    "通义万相-海报生成": "wanx-poster-generation-v1",
    "通义万相-虚拟模特": "wanx-virtualmodel",

    # 图像扩展/编辑
    "图像画面扩展": "image-out-painting",
    "通义万相2.1-图像编辑": "wanx2.1-imageedit",
    "通义万相2.1-VACE Plus": "wanx2.1-vace-plus",
    "通义万相2.5-图生图": "wan2.5-i2i-preview",

    # 艺术字
    "艺术字-语义": "wordart-semantic",
    "艺术字-纹理": "wordart-texture",

    # 虚拟试衣
    "虚拟试衣": "aitryon",
    "虚拟试衣Plus": "aitryon-plus",
    "虚拟试衣精修": "aitryon-refiner",
    "虚拟试衣解析": "aitryon-parsing-v1",

    # Emoji
    "Emoji生成": "emoji-v1",
    "Emoji检测": "emoji-detect-v1",

    # 多语言图像
    "通义千问-多语言图像": "qwen-mt-image",
}

# 文生视频模型选项
VIDEO_MODEL_CHOICES = {
    "通义万相2.6-T2V": "wan2.6-t2v",
    "通义万相2.5-T2V预览": "wan2.5-t2v-preview",
    "通义万相2.2-T2V-Plus": "wan2.2-t2v-plus",
    "通义万相2.1-T2V-Plus": "wanx2.1-t2v-plus",
    "通义万相2.1-T2V-Turbo": "wanx2.1-t2v-turbo",
}

# 图像编辑模型选项（需要上传参考图片）
EDIT_MODEL_CHOICES = {
    "通义千问-图像编辑": "qwen-image-edit",
    "通义千问-图像编辑Plus": "qwen-image-edit-plus",
    "通义千问-图像编辑Max": "qwen-image-edit-max",
    "图像编辑Plus(2025-12)": "qwen-image-edit-plus-2025-12-15",
    "图像编辑Plus(2025-10)": "qwen-image-edit-plus-2025-10-30",
    "图像编辑Max(2026)": "qwen-image-edit-max-2026-01-16",
}

# 尺寸选项
SIZE_CHOICES = [
    "512*512",
    "768*768",
    "1024*1024",
    "1280*720",
    "1920*1080",
]

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


def create_ui():
    """创建Gradio界面"""
    
    # Gradio 6.0+ 主题参数移到launch中
    with gr.Blocks(title="阿里云百炼文生图") as demo:

        # 预加载保存的 API Key
        saved_key = load_saved_api_key()

        # 标题
        gr.Markdown(f"""
        # 🎨 阿里云百炼文生图工具

        **版本: {VERSION}** | 支持文生图、文生视频和图像编辑
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
                inbrowser=False,
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
                        inbrowser=False,
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
                            inbrowser=False,
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
