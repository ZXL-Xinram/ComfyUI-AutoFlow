"""
AutoFlow Load Images For Loop with Background Color Control

复刻ComfyUI-Easy-Use的Load Images For Loop节点，但增加透明图像背景色选择功能
"""

import os
import numpy as np
import torch
from PIL import Image, ImageOps
import folder_paths

try:
    from comfy_execution.graph_utils import GraphBuilder
except:
    GraphBuilder = None

# 定义通用类型
any_type = "*"

def ByPassTypeTuple(x):
    """兼容函数，用于处理类型元组"""
    return x


class AutoFlowLoadImagesForLoopWithBackground:
    """
    批量加载图像用于循环节点，支持为透明图像设置自定义背景色
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # 背景色选项
        background_colors = [
            "default",  # 使用系统默认行为
            "white",    # 白色
            "black",    # 黑色
            "gray",     # 灰色
            "red",      # 红色
            "green",    # 绿色
            "blue",     # 蓝色
            "yellow",   # 黄色
        ]
        
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "background_color": (background_colors, {"default": "default"}),
            },
            "optional": {
                "start_index": ("INT", {"default": 0, "min": 0, "step": 1}),
                "limit": ("INT", {"default": -1, "min": -1, "max": 10000}),
                "initial_value1": (any_type,),
                "initial_value2": (any_type,),
            },
            "hidden": {
                "initial_value0": (any_type,),
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ByPassTypeTuple(tuple(["FLOW_CONTROL", "INT", "IMAGE", "MASK", "STRING", any_type, any_type]))
    RETURN_NAMES = ByPassTypeTuple(tuple(["flow", "index", "image", "mask", "name", "value1", "value2"]))
    CATEGORY = "AutoFlow/image"
    FUNCTION = "load_images"

    def get_background_color(self, color_name):
        """
        根据颜色名称返回RGB值
        """
        color_map = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "gray": (128, 128, 128),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
        }
        return color_map.get(color_name, None)

    def process_image_with_background(self, image_path, background_color):
        """
        处理图像，支持背景色设置
        """
        i = Image.open(image_path)
        i = ImageOps.exif_transpose(i)

        # 处理透明图像的背景色
        if background_color != "default" and ('A' in i.getbands() or (i.mode == 'P' and 'transparency' in i.info)):
            # 图像有透明通道，需要处理背景色
            bg_color = self.get_background_color(background_color)
            if bg_color:
                # 创建指定背景色的图像
                bg_image = Image.new('RGB', i.size, bg_color)
                if i.mode != 'RGBA':
                    i = i.convert('RGBA')
                # 使用alpha合成
                image = Image.alpha_composite(bg_image.convert('RGBA'), i).convert('RGB')
            else:
                image = i.convert("RGB")
        else:
            # 使用默认行为
            image = i.convert("RGB")

        # 转换为tensor
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]

        # 处理mask
        if 'A' in i.getbands():
            mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

        return image, mask

    def load_images(self, directory: str, background_color: str, start_index: int = 0, limit: int = -1, 
                   prompt=None, extra_pnginfo=None, unique_id=None, **kwargs):
        
        print(f"Loading images from directory: {directory}")
        
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory '{directory}' cannot be found.")

        dir_files = os.listdir(directory)
        if len(dir_files) == 0:
            raise FileNotFoundError(f"No files in directory '{directory}'.")

        # 过滤图像文件
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif']
        dir_files = [f for f in dir_files if any(f.lower().endswith(ext) for ext in valid_extensions)]

        if len(dir_files) == 0:
            raise FileNotFoundError(f"No valid image files in directory '{directory}'.")

        dir_files = sorted(dir_files)
        dir_files = [os.path.join(directory, x) for x in dir_files]

        # 检查索引范围
        total_files = len(dir_files)
        if start_index >= total_files:
            raise ValueError(f"Start index {start_index} is out of range. Directory has {total_files} files.")

        # 处理限制
        if limit > 0:
            end_index = min(start_index + limit, total_files)
            dir_files = dir_files[start_index:end_index]
        elif start_index > 0:
            dir_files = dir_files[start_index:]

        if GraphBuilder is None:
            # 如果GraphBuilder不可用，简化返回
            print("Warning: GraphBuilder not available, using simplified mode")
            
            # 获取当前索引
            index = 0
            if "initial_value0" in kwargs:
                index = kwargs["initial_value0"]
                
            if index >= len(dir_files):
                index = 0  # 重置到开始
                
            image_path = dir_files[index]
            name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 处理图像
            image, mask = self.process_image_with_background(image_path, background_color)
            
            outputs = [kwargs.get('initial_value1', None), kwargs.get('initial_value2', None)]
            
            return tuple(["stub", index, image, mask, name] + outputs)
        
        else:
            # 使用GraphBuilder的完整实现
            graph = GraphBuilder()
            index = 0
            
            if "initial_value0" in kwargs:
                index = kwargs["initial_value0"]
            
            if index >= len(dir_files):
                index = 0  # 重置到开始
                
            image_path = dir_files[index]
            name = os.path.splitext(os.path.basename(image_path))[0]
            
            # 处理图像
            image, mask = self.process_image_with_background(image_path, background_color)
            
            # 创建循环控制
            while_open = graph.node("easy whileLoopStart", 
                                  condition=True, 
                                  initial_value0=index, 
                                  initial_value1=kwargs.get('initial_value1', None), 
                                  initial_value2=kwargs.get('initial_value2', None))
            
            outputs = [kwargs.get('initial_value1', None), kwargs.get('initial_value2', None)]
            
            return {
                "result": tuple(["stub", index, image, mask, name] + outputs),
                "expand": graph.finalize(),
            } 