"""
Image resize calculator node - 图像尺寸计算器
根据指定的像素总数，计算保持宽高比的最大整数尺寸
"""

import math
from typing import Tuple

class AutoFlowImageResizeCalculator:
    """
    图像尺寸计算器节点
    
    功能: 根据输入的width、height和目标像素总数，计算保持宽高比不变的最大整数尺寸
    用途: 用于严格控制图像处理的计算量等场景
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 65536,
                    "step": 1,
                    "tooltip": "Original image width"
                }),
                "height": ("INT", {
                    "default": 1024,
                    "min": 1,
                    "max": 65536,
                    "step": 1,
                    "tooltip": "Original image height"
                }),
                "num_pixels": ("INT", {
                    "default": 1048576,  # 1024*1024
                    "min": 1,
                    "max": 16777216,  # 4096*4096
                    "step": 1,
                    "tooltip": "Target maximum total pixels (width_max * height_max <= num_pixels)"
                }),
            }
        }
    
    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width_max", "height_max")
    FUNCTION = "calculate_max_size"
    CATEGORY = "AutoFlow/Image"
    
    @classmethod
    def IS_CHANGED(cls, width, height, num_pixels):
        """
        确保节点在输入变化时自动更新
        """
        return f"{width}_{height}_{num_pixels}"
    
    def calculate_max_size(self, width: int, height: int, num_pixels: int) -> Tuple[int, int]:
        """
        计算保持宽高比的最大整数尺寸
        
        Args:
            width: 原始宽度
            height: 原始高度  
            num_pixels: 目标像素总数上限
            
        Returns:
            tuple: (width_max, height_max) 最大整数尺寸
        """
        try:
            # 输入验证
            if width <= 0 or height <= 0 or num_pixels <= 0:
                print(f"❌ [AutoFlowImageResizeCalculator] Invalid input: width={width}, height={height}, num_pixels={num_pixels}")
                return (1, 1)
            
            # 计算原始宽高比
            aspect_ratio = width / height
            
            # 如果原始像素数已经小于等于目标，直接返回原始尺寸
            if width * height <= num_pixels:
                print(f"✅ [AutoFlowImageResizeCalculator] Original size fits: {width}x{height} <= {num_pixels} pixels")
                return (width, height)
            
            # 数学推导:
            # 设缩放后的尺寸为 (w_max, h_max)
            # 保持宽高比: w_max / h_max = width / height = aspect_ratio
            # 所以: w_max = aspect_ratio * h_max
            # 像素约束: w_max * h_max <= num_pixels
            # 代入得: (aspect_ratio * h_max) * h_max <= num_pixels
            # 即: aspect_ratio * h_max^2 <= num_pixels
            # 解得: h_max <= sqrt(num_pixels / aspect_ratio)
            
            # 计算理论最大高度
            h_max_float = math.sqrt(num_pixels / aspect_ratio)
            h_max = int(math.floor(h_max_float))
            
            # 计算对应的宽度
            w_max_float = aspect_ratio * h_max
            w_max = int(math.floor(w_max_float))
            
            # 验证并可能需要微调
            # 由于取整误差，可能需要进一步调整以确保 w_max * h_max <= num_pixels
            while w_max * h_max > num_pixels and (w_max > 1 or h_max > 1):
                if w_max > h_max:
                    w_max -= 1
                else:
                    h_max -= 1
                    # 重新计算宽度以保持比例
                    w_max = int(math.floor(aspect_ratio * h_max))
            
            # 尝试在保持约束的前提下最大化尺寸
            # 检查是否可以增加尺寸而不违反约束
            improved = True
            max_iterations = 100  # 防止无限循环
            iteration = 0
            
            while improved and iteration < max_iterations:
                improved = False
                iteration += 1
                
                # 尝试增加高度
                test_h = h_max + 1
                test_w = int(math.floor(aspect_ratio * test_h))
                if test_w * test_h <= num_pixels:
                    h_max = test_h
                    w_max = test_w
                    improved = True
                    continue
                
                # 尝试增加宽度
                test_w = w_max + 1
                test_h = int(math.floor(test_w / aspect_ratio))
                if test_w * test_h <= num_pixels:
                    w_max = test_w
                    h_max = test_h
                    improved = True
            
            # 最终验证
            if w_max <= 0:
                w_max = 1
            if h_max <= 0:
                h_max = 1
                
            final_pixels = w_max * h_max
            
            print(f"✅ [AutoFlowImageResizeCalculator] Calculated size: {w_max}x{h_max} = {final_pixels} pixels (limit: {num_pixels})")
            print(f"   Original: {width}x{height} = {width*height} pixels")
            print(f"   Aspect ratio preserved: {width/height:.4f} -> {w_max/h_max:.4f}")
            
            return (w_max, h_max)
            
        except Exception as e:
            print(f"❌ [AutoFlowImageResizeCalculator] Error in calculation: {str(e)}")
            return (1, 1) 