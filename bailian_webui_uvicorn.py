#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼文生图 Web UI - Uvicorn版本
绕过Gradio的连接验证问题
"""
import os
import sys
import time
import webbrowser
import threading

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# Check dependencies
try:
    import gradio as gr
except ImportError:
    print("[ERROR] Gradio not installed!")
    print("[INFO] Run: pip install gradio requests uvicorn")
    input("Press Enter to exit...")
    sys.exit(1)

try:
    import uvicorn
except ImportError:
    print("[ERROR] Uvicorn not installed!")
    print("[INFO] Run: pip install uvicorn")
    input("Press Enter to exit...")
    sys.exit(1)

from bailian_image_gen import BailianImageGenerator

VERSION = "1.1.0"
generator = None

MODEL_CHOICES = {
    "wanx-v1": "wanx-v1",
    "wanx2.1-t2i-turbo": "wanx2.1-t2i-turbo",
    "wanx2.1-t2i-plus": "wanx2.1-t2i-plus",
    "qwen-image": "qwen-image",
    "flux-schnell": "flux-schnell",
}

SIZE_CHOICES = ["512*512", "768*768", "1024*1024", "1280*720", "1920*1080"]

def init_generator(api_key):
    global generator
    try:
        if api_key.strip():
            generator = BailianImageGenerator(api_key.strip())
            return "API Key set successfully!", gr.update(visible=False), gr.update(visible=True)
        else:
            generator = BailianImageGenerator()
            return "API Key loaded from environment!", gr.update(visible=False), gr.update(visible=True)
    except Exception as e:
        return f"Error: {str(e)}", gr.update(visible=True), gr.update(visible=False)

def generate_image(prompt, model_name, size, seed=None):
    global generator
    if generator is None:
        return None, "Error: Please set API Key first"
    if not prompt.strip():
        return None, "Error: Please enter prompt"
    
    model = MODEL_CHOICES.get(model_name, "wanx-v1")
    seed_val = int(seed) if seed and str(seed).strip() else None
    
    try:
        result = generator.generate_image(
            prompt=prompt.strip(),
            model=model,
            size=size,
            seed=seed_val
        )
        
        if result["success"]:
            images = [f for f in result["files"] if os.path.exists(f)]
            if images:
                return images, f"Success!\nSaved to:\n" + "\n".join(result["files"])
            return None, "Warning: Images generated but files not found"
        else:
            return None, f"Error: {result.get('error', 'Unknown error')}"
    except Exception as e:
        return None, f"Error: {str(e)}"

def create_ui():
    with gr.Blocks(title="Aliyun Bailian Image Gen") as demo:
        gr.Markdown(f"""
        # Image Generation Tool
        **Version: {VERSION}** | Powered by Aliyun Bailian
        """)
        
        with gr.Row() as api_row:
            with gr.Column():
                gr.Markdown("### API Key Setup")
                api_key_input = gr.Textbox(
                    label="API Key",
                    placeholder="sk-xxxxxxxxxxxxxxxx",
                    type="password"
                )
                api_status = gr.Textbox(label="Status", value="Waiting...", interactive=False)
                set_api_btn = gr.Button("Set API Key", variant="primary")
        
        with gr.Column(visible=False) as main_ui:
            gr.Markdown("---")
            gr.Markdown("### Generation Settings")
            
            with gr.Row():
                with gr.Column(scale=2):
                    prompt_input = gr.Textbox(
                        label="Prompt",
                        placeholder="Describe the image you want to generate...",
                        lines=3
                    )
                
                with gr.Column(scale=1):
                    model_dropdown = gr.Dropdown(
                        label="Model",
                        choices=list(MODEL_CHOICES.keys()),
                        value="wanx-v1"
                    )
                    size_dropdown = gr.Dropdown(
                        label="Size",
                        choices=SIZE_CHOICES,
                        value="1024*1024"
                    )
                    seed_input = gr.Number(label="Seed (optional)", value=None, precision=0)
            
            generate_btn = gr.Button("Generate Image", variant="primary")
            
            gr.Markdown("---")
            gr.Markdown("### Results")
            
            with gr.Row():
                output_gallery = gr.Gallery(label="Generated Images", columns=2, height="auto")
                output_status = gr.Textbox(label="Status", lines=5, interactive=False)
        
        set_api_btn.click(
            fn=init_generator,
            inputs=[api_key_input],
            outputs=[api_status, api_row, main_ui]
        )
        
        generate_btn.click(
            fn=generate_image,
            inputs=[prompt_input, model_dropdown, size_dropdown, seed_input],
            outputs=[output_gallery, output_status]
        )
    
    return demo

def check_port(port):
    """Check if port is available"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except:
        return False

def main():
    print("=" * 50)
    print("   Aliyun Bailian Image Gen Web UI")
    print(f"   Version: {VERSION}")
    print("=" * 50)
    print()
    print(f"[INFO] Gradio version: {gr.__version__}")
    print()
    
    # Find available port
    ports = [7860, 7861, 7862, 7870, 7880, 8000, 8080]
    port = None
    for p in ports:
        if check_port(p):
            port = p
            break
    
    if port is None:
        print("[ERROR] All ports occupied!")
        input("Press Enter to exit...")
        return
    
    print(f"[INFO] Starting server on port {port}...")
    print()
    
    # Create UI
    demo = create_ui()
    
    # Get the FastAPI app
    app = demo.queue().app
    
    print("=" * 50)
    print("   Server is starting...")
    print(f"   URL: http://127.0.0.1:{port}")
    print("=" * 50)
    print()
    print("[INFO] Opening browser in 3 seconds...")
    print("[INFO] Press Ctrl+C to stop")
    print()
    
    # Open browser after delay
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
        except:
            pass
    
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start uvicorn server
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
