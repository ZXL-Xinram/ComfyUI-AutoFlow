"""
Condition checker node - 提供条件判断功能
"""

from typing import Tuple
from comfy.comfy_types import IO

class AutoFlowConditionChecker:
    """
    条件判断节点
    
    功能: 根据用户选择的数据类型和条件进行判断
    输入: 可选择的String、Int、Float类型数据和比较条件
    输出: Boolean结果
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data_type": (["String", "Int", "Float"], {
                    "default": "String"
                }),
                "condition": (["equals", "contains", "not_equals", "greater_than", "greater_or_equal"], {
                    "default": "equals"
                }),
            },
            "optional": {
                "string1": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "First string value"
                }),
                "string2": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Second string value"
                }),
                "int1": ("INT", {
                    "default": 0,
                    "min": -999999,
                    "max": 999999,
                    "step": 1
                }),
                "int2": ("INT", {
                    "default": 0,
                    "min": -999999,
                    "max": 999999,
                    "step": 1
                }),
                "float1": ("FLOAT", {
                    "default": 0.0,
                    "min": -999999.0,
                    "max": 999999.0,
                    "step": 0.01
                }),
                "float2": ("FLOAT", {
                    "default": 0.0,
                    "min": -999999.0,
                    "max": 999999.0,
                    "step": 0.01
                }),
            }
        }
    
    RETURN_TYPES = (IO.BOOLEAN,)
    RETURN_NAMES = ("result",)
    FUNCTION = "check_condition"
    CATEGORY = "AutoFlow/Utilities"
    
    @classmethod
    def IS_CHANGED(cls, data_type, condition, **kwargs):
        """
        确保节点在输入变化时自动更新
        通过返回输入参数的组合来检测变化
        """
        # 构建用于检测变化的字符串
        change_key = f"{data_type}_{condition}"
        
        # 根据数据类型添加相应的输入值
        if data_type == "String":
            string1 = kwargs.get("string1", "")
            string2 = kwargs.get("string2", "")
            change_key += f"_{string1}_{string2}"
        elif data_type == "Int":
            int1 = kwargs.get("int1", 0)
            int2 = kwargs.get("int2", 0)
            change_key += f"_{int1}_{int2}"
        elif data_type == "Float":
            float1 = kwargs.get("float1", 0.0)
            float2 = kwargs.get("float2", 0.0)
            change_key += f"_{float1}_{float2}"
        
        return change_key
    
    def check_condition(self, data_type: str, condition: str, 
                       string1: str = "", string2: str = "",
                       int1: int = 0, int2: int = 0,
                       float1: float = 0.0, float2: float = 0.0) -> Tuple[bool]:
        """
        执行条件判断
        
        Args:
            data_type: 数据类型选择 (String/Int/Float)
            condition: 条件类型
            string1, string2: 字符串输入
            int1, int2: 整数输入
            float1, float2: 浮点数输入
            
        Returns:
            tuple: (判断结果,)
        """
        try:
            if data_type == "String":
                # 字符串条件判断
                result = self._check_string_condition(string1, string2, condition)
            elif data_type == "Int":
                # 整数条件判断
                result = self._check_numeric_condition(int1, int2, condition)
            elif data_type == "Float":
                # 浮点数条件判断
                result = self._check_numeric_condition(float1, float2, condition)
            else:
                # 未知数据类型
                result = False
                
            return (result,)
            
        except Exception as e:
            print(f"❌ [AutoFlowConditionChecker] Error in condition check: {str(e)}")
            return (False,)
    
    def _check_string_condition(self, str1: str, str2: str, condition: str) -> bool:
        """
        检查字符串条件
        
        Args:
            str1: 第一个字符串
            str2: 第二个字符串
            condition: 条件类型
            
        Returns:
            bool: 判断结果
        """
        # 确保输入是字符串类型
        str1 = str(str1) if str1 is not None else ""
        str2 = str(str2) if str2 is not None else ""
        
        if condition == "equals":
            return str1 == str2
        elif condition == "contains":
            # 修复contains逻辑：
            # 当String1和String2都为空时，返回true
            # 当String1不为空，而String2为空时，返回false
            if str1 == "" and str2 == "":
                return True
            elif str2 == "":
                return False
            else:
                return str2 in str1
        elif condition == "not_equals":
            return str1 != str2
        else:
            # 字符串不支持的条件
            print(f"⚠️ [AutoFlowConditionChecker] Unsupported condition '{condition}' for String type")
            return False
    
    def _check_numeric_condition(self, val1, val2, condition: str) -> bool:
        """
        检查数值条件
        
        Args:
            val1: 第一个数值
            val2: 第二个数值
            condition: 条件类型
            
        Returns:
            bool: 判断结果
        """
        try:
            if condition == "equals":
                return val1 == val2
            elif condition == "not_equals":
                return val1 != val2
            elif condition == "greater_than":
                return val1 > val2
            elif condition == "greater_or_equal":
                return val1 >= val2
            else:
                # 数值类型不支持的条件
                print(f"⚠️ [AutoFlowConditionChecker] Unsupported condition '{condition}' for numeric type")
                return False
        except Exception as e:
            print(f"❌ [AutoFlowConditionChecker] Error in numeric comparison: {str(e)}")
            return False 