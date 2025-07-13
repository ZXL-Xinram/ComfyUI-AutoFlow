"""
时间戳生成器节点
提供多种文件系统安全的时间格式
"""

import datetime
import time


class TimestampGenerator:
    """
    生成当前时间戳的节点
    提供多种格式选择，所有格式都适用于文件系统路径
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format": ([
                    "YYYYMMDDHHMMSS",      # 20250705014305
                    "YYYY-MM-DD_HH-MM-SS", # 2025-07-05_01-43-05
                    "YYYYMMDD_HHMMSS",     # 20250705_014305
                    "YYYY-MM-DD",          # 2025-07-05
                    "YYYYMMDD",            # 20250705
                    "HHMMSS",              # 014305
                    "HH-MM-SS",            # 01-43-05
                    "timestamp_ms",        # 1720136585123
                    "timestamp_s",         # 1720136585
                    "compact",             # 250705014305 (short year)
                    "readable",            # 2025Jul05_014305
                    "iso_safe",            # 2025-07-05T01-43-05
                ], {
                    "default": "YYYYMMDDHHMMSS"
                }),
            },
            "optional": {
                "custom_format": ("STRING", {
                    "default": "",
                    "tooltip": "自定义格式字符串，使用Python strftime格式"
                }),
                "use_utc": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否使用UTC时间"
                }),
                "add_milliseconds": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否添加毫秒"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("timestamp",)
    FUNCTION = "generate_timestamp"
    CATEGORY = "AutoFlow/utilities"
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """
        告诉ComfyUI这个节点总是需要重新执行
        因为每次都需要生成新的时间戳
        """
        return float("nan")
    
    def generate_timestamp(self, format, custom_format="", use_utc=False, add_milliseconds=False):
        """
        生成时间戳
        
        Args:
            format: 预设格式
            custom_format: 自定义格式字符串
            use_utc: 是否使用UTC时间
            add_milliseconds: 是否添加毫秒
            
        Returns:
            tuple: (时间戳字符串,)
        """
        # 获取当前时间
        if use_utc:
            now = datetime.datetime.utcnow()
        else:
            now = datetime.datetime.now()
        
        # 如果指定了自定义格式且不为空，优先使用自定义格式
        if custom_format and custom_format.strip():
            try:
                timestamp = now.strftime(custom_format.strip())
                if add_milliseconds:
                    ms = int(now.microsecond / 1000)
                    timestamp += f"{ms:03d}"
                return (timestamp,)
            except Exception as e:
                # 如果自定义格式错误，回退到默认格式
                print(f"Custom format error: {e}, falling back to default")
        
        # 使用预设格式
        if format == "YYYYMMDDHHMMSS":
            timestamp = now.strftime("%Y%m%d%H%M%S")
        elif format == "YYYY-MM-DD_HH-MM-SS":
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
        elif format == "YYYYMMDD_HHMMSS":
            timestamp = now.strftime("%Y%m%d_%H%M%S")
        elif format == "YYYY-MM-DD":
            timestamp = now.strftime("%Y-%m-%d")
        elif format == "YYYYMMDD":
            timestamp = now.strftime("%Y%m%d")
        elif format == "HHMMSS":
            timestamp = now.strftime("%H%M%S")
        elif format == "HH-MM-SS":
            timestamp = now.strftime("%H-%M-%S")
        elif format == "timestamp_ms":
            timestamp = str(int(time.time() * 1000))
        elif format == "timestamp_s":
            timestamp = str(int(time.time()))
        elif format == "compact":
            timestamp = now.strftime("%y%m%d%H%M%S")
        elif format == "readable":
            timestamp = now.strftime("%Y%b%d_%H%M%S")
        elif format == "iso_safe":
            timestamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        else:
            # 默认格式
            timestamp = now.strftime("%Y%m%d%H%M%S")
        
        # 添加毫秒
        if add_milliseconds and format not in ["timestamp_ms", "timestamp_s"]:
            ms = int(now.microsecond / 1000)
            timestamp += f"{ms:03d}"
        
        return (timestamp,)


class TimestampFormatter:
    """
    格式化指定时间戳的节点
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "timestamp": ("STRING", {
                    "default": "",
                    "tooltip": "输入时间戳字符串，支持多种格式"
                }),
                "input_format": ("STRING", {
                    "default": "%Y-%m-%d %H:%M:%S",
                    "tooltip": "输入时间戳的格式"
                }),
                "output_format": ([
                    "YYYYMMDDHHMMSS",
                    "YYYY-MM-DD_HH-MM-SS",
                    "YYYYMMDD_HHMMSS",
                    "YYYY-MM-DD",
                    "YYYYMMDD",
                    "readable",
                    "iso_safe",
                ], {
                    "default": "YYYYMMDDHHMMSS"
                }),
            },
            "optional": {
                "custom_output_format": ("STRING", {
                    "default": "",
                    "tooltip": "自定义输出格式，使用Python strftime格式"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("formatted_timestamp",)
    FUNCTION = "format_timestamp"
    CATEGORY = "AutoFlow/utilities"
    
    def format_timestamp(self, timestamp, input_format, output_format, custom_output_format=""):
        """
        格式化时间戳
        
        Args:
            timestamp: 输入时间戳字符串
            input_format: 输入格式
            output_format: 输出格式
            custom_output_format: 自定义输出格式
            
        Returns:
            tuple: (格式化后的时间戳,)
        """
        try:
            # 解析输入时间戳
            dt = datetime.datetime.strptime(timestamp, input_format)
            
            # 使用自定义格式（如果提供）
            if custom_output_format and custom_output_format.strip():
                return (dt.strftime(custom_output_format.strip()),)
            
            # 使用预设格式
            if output_format == "YYYYMMDDHHMMSS":
                result = dt.strftime("%Y%m%d%H%M%S")
            elif output_format == "YYYY-MM-DD_HH-MM-SS":
                result = dt.strftime("%Y-%m-%d_%H-%M-%S")
            elif output_format == "YYYYMMDD_HHMMSS":
                result = dt.strftime("%Y%m%d_%H%M%S")
            elif output_format == "YYYY-MM-DD":
                result = dt.strftime("%Y-%m-%d")
            elif output_format == "YYYYMMDD":
                result = dt.strftime("%Y%m%d")
            elif output_format == "readable":
                result = dt.strftime("%Y%b%d_%H%M%S")
            elif output_format == "iso_safe":
                result = dt.strftime("%Y-%m-%dT%H-%M-%S")
            else:
                result = dt.strftime("%Y%m%d%H%M%S")
            
            return (result,)
            
        except Exception as e:
            print(f"Timestamp format error: {e}")
            return (timestamp,)  # 返回原始输入 