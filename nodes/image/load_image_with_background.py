"""
AutoFlow Load Image with Background Color Control

复刻官方Load Image节点，但增加透明图像背景色选择功能
"""

import os
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import node_helpers


class AutoFlowLoadImageWithBackground:
    """
    加载图像节点，支持为透明图像设置自定义背景色
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        
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
                "image": (sorted(files), {"image_upload": True}),
                "background_color": (background_colors, {"default": "default"}),
            }
        }

    CATEGORY = "AutoFlow/image"
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "image_path")
    FUNCTION = "load_image"

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

    def load_image(self, image, background_color):
        image_path = folder_paths.get_annotated_filepath(image)
        # 获取图片的绝对路径
        absolute_image_path = os.path.abspath(image_path)
        img = node_helpers.pillow(Image.open, image_path)

        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']

        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))

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

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]

            if image.size[0] != w or image.size[1] != h:
                continue

            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            
            # 处理mask
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            elif i.mode == 'P' and 'transparency' in i.info:
                mask = np.array(i.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
                
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask, absolute_image_path) 