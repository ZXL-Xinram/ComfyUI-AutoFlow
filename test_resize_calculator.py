#!/usr/bin/env python3
"""
测试图像尺寸计算器节点
"""

import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from nodes.image.image_resize_calculator import AutoFlowImageResizeCalculator

def test_resize_calculator():
    """测试图像尺寸计算器功能"""
    calculator = AutoFlowImageResizeCalculator()
    
    # 测试用例1: 1920x1080 -> 1024*1024 像素
    print("=== 测试用例1: 1920x1080 -> 1048576 像素 ===")
    w_max, h_max = calculator.calculate_max_size(1920, 1080, 1048576)
    ratio_original = 1920 / 1080
    ratio_result = w_max / h_max
    print(f"原始尺寸: 1920x1080 ({1920*1080} 像素)")
    print(f"结果尺寸: {w_max}x{h_max} ({w_max*h_max} 像素)")
    print(f"原始宽高比: {ratio_original:.4f}")
    print(f"结果宽高比: {ratio_result:.4f}")
    print(f"宽高比差异: {abs(ratio_original - ratio_result):.6f}")
    print()
    
    # 测试用例2: 1024x768 -> 500000 像素
    print("=== 测试用例2: 1024x768 -> 500000 像素 ===")
    w_max, h_max = calculator.calculate_max_size(1024, 768, 500000)
    ratio_original = 1024 / 768
    ratio_result = w_max / h_max
    print(f"原始尺寸: 1024x768 ({1024*768} 像素)")
    print(f"结果尺寸: {w_max}x{h_max} ({w_max*h_max} 像素)")
    print(f"原始宽高比: {ratio_original:.4f}")
    print(f"结果宽高比: {ratio_result:.4f}")
    print(f"宽高比差异: {abs(ratio_original - ratio_result):.6f}")
    print()
    
    # 测试用例3: 正方形图像
    print("=== 测试用例3: 512x512 -> 200000 像素 ===")
    w_max, h_max = calculator.calculate_max_size(512, 512, 200000)
    ratio_original = 512 / 512
    ratio_result = w_max / h_max
    print(f"原始尺寸: 512x512 ({512*512} 像素)")
    print(f"结果尺寸: {w_max}x{h_max} ({w_max*h_max} 像素)")
    print(f"原始宽高比: {ratio_original:.4f}")
    print(f"结果宽高比: {ratio_result:.4f}")
    print(f"宽高比差异: {abs(ratio_original - ratio_result):.6f}")
    print()
    
    # 测试用例4: 原始尺寸已经小于目标
    print("=== 测试用例4: 800x600 -> 1000000 像素 ===")
    w_max, h_max = calculator.calculate_max_size(800, 600, 1000000)
    print(f"原始尺寸: 800x600 ({800*600} 像素)")
    print(f"结果尺寸: {w_max}x{h_max} ({w_max*h_max} 像素)")
    print()

if __name__ == "__main__":
    test_resize_calculator() 