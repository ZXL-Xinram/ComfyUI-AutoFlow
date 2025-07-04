"""
路径解析节点 - 提取路径的目录、文件名和后缀名
"""

import os
import re
from typing import Tuple

class PathParser:
    """
    路径解析节点
    
    功能：从完整路径中提取目录、文件名和后缀名
    输入：完整路径字符串（如 C:\workspace\hello.png）
    输出：目录路径、文件名、后缀名
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Enter full path, e.g.: C:\\workspace\\hello.png"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("directory", "filename", "extension")
    FUNCTION = "parse_path"
    CATEGORY = "AutoFlow/Utilities"
    
    def parse_path(self, path: str) -> Tuple[str, str, str]:
        """
        解析路径，提取目录、文件名和后缀名
        
        Args:
            path: 完整路径字符串
            
        Returns:
            tuple: (目录路径, 文件名, 后缀名)
        """
        # 处理空路径
        if not path or not path.strip():
            return ("", "", "")
        
        # 清理路径
        path = path.strip()
        
        # 标准化路径分隔符
        path = os.path.normpath(path)
        
        # 分离目录和文件名
        directory, filename_with_ext = os.path.split(path)
        
        # 如果目录不为空，确保以路径分隔符结尾
        if directory and not directory.endswith(os.sep):
            directory += os.sep
        
        # 分离文件名和后缀名
        if filename_with_ext:
            # 使用splitext分离文件名和后缀
            filename, extension = os.path.splitext(filename_with_ext)
        else:
            filename = ""
            extension = ""
        
        return (directory, filename, extension)


class PathJoiner:
    """
    路径拼接节点
    
    功能：将目录、文件名和后缀名拼接成完整路径
    输入：目录路径、文件名、后缀名
    输出：完整路径
    """
    
    @classmethod 
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Directory path, e.g.: C:\\workspace\\"
                }),
                "filename": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Filename, e.g.: hello"
                }),
                "extension": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "File extension, e.g.: .png"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("path",)
    FUNCTION = "join_path"
    CATEGORY = "AutoFlow/Utilities"
    
    def join_path(self, directory: str, filename: str, extension: str) -> Tuple[str]:
        """
        拼接路径
        
        Args:
            directory: 目录路径
            filename: 文件名
            extension: 后缀名
            
        Returns:
            tuple: (完整路径,)
        """
        # 处理空值
        directory = directory.strip() if directory else ""
        filename = filename.strip() if filename else ""
        extension = extension.strip() if extension else ""
        
        # 如果文件名为空，返回空路径
        if not filename:
            return ("",)
        
        # 确保后缀名以点开头
        if extension and not extension.startswith('.'):
            extension = '.' + extension
        
        # 拼接文件名和后缀名
        filename_with_ext = filename + extension
        
        # 拼接完整路径
        if directory:
            # 确保目录以路径分隔符结尾
            if not directory.endswith(os.sep) and not directory.endswith('/'):
                directory += os.sep
            full_path = os.path.join(directory, filename_with_ext)
        else:
            full_path = filename_with_ext
        
        # 标准化路径
        full_path = os.path.normpath(full_path)
        
        return (full_path,)


class PathValidator:
    """
    路径验证节点
    
    功能：验证路径是否有效、是否存在等
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Path to validate"
                }),
                "check_existence": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Whether to check if path exists"
                }),
            }
        }
    
    RETURN_TYPES = ("BOOLEAN", "BOOLEAN", "STRING")
    RETURN_NAMES = ("is_valid", "exists", "error_message")
    FUNCTION = "validate_path"
    CATEGORY = "AutoFlow/Utilities"
    
    def validate_path(self, path: str, check_existence: bool = True) -> Tuple[bool, bool, str]:
        """
        验证路径
        
        Args:
            path: 路径字符串
            check_existence: 是否检查路径存在性
            
        Returns:
            tuple: (是否有效, 是否存在, 错误信息)
        """
        if not path or not path.strip():
            return (False, False, "Path is empty")
        
        path = path.strip()
        error_message = ""
        
        # 检查路径格式是否有效
        try:
            # 尝试标准化路径
            normalized_path = os.path.normpath(path)
            is_valid = True
        except Exception as e:
            is_valid = False
            error_message = f"Invalid path format: {str(e)}"
            return (is_valid, False, error_message)
        
        # 检查路径是否存在
        exists = False
        if check_existence:
            exists = os.path.exists(path)
            if not exists:
                error_message = "Path does not exist"
        
        return (is_valid, exists, error_message) 