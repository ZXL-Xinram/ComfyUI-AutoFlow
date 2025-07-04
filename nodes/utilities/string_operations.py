"""
String operation nodes - Provides string concatenation, replacement, splitting and other functions
"""

import re
from typing import Tuple, List

class StringConcatenator:
    """
    String concatenation node
    
    Function: Concatenate two strings into one
    Input: Two strings
    Output: Concatenated string
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string_a": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "First string"
                }),
                "string_b": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Second string"
                }),
                "separator": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Separator (optional)"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "concatenate"
    CATEGORY = "AutoFlow/Utilities"
    
    def concatenate(self, string_a: str, string_b: str, separator: str = "") -> Tuple[str]:
        """
        Concatenate two strings
        
        Args:
            string_a: First string
            string_b: Second string
            separator: Separator
            
        Returns:
            tuple: (Concatenated string,)
        """
        # Handle None values
        string_a = str(string_a) if string_a is not None else ""
        string_b = str(string_b) if string_b is not None else ""
        separator = str(separator) if separator is not None else ""
        
        # Concatenate strings
        result = string_a + separator + string_b
        
        return (result,)


class StringMultiConcatenator:
    """
    Multi-string concatenation node
    
    Function: Concatenate multiple strings
    Input: Multiple string inputs
    Output: Concatenated string
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "separator": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Separator (optional)"
                }),
            },
            "optional": {
                "string_1": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "String 1"
                }),
                "string_2": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "String 2"
                }),
                "string_3": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "String 3"
                }),
                "string_4": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "String 4"
                }),
                "string_5": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "String 5"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "multi_concatenate"
    CATEGORY = "AutoFlow/Utilities"
    
    def multi_concatenate(self, separator: str = "", **kwargs) -> Tuple[str]:
        """
        Concatenate multiple strings
        
        Args:
            separator: Separator
            **kwargs: Dynamic string parameters
            
        Returns:
            tuple: (Concatenated string,)
        """
        # Collect all non-empty strings
        strings = []
        for i in range(1, 6):  # string_1 to string_5
            key = f"string_{i}"
            if key in kwargs and kwargs[key] is not None:
                value = str(kwargs[key]).strip()
                if value:  # Only add non-empty strings
                    strings.append(value)
        
        # Concatenate strings
        result = separator.join(strings)
        
        return (result,)


class StringReplacer:
    """
    String replacement node
    
    Function: Replace specified content in strings
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Text to process"
                }),
                "search": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Content to find"
                }),
                "replace": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Content to replace with"
                }),
                "use_regex": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Whether to use regular expressions"
                }),
                "case_sensitive": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Whether to be case sensitive"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("result", "count")
    FUNCTION = "replace_text"
    CATEGORY = "AutoFlow/Utilities"
    
    def replace_text(self, text: str, search: str, replace: str, 
                    use_regex: bool = False, case_sensitive: bool = True) -> Tuple[str, int]:
        """
        Replace content in strings
        
        Args:
            text: Text to process
            search: Content to find
            replace: Content to replace with
            use_regex: Whether to use regular expressions
            case_sensitive: Whether to be case sensitive
            
        Returns:
            tuple: (Replaced text, replacement count)
        """
        if not text or not search:
            return (text, 0)
        
        count = 0
        result = text
        
        try:
            if use_regex:
                # Use regular expression replacement
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search, flags)
                result, count = pattern.subn(replace, text)
            else:
                # Normal string replacement
                if case_sensitive:
                    # Case sensitive
                    count = text.count(search)
                    result = text.replace(search, replace)
                else:
                    # Case insensitive
                    # Use regex for case-insensitive replacement
                    pattern = re.compile(re.escape(search), re.IGNORECASE)
                    result, count = pattern.subn(replace, text)
        except Exception as e:
            # If regex error, return original text
            print(f"String replacement error: {e}")
            return (text, 0)
        
        return (result, count)


class StringSplitter:
    """
    String splitting node
    
    Function: Split strings by delimiter into multiple parts
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Text to split"
                }),
                "delimiter": ("STRING", {
                    "multiline": False,
                    "default": ",",
                    "placeholder": "Delimiter"
                }),
                "max_splits": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 100,
                    "tooltip": "Maximum number of splits, -1 for unlimited"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("parts", "count")
    FUNCTION = "split_text"
    CATEGORY = "AutoFlow/Utilities"
    OUTPUT_IS_LIST = (True, False)
    
    def split_text(self, text: str, delimiter: str, max_splits: int = -1) -> Tuple[List[str], int]:
        """
        Split string
        
        Args:
            text: Text to split
            delimiter: Delimiter
            max_splits: Maximum number of splits
            
        Returns:
            tuple: (List of split parts, split count)
        """
        if not text:
            return ([], 0)
        
        if max_splits == -1:
            parts = text.split(delimiter)
        else:
            parts = text.split(delimiter, max_splits)
        
        # Remove whitespace
        parts = [part.strip() for part in parts]
        
        return (parts, len(parts))


class StringFormatter:
    """
    String formatting node
    
    Function: Format strings using Python string formatting syntax
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Template string, e.g.: {name}_{index:03d}.png"
                }),
            },
            "optional": {
                "value_1": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Value 1"
                }),
                "value_2": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Value 2"
                }),
                "value_3": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Value 3"
                }),
                "value_4": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Value 4"
                }),
                "value_5": ("STRING", {
                    "multiline": False,
                    "default": "",
                    "placeholder": "Value 5"
                }),
                "number_1": ("INT", {
                    "default": 0,
                    "tooltip": "Number value 1"
                }),
                "number_2": ("INT", {
                    "default": 0,
                    "tooltip": "Number value 2"
                }),
                "number_3": ("INT", {
                    "default": 0,
                    "tooltip": "Number value 3"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "format_string"
    CATEGORY = "AutoFlow/Utilities"
    
    def format_string(self, template: str, **kwargs) -> Tuple[str]:
        """
        Format string
        
        Args:
            template: Template string
            **kwargs: Formatting parameters
            
        Returns:
            tuple: (Formatted string,)
        """
        if not template:
            return ("",)
        
        try:
            # Prepare formatting arguments
            format_args = {}
            
            # Add string values
            for i in range(1, 6):
                key = f"value_{i}"
                if key in kwargs and kwargs[key] is not None:
                    format_args[f"value{i}"] = str(kwargs[key])
                    format_args[f"v{i}"] = str(kwargs[key])  # Short alias
            
            # Add number values
            for i in range(1, 4):
                key = f"number_{i}"
                if key in kwargs and kwargs[key] is not None:
                    format_args[f"number{i}"] = kwargs[key]
                    format_args[f"n{i}"] = kwargs[key]  # Short alias
            
            # Format string
            result = template.format(**format_args)
            
        except Exception as e:
            print(f"String formatting error: {e}")
            result = template  # If formatting fails, return original template
        
        return (result,)


class StringCase:
    """
    String case conversion node
    
    Function: Convert string case
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Text to convert"
                }),
                "case_type": ([
                    "upper",        # All uppercase
                    "lower",        # All lowercase
                    "title",        # Title case
                    "capitalize",   # First letter uppercase
                    "swapcase",     # Swap case
                ], {
                    "default": "lower"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "convert_case"
    CATEGORY = "AutoFlow/Utilities"
    
    def convert_case(self, text: str, case_type: str) -> Tuple[str]:
        """
        Convert string case
        
        Args:
            text: Text to convert
            case_type: Conversion type
            
        Returns:
            tuple: (Converted text,)
        """
        if not text:
            return ("",)
        
        if case_type == "upper":
            result = text.upper()
        elif case_type == "lower":
            result = text.lower()
        elif case_type == "title":
            result = text.title()
        elif case_type == "capitalize":
            result = text.capitalize()
        elif case_type == "swapcase":
            result = text.swapcase()
        else:
            result = text
        
        return (result,) 