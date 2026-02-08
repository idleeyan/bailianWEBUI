# 阿里云百炼文生图工具

版本: 1.2.0

一个简单的阿里云百炼文生图API调用程序，支持**文生图**和**图像编辑**功能，提供Web UI、交互式模式和命令行模式。

## 功能特点

- 🌐 **Web UI界面**：基于Gradio的现代化网页界面
- 🎨 **文生图**：支持多种通义万相模型生成图片
- ✏️ **图像编辑**：支持上传图片进行智能编辑（图生图）
- 🖼️ 支持自定义图片尺寸
- 💾 自动保存生成的图片
- 🖥️ 支持交互式、命令行、Web UI三种使用方式
- 📝 简单易用的中文界面

## 环境要求

- Python 3.6+
- requests 库
- gradio 库（Web UI需要）

## 安装

1. 确保已安装 Python 3.6 或更高版本
2. 安装依赖：

```bash
pip install requests gradio
```

## 获取API Key

1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/?apiKey=1)
2. 登录阿里云账号
3. 创建 API Key
4. 复制 API Key 备用

## 使用方法

### 方法一：Web UI模式（推荐！最方便）

启动网页界面：

```bash
python bailian_webui.py
```

然后会自动打开浏览器，显示可视化界面：
1. 输入API Key
2. 在文本框输入图片描述
3. 选择模型和尺寸
4. 点击生成按钮
5. 等待图片生成并显示在页面上

**特点**：
- 可视化操作，最友好
- 实时显示生成进度
- 图片直接在网页上展示
- 支持画廊查看多张图片

### 方法二：交互式模式（命令行）

直接运行程序：

```bash
python bailian_image_gen.py
```

然后按照提示操作：
1. 输入API Key（首次使用）
2. 选择"生成图片"
3. 输入图片描述（提示词）
4. 选择模型和尺寸
5. 等待图片生成

### 方法三：命令行模式（快速生成）

```bash
python bailian_image_gen.py "一只可爱的猫咪在草地上玩耍"
```

### 方法四：环境变量设置API Key

```bash
# Windows
set DASHSCOPE_API_KEY=your_api_key_here
python bailian_image_gen.py

# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key_here
python bailian_image_gen.py
```

## 支持的模型

### 文生图模型

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 1 | wanx-v1 | 通义万相-文生图V1（默认） |
| 2 | wanx2.1-t2i-turbo | 通义万相2.1-Turbo |
| 3 | wanx2.1-t2i-plus | 通义万相2.1-Plus |
| 4 | wan2.6-t2i | 通义万相2.6-文生图 |
| 5 | wan2.5-t2i-preview | 通义万相2.5-文生图预览版 |
| 6 | wan2.2-t2i-plus | 通义万相2.2-文生图Plus |
| 7 | wan2.2-t2i-flash | 通义万相2.2-文生图Flash |
| 8 | wan2.0-t2i-turbo | 通义万相2.0-Turbo |

### 通义千问图像模型

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 10 | qwen-image | 通义千问-图像生成 |
| 11 | qwen-image-plus | 通义千问-图像生成Plus |
| 12 | qwen-image-max | 通义千问-图像生成Max |
| 13 | qwen-image-turbo | 通义千问-图像生成Turbo |
| 14 | qwen-image-plus-2026-01-09 | 通义千问-图像Plus(2026版) |
| 15 | qwen-image-max-2025-12-30 | 通义千问-图像Max(2025版) |

### 图像编辑模型（图生图）

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 1 | qwen-image-edit | 通义千问-图像编辑 |
| 2 | qwen-image-edit-plus | 通义千问-图像编辑Plus |
| 3 | qwen-image-edit-max | 通义千问-图像编辑Max |
| 4 | qwen-image-edit-plus-2025-12-15 | 图像编辑Plus(2025-12) |
| 5 | qwen-image-edit-plus-2025-10-30 | 图像编辑Plus(2025-10) |
| 6 | qwen-image-edit-max-2026-01-16 | 图像编辑Max(2026版) |

### Flux模型

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 22 | flux-schnell | Flux-Schnell |
| 23 | flux-dev | Flux-Dev |
| 24 | flux-merged | Flux-Merged |

### 其他图像生成

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 19 | wanx-sketch-to-image-lite | 通义万相-草图生图 |
| 20 | wanx-x-painting | 通义万相-X绘画 |
| 21 | wanx-style-repaint-v1 | 通义万相-风格重绘 |
| 22 | wanx-background-generation-v2 | 通义万相-背景生成V2 |
| 23 | wanx-poster-generation-v1 | 通义万相-海报生成 |
| 24 | wanx-virtualmodel | 通义万相-虚拟模特 |
| 25 | image-out-painting | 图像画面扩展 |
| 26 | wanx2.1-imageedit | 通义万相2.1-图像编辑 |
| 27 | wanx2.1-vace-plus | 通义万相2.1-VACE Plus |
| 28 | wan2.5-i2i-preview | 通义万相2.5-图生图 |

### 艺术字

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 29 | wordart-semantic | 艺术字-语义 |
| 30 | wordart-texture | 艺术字-纹理 |

### 虚拟试衣

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 31 | aitryon | 虚拟试衣 |
| 32 | aitryon-plus | 虚拟试衣Plus |
| 33 | aitryon-refiner | 虚拟试衣精修 |
| 34 | aitryon-parsing-v1 | 虚拟试衣解析 |

### Emoji

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 35 | emoji-v1 | Emoji生成 |
| 36 | emoji-detect-v1 | Emoji检测 |

### 多语言图像

| 编号 | 模型名称 | 说明 |
|------|----------|------|
| 37 | qwen-mt-image | 通义千问-多语言图像 |

## 支持的图片尺寸

- 512*512
- 768*768
- 1024*1024（默认）
- 1280*720
- 1920*1080

## 示例

### 示例1：交互式生成（文生图）
```
$ python bailian_image_gen.py

============================================================
   阿里云百炼文生图工具
   版本: 1.2.0
============================================================

请输入您的阿里云百炼API Key:
> sk-xxxxxxxxxxxxxxxx

============================================================
主菜单:
  [1] 生成图片（文生图）
  [2] 编辑图片（图生图）
  [3] 查看支持的模型
  [4] 退出
============================================================

请选择操作 (1-4): 1

请输入图片描述（提示词）:
> 一只穿着宇航服的猫咪在月球上漫步

可用的文生图模型列表:
  [1] wanx-v1 - 通义万相-文生图V1（默认）
  [2] wanx2.1-t2i-turbo - 通义万相2.1-Turbo
  ...

请选择模型 (1-37，默认1): 1

可选尺寸:
  [1] 512*512
  [2] 768*768
  [3] 1024*1024
  [4] 1280*720
  [5] 1920*1080
请选择尺寸 (1-5，默认3): 3

正在生成图片...
模型: wanx-v1
提示词: 一只穿着宇航服的猫咪在月球上漫步
尺寸: 1024*1024
任务已提交，任务ID: xxxxxxxx
  正在生成中... (0秒)
  正在生成中... (10秒)

✅ 图片生成成功！
  已保存: generated_images/image_20250208_143052_1.png

✅ 成功生成 1 张图片
   📁 generated_images/image_20250208_143052_1.png
```

### 示例2：交互式编辑（图生图）
```
请选择操作 (1-4): 2

请输入参考图片路径:
> generated_images/image_20250208_143052_1.png

请输入编辑指令（提示词）:
> 把背景换成火星表面，添加红色岩石

可用的图像编辑模型列表:
  [1] qwen-image-edit - 通义千问-图像编辑
  [2] qwen-image-edit-plus - 通义千问-图像编辑Plus
  ...

请选择模型 (1-6，默认2): 2

正在编辑图片...
模型: qwen-image-edit-plus
提示词: 把背景换成火星表面，添加红色岩石
参考图片: generated_images/image_20250208_143052_1.png
尺寸: 1024*1024
任务已提交，任务ID: xxxxxxxx

✅ 图片编辑成功！
  已保存: generated_images/image_20250208_144530_1.png

✅ 成功编辑图片，生成 1 张图片
   📁 generated_images/image_20250208_144530_1.png
```

### 示例3：命令行快速生成
```bash
$ python bailian_image_gen.py "美丽的风景，日落时分的海滩"

正在生成图片...
模型: wanx-v1
提示词: 美丽的风景，日落时分的海滩
尺寸: 1024*1024
任务已提交，任务ID: xxxxxxxx
...

✅ 图片生成成功！
   📁 generated_images/image_20250208_143120_1.png
```

## 输出目录

生成的图片会自动保存在 `generated_images/` 目录下，文件名格式为：`image_YYYYMMDD_HHMMSS_N.png`

## 更新日志

### v1.2.0 (2025-02-08)
- ✅ 新增图像编辑功能（图生图）
- ✅ 支持6种图像编辑模型：qwen-image-edit系列
- ✅ Web UI新增"图像编辑"选项卡
- ✅ 交互式模式支持编辑图片功能
- ✅ 模型列表分离：文生图模型和图像编辑模型分开显示

### v1.1.0 (2025-02-08)
- 新增Web UI界面（基于Gradio）
- 支持可视化操作和图片预览
- 优化用户体验

### v1.0.0 (2025-02-08)
- 初始版本发布
- 支持交互式和命令行两种模式
- 支持多种模型和尺寸选择
- 支持图片自动保存

## 注意事项

1. **API Key安全**：请勿将API Key硬编码在代码中或上传到公共仓库
2. **免费额度**：阿里云百炼提供免费额度，超出后需要付费
3. **生成时间**：图片生成需要一定时间，请耐心等待
4. **网络要求**：需要能够访问阿里云API的网络环境

## 常见问题

### Q: 提示"API Key不能为空"
A: 请确保已正确输入API Key，或通过环境变量 `DASHSCOPE_API_KEY` 设置

### Q: 生成失败或超时
A: 
- 检查网络连接
- 检查API Key是否有效
- 检查是否有足够的额度
- 稍后重试

### Q: 生成的图片在哪里？
A: 图片保存在程序同级目录的 `generated_images/` 文件夹中

## 相关链接

- [阿里云百炼控制台](https://bailian.console.aliyun.com/)
- [获取API Key](https://bailian.console.aliyun.com/?apiKey=1)
- [阿里云百炼文档](https://help.aliyun.com/zh/model-studio/)

## 许可证

MIT License
