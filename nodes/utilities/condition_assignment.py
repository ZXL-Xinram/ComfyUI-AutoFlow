"""
Condition assignment node - 提供条件赋值功能
"""

from typing import Tuple, Any
from comfy.comfy_types import IO

# 定义ANY类型 - 使用AlwaysEqualProxy来确保与任何类型兼容
class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")

class AutoFlowConditionAssignment:
    """
    条件赋值节点
    
    功能: 根据Boolean输入值决定输出String、Int、Float的值
    输入: Boolean条件和对应的真假值
    输出: String、Int、Float三种类型的值
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": (IO.BOOLEAN, {
                    "default": True,
                    "tooltip": "Condition to determine output values"
                }),
                "string_true": ("STRING", {
                    "multiline": False,
                    "default": "true",
                    "placeholder": "String value when condition is true"
                }),
                "string_false": ("STRING", {
                    "multiline": False,
                    "default": "false",
                    "placeholder": "String value when condition is false"
                }),
                "int_true": ("INT", {
                    "default": 1,
                    "min": -999999,
                    "max": 999999,
                    "step": 1,
                    "tooltip": "Integer value when condition is true"
                }),
                "int_false": ("INT", {
                    "default": 0,
                    "min": -999999,
                    "max": 999999,
                    "step": 1,
                    "tooltip": "Integer value when condition is false"
                }),
                "float_true": ("FLOAT", {
                    "default": 1.0,
                    "min": -999999.0,
                    "max": 999999.0,
                    "step": 0.01,
                    "tooltip": "Float value when condition is true"
                }),
                "float_false": ("FLOAT", {
                    "default": 0.0,
                    "min": -999999.0,
                    "max": 999999.0,
                    "step": 0.01,
                    "tooltip": "Float value when condition is false"
                }),
            },
            "optional": {
                "image_true": ("IMAGE", {
                    "tooltip": "Image value when condition is true"
                }),
                "image_false": ("IMAGE", {
                    "tooltip": "Image value when condition is false"
                }),
                "any_true": (any_type, {
                    "tooltip": "Any type value when condition is true"
                }),
                "any_false": (any_type, {
                    "tooltip": "Any type value when condition is false"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "FLOAT", "IMAGE", any_type)
    RETURN_NAMES = ("string", "int", "float", "image", "any")
    FUNCTION = "assign_values"
    CATEGORY = "AutoFlow/Utilities"
    
    @classmethod
    def IS_CHANGED(cls, condition, string_true, string_false, 
                   int_true, int_false, float_true, float_false, **kwargs):
        """
        确保节点在输入变化时自动更新
        通过返回输入参数的组合来检测变化
        """
        # 构建用于检测变化的字符串，包含所有影响输出的参数
        change_key = f"{condition}_{string_true}_{string_false}_{int_true}_{int_false}_{float_true}_{float_false}"
        
        # 添加可选的image和any类型参数（如果存在）
        image_true = kwargs.get("image_true", None)
        image_false = kwargs.get("image_false", None)
        any_true = kwargs.get("any_true", None)
        any_false = kwargs.get("any_false", None)
        
        # 对于复杂类型，我们使用其类型和id来生成唯一标识
        if image_true is not None:
            change_key += f"_img_t_{type(image_true).__name__}_{id(image_true)}"
        if image_false is not None:
            change_key += f"_img_f_{type(image_false).__name__}_{id(image_false)}"
        if any_true is not None:
            change_key += f"_any_t_{type(any_true).__name__}_{id(any_true)}"
        if any_false is not None:
            change_key += f"_any_f_{type(any_false).__name__}_{id(any_false)}"
        
        return change_key
    
    def assign_values(self, condition: bool, 
                     string_true: str, string_false: str,
                     int_true: int, int_false: int,
                     float_true: float, float_false: float,
                     image_true=None, image_false=None,
                     any_true=None, any_false=None) -> Tuple[str, int, float, Any, Any]:
        """
        根据条件分配值
        
        Args:
            condition: 布尔条件
            string_true: 条件为真时的字符串值
            string_false: 条件为假时的字符串值
            int_true: 条件为真时的整数值
            int_false: 条件为假时的整数值
            float_true: 条件为真时的浮点数值
            float_false: 条件为假时的浮点数值
            image_true: 条件为真时的图像值
            image_false: 条件为假时的图像值
            any_true: 条件为真时的任意类型值
            any_false: 条件为假时的任意类型值
            
        Returns:
            tuple: (字符串值, 整数值, 浮点数值, 图像值, 任意类型值)
        """
        try:
            if condition:
                # 条件为真时返回真值
                result_string = str(string_true) if string_true is not None else ""
                result_int = int(int_true) if int_true is not None else 0
                result_float = float(float_true) if float_true is not None else 0.0
                result_image = image_true if image_true is not None else None
                result_any = any_true if any_true is not None else None
            else:
                # 条件为假时返回假值
                result_string = str(string_false) if string_false is not None else ""
                result_int = int(int_false) if int_false is not None else 0
                result_float = float(float_false) if float_false is not None else 0.0
                result_image = image_false if image_false is not None else None
                result_any = any_false if any_false is not None else None
            
            return (result_string, result_int, result_float, result_image, result_any)
            
        except Exception as e:
            print(f"❌ [AutoFlowConditionAssignment] Error in value assignment: {str(e)}")
            # 返回默认值
            return ("", 0, 0.0, None, None) 