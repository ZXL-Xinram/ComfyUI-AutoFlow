import torch
import numpy as np
from PIL import Image
import os
import folder_paths
from pathlib import Path
import cv2
import hashlib

# 支持的视频格式
VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'mpg', 'mpeg', 'm4v']

class AutoFlowVideoToImages:
    """
    将视频转换为图像序列
    Convert video to image sequence
    支持上传模式和路径模式
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 获取input目录下的视频文件
        input_dir = folder_paths.get_input_directory()
        video_files = []
        if os.path.exists(input_dir):
            for f in os.listdir(input_dir):
                if f.lower().endswith(tuple(f'.{ext}' for ext in VIDEO_EXTENSIONS)):
                    video_files.append(f)
        
        return {
            "required": {
                "use_path_mode": ("BOOLEAN", {"default": False}),  # False=上传模式, True=路径模式
                "video_upload": (sorted(video_files) if video_files else [""],),  # 上传模式：从列表选择
                "video_path": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "D:/videos/my_video.mp4"
                }),  # 路径模式：输入完整路径
                "start_frame": ("INT", {"default": 0, "min": 0, "max": 999999, "step": 1}),
                "frame_count": ("INT", {"default": -1, "min": -1, "max": 999999, "step": 1}),  # -1表示全部
            },
        }
    
    RETURN_TYPES = ("IMAGE", "INT", "INT", "STRING")
    RETURN_NAMES = ("images", "total_frames", "fps", "video_info")
    FUNCTION = "convert"
    CATEGORY = "AutoFlow/Video"
    
    def convert(self, use_path_mode, video_upload, video_path, start_frame, frame_count):
        # 根据模式确定视频路径
        if use_path_mode:
            # 路径模式
            if not video_path or not os.path.exists(video_path):
                raise ValueError(f"路径模式下必须提供有效的视频路径 / Must provide valid video path in path mode: {video_path}")
            video_file_path = video_path
        else:
            # 上传模式
            if not video_upload:
                raise ValueError("上传模式下必须选择视频文件 / Must select a video file in upload mode")
            video_file_path = folder_paths.get_annotated_filepath(video_upload)
        
        # 打开视频
        cap = cv2.VideoCapture(video_file_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件 / Cannot open video file: {video_file_path}")
        
        # 获取视频信息
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_info = f"Video: {os.path.basename(video_file_path)} | {width}x{height} | {fps}fps | {total_frames} frames"
        
        # 设置起始帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        # 确定要读取的帧数
        if frame_count == -1:
            frames_to_read = total_frames - start_frame
        else:
            frames_to_read = min(frame_count, total_frames - start_frame)
        
        images = []
        for i in range(frames_to_read):
            ret, frame = cap.read()
            if not ret:
                break
            
            # OpenCV读取的是BGR，转换为RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为torch tensor，归一化到[0,1]
            frame_tensor = torch.from_numpy(frame_rgb).float() / 255.0
            images.append(frame_tensor)
        
        cap.release()
        
        if len(images) == 0:
            raise ValueError("未能从视频中读取任何帧 / No frames read from video")
        
        # 堆叠为batch
        images_batch = torch.stack(images, dim=0)
        
        mode_str = "Path" if use_path_mode else "Upload"
        print(f"[AutoFlow] Mode: {mode_str} | {video_info}")
        print(f"[AutoFlow] Loaded {len(images)} frames (from frame {start_frame})")
        
        return (images_batch, len(images), fps, video_info)


class AutoFlowAddAlphaChannel:
    """
    将蒙版图像作为Alpha通道添加到RGB图像
    Add mask as alpha channel to RGB images
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),  # RGB图像 [B,H,W,3]
                "mask": ("IMAGE",),    # 蒙版图像 [B,H,W,3] 或 [B,H,W,1]，白色=不透明，黑色=透明
                "invert_mask": ("BOOLEAN", {"default": False}),  # 是否反转蒙版
                "multiply_rgb": ("BOOLEAN", {"default": False}),  # 是否将RGB与蒙版相乘（预乘Alpha）
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("rgba_images",)
    FUNCTION = "add_alpha"
    CATEGORY = "AutoFlow/Video"
    
    def add_alpha(self, images, mask, invert_mask, multiply_rgb):
        # 确保images和mask的batch大小一致
        if images.shape[0] != mask.shape[0]:
            raise ValueError(f"图像和蒙版的batch大小不一致: {images.shape[0]} vs {mask.shape[0]}")
        
        # 提取蒙版的第一个通道作为Alpha
        if mask.shape[-1] == 3:
            # 如果是RGB蒙版，取平均值
            alpha = mask.mean(dim=-1, keepdim=True)
        else:
            alpha = mask
        
        # 反转蒙版（如果需要）
        if invert_mask:
            alpha = 1.0 - alpha
        
        # 如果需要预乘Alpha（这样边缘更自然）
        if multiply_rgb:
            rgb_premultiplied = images * alpha
        else:
            rgb_premultiplied = images
        
        # 合并RGB和Alpha通道
        rgba = torch.cat([rgb_premultiplied, alpha], dim=-1)
        
        return (rgba,)


class AutoFlowSaveImagesWithAlpha:
    """
    保存带透明通道的PNG图像序列
    Save PNG image sequence with alpha channel
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),  # RGBA图像 [B,H,W,4]
                "filename_prefix": ("STRING", {"default": "transparent/alpha_image"}),
            },
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("output_path", "saved_count")
    FUNCTION = "save_images"
    CATEGORY = "AutoFlow/Video"
    OUTPUT_NODE = True
    
    def save_images(self, images, filename_prefix):
        # 使用ComfyUI的标准路径处理函数
        output_dir = folder_paths.get_output_directory()
        
        # 解析子目录和文件名前缀
        # 例如 "images/alpha_image" -> subfolder="images", filename="alpha_image"
        subfolder = os.path.dirname(os.path.normpath(filename_prefix))
        filename = os.path.basename(os.path.normpath(filename_prefix))
        
        # 创建完整输出目录
        full_output_folder = os.path.join(output_dir, subfolder)
        
        # 安全检查：确保输出路径在output_dir内
        if os.path.commonpath((output_dir, os.path.abspath(full_output_folder))) != output_dir:
            raise ValueError(f"不允许保存到output目录之外 / Saving outside output folder is not allowed: {full_output_folder}")
        
        # 创建目录（如果不存在）
        os.makedirs(full_output_folder, exist_ok=True)
        
        # 查找现有文件，确定起始计数器（防止覆盖）
        # 查找格式为 filename_数字_.png 的文件
        def map_filename(f):
            """提取文件名中的计数器"""
            prefix_len = len(filename)
            if not f.startswith(filename + "_"):
                return 0
            try:
                # 提取 filename_数字_ 中的数字部分
                digits = int(f[prefix_len + 1:].split('_')[0])
                return digits
            except:
                return 0
        
        try:
            existing_files = os.listdir(full_output_folder)
            # 过滤出匹配的文件名并提取计数器
            counters = [map_filename(f) for f in existing_files if f.startswith(filename + "_") and f.endswith("_.png")]
            counter = max(counters) + 1 if counters else 1
        except FileNotFoundError:
            counter = 1
        
        saved_count = 0
        results = []
        
        for i, img_tensor in enumerate(images):
            # 转换为numpy数组 [H,W,4]
            img_np = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
            
            # 检查是否有Alpha通道
            if img_np.shape[-1] == 4:
                # RGBA
                img_pil = Image.fromarray(img_np, mode='RGBA')
            elif img_np.shape[-1] == 3:
                # RGB，添加完全不透明的Alpha通道
                alpha = np.ones((img_np.shape[0], img_np.shape[1], 1), dtype=np.uint8) * 255
                img_np = np.concatenate([img_np, alpha], axis=-1)
                img_pil = Image.fromarray(img_np, mode='RGBA')
            else:
                raise ValueError(f"不支持的图像通道数: {img_np.shape[-1]}")
            
            # 生成文件名：filename_counter_frameindex_.png
            # 例如：alpha_image_00001_00000_.png
            file = f"{filename}_{counter:05}_{i:05}_.png"
            filepath = os.path.join(full_output_folder, file)
            
            # 保存PNG（自动支持透明通道）
            img_pil.save(filepath, format='PNG', compress_level=6)
            saved_count += 1
            
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": "output"
            })
        
        # 下次运行时从下一个counter开始
        counter += 1
        
        print(f"[AutoFlow] Saved {saved_count} transparent PNG images to: {full_output_folder}")
        
        return (full_output_folder, saved_count)


class AutoFlowCombineVideoAndMask:
    """
    一步到位：将原视频和蒙版视频合成为透明PNG序列
    One-step: Combine original video and mask video to transparent PNG sequence
    支持上传模式和路径模式
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        video_files = []
        if os.path.exists(input_dir):
            for f in os.listdir(input_dir):
                if f.lower().endswith(tuple(f'.{ext}' for ext in VIDEO_EXTENSIONS)):
                    video_files.append(f)
        
        return {
            "required": {
                "use_path_mode": ("BOOLEAN", {"default": False}),  # False=上传模式, True=路径模式
                "original_video_upload": (sorted(video_files) if video_files else [""],),
                "mask_video_upload": (sorted(video_files) if video_files else [""],),
                "original_video_path": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "D:/videos/original.mp4"
                }),
                "mask_video_path": ("STRING", {
                    "default": "", 
                    "multiline": False,
                    "placeholder": "D:/videos/mask.mp4"
                }),
                "filename_prefix": ("STRING", {"default": "transparent"}),
                "invert_mask": ("BOOLEAN", {"default": False}),
                "multiply_rgb": ("BOOLEAN", {"default": False}),
                "start_frame": ("INT", {"default": 0, "min": 0, "max": 999999, "step": 1}),
                "frame_count": ("INT", {"default": -1, "min": -1, "max": 999999, "step": 1}),
            },
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "INT", "STRING")
    RETURN_NAMES = ("images", "output_path", "saved_count", "process_info")
    FUNCTION = "process"
    CATEGORY = "AutoFlow/Video"
    OUTPUT_NODE = True
    
    def process(self, use_path_mode, original_video_upload, mask_video_upload, 
                original_video_path, mask_video_path, filename_prefix, 
                invert_mask, multiply_rgb, start_frame, frame_count):
        
        # 根据模式确定视频路径
        if use_path_mode:
            # 路径模式
            if not original_video_path or not mask_video_path:
                raise ValueError("路径模式下必须提供原视频和蒙版视频的完整路径 / Must provide both video paths in path mode")
            if not os.path.exists(original_video_path):
                raise ValueError(f"原视频路径不存在 / Original video path not found: {original_video_path}")
            if not os.path.exists(mask_video_path):
                raise ValueError(f"蒙版视频路径不存在 / Mask video path not found: {mask_video_path}")
            original_path = original_video_path
            mask_path = mask_video_path
        else:
            # 上传模式
            if not original_video_upload or not mask_video_upload:
                raise ValueError("上传模式下必须选择原视频和蒙版视频 / Must select both videos in upload mode")
            original_path = folder_paths.get_annotated_filepath(original_video_upload)
            mask_path = folder_paths.get_annotated_filepath(mask_video_upload)
        
        mode_str = "Path" if use_path_mode else "Upload"
        print(f"[AutoFlow] Processing videos in {mode_str} mode...")
        print(f"[AutoFlow] Original: {os.path.basename(original_path)}")
        print(f"[AutoFlow] Mask: {os.path.basename(mask_path)}")
        
        # 1. 读取原视频
        video_to_images = AutoFlowVideoToImages()
        original_images, total_frames, fps, video_info = video_to_images.convert(
            use_path_mode, original_video_upload, original_path, start_frame, frame_count
        )
        
        # 2. 读取蒙版视频
        mask_images, mask_total_frames, mask_fps, mask_info = video_to_images.convert(
            use_path_mode, mask_video_upload, mask_path, start_frame, frame_count
        )
        
        # 3. 添加Alpha通道
        add_alpha = AutoFlowAddAlphaChannel()
        rgba_images, = add_alpha.add_alpha(original_images, mask_images, invert_mask, multiply_rgb)
        
        # 4. 保存为PNG序列
        save_images = AutoFlowSaveImagesWithAlpha()
        output_path, saved_count = save_images.save_images(rgba_images, filename_prefix)
        
        process_info = f"Processed {saved_count} frames | Mode: {mode_str} | Output: {output_path}"
        print(f"[AutoFlow] {process_info}")
        
        # 返回RGBA图像序列、输出路径、保存数量和处理信息
        return (rgba_images, output_path, saved_count, process_info)


# 节点映射
NODE_CLASS_MAPPINGS = {
    "AutoFlowVideoToImages": AutoFlowVideoToImages,
    "AutoFlowAddAlphaChannel": AutoFlowAddAlphaChannel,
    "AutoFlowSaveImagesWithAlpha": AutoFlowSaveImagesWithAlpha,
    "AutoFlowCombineVideoAndMask": AutoFlowCombineVideoAndMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AutoFlowVideoToImages": "AutoFlow Video To Images",
    "AutoFlowAddAlphaChannel": "AutoFlow Add Alpha Channel",
    "AutoFlowSaveImagesWithAlpha": "AutoFlow Save Images With Alpha",
    "AutoFlowCombineVideoAndMask": "AutoFlow Combine Video And Mask",
}
