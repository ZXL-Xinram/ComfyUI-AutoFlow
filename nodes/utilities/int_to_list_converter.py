"""
AutoFlow Int to List Converter Node

支持可扩展的int输入，自动将多个int值转换为list输出
当用户连接新的输入时，会自动渲染新的输入槽位
"""

import torch
from typing import Any, Dict, List, Tuple

# 定义通用类型
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True
    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")

# 最大输入数量常量
MAX_INT_INPUTS = 20

class AutoFlowIntToListConverter:
    """
    可扩展的Int转List转换器节点
    
    功能：
    - 支持1到最多20个int输入
    - 自动扩展输入槽位当用户连接新输入时
    - 将所有连接的int值合并为一个list输出
    - 忽略未连接的输入槽位
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入类型 - 使用可选输入实现可扩展性"""
        return {
            "required": {
                # 至少需要一个int输入
                "int_input_1": ("INT", {"default": 0, "min": -999999, "max": 999999}),
                # 控制输出列表长度的参数
                "length": ("INT", {"default": 1, "min": 1, "max": MAX_INT_INPUTS}),
            },
            "optional": {
                # 可扩展的int输入，从2到MAX_INT_INPUTS
                f"int_input_{i}": ("INT", {"default": 0, "min": -999999, "max": 999999}) 
                for i in range(2, MAX_INT_INPUTS + 1)
            }
        }
    
    RETURN_TYPES = (any_type,)  # 返回通用类型作为列表
    RETURN_NAMES = ("int_list",)
    OUTPUT_IS_LIST = (True,)  # 输出是列表形式
    FUNCTION = "convert_to_list"
    CATEGORY = "AutoFlow/Utilities/Converters"
    
    def convert_to_list(self, length, **kwargs):
        """
        将指定数量的int输入转换为list
        
        Args:
            length: 输出列表的长度
            **kwargs: 所有的int输入参数
            
        Returns:
            Tuple: 包含指定长度的int值列表
        """
        # 收集指定数量的int值
        int_values = []
        
        # 按顺序处理输入，只取length指定的数量
        for i in range(1, length + 1):
            input_key = f"int_input_{i}"
            if input_key in kwargs:
                value = kwargs[input_key]
                int_values.append(value)
            else:
                # 如果输入不存在，使用默认值0
                int_values.append(0)
            
        print(f"[AutoFlowIntToListConverter] 转换了 {len(int_values)} 个int值到列表: {int_values}")
        
        return (int_values,)


class AutoFlowListToIntExtractor:
    """
    List转Int提取器节点
    
    功能：
    - 从int列表中按索引提取特定的int值
    - 支持负索引（从末尾开始）
    - 提供安全的边界检查
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入类型"""
        return {
            "required": {
                "int_list": (any_type, {}),  # 输入的int列表
                "index": ("INT", {"default": 0, "min": -999, "max": 999}),  # 要提取的索引
            },
            "optional": {
                "default_value": ("INT", {"default": 0, "min": -999999, "max": 999999}),  # 索引越界时的默认值
            }
        }
    
    RETURN_TYPES = ("INT", "BOOLEAN")
    RETURN_NAMES = ("extracted_int", "is_valid_index")
    INPUT_IS_LIST = (True, False, False)  # 第一个输入是列表
    FUNCTION = "extract_int"
    CATEGORY = "AutoFlow/Utilities/Converters"
    
    def extract_int(self, int_list, index, default_value=0):
        """
        从int列表中提取指定索引的值
        
        Args:
            int_list: 输入的int列表
            index: 要提取的索引位置
            default_value: 索引无效时的默认值
            
        Returns:
            Tuple: (提取的值, 是否为有效索引)
        """
        try:
            # 检查列表是否为空
            if not int_list:
                print(f"[AutoFlowListToIntExtractor] 空列表，返回默认值: {default_value}")
                return (default_value, False)
            
            # 检查索引是否在有效范围内
            if -len(int_list) <= index < len(int_list):
                extracted_value = int_list[index]
                print(f"[AutoFlowListToIntExtractor] 从索引 {index} 提取值: {extracted_value}")
                return (extracted_value, True)
            else:
                print(f"[AutoFlowListToIntExtractor] 索引 {index} 超出范围 [0, {len(int_list)-1}]，返回默认值: {default_value}")
                return (default_value, False)
                
        except Exception as e:
            print(f"[AutoFlowListToIntExtractor] 提取时发生错误: {str(e)}，返回默认值: {default_value}")
            return (default_value, False)


class AutoFlowListLength:
    """
    列表长度计算器节点
    
    功能：
    - 计算int列表的长度
    - 用于配合其他节点使用
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        """定义输入类型"""
        return {
            "required": {
                "int_list": (any_type, {}),  # 输入的int列表
            }
        }
    
    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("list_length",)
    INPUT_IS_LIST = (True,)  # 输入是列表
    FUNCTION = "get_length"
    CATEGORY = "AutoFlow/Utilities/Converters"
    
    def get_length(self, int_list):
        """
        获取列表长度
        
        Args:
            int_list: 输入的int列表
            
        Returns:
            Tuple: 列表的长度
        """
        length = len(int_list) if int_list else 0
        print(f"[AutoFlowListLength] 列表长度: {length}")
        return (length,) 