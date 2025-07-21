"""
ComfyUI-AutoFlow Custom Node Package

A collection of ComfyUI custom nodes focused on path processing and string operations
"""

import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import node classes
try:
    from .nodes.utilities.path_parser import PathParser, PathJoiner, PathValidator
    from .nodes.utilities.string_operations import (
        StringConcatenator, 
        StringMultiConcatenator,
        StringReplacer,
        StringSplitter,
        StringFormatter,
        StringCase
    )
    from .nodes.utilities.timestamp_generator import TimestampGenerator, TimestampFormatter
    from .nodes.utilities.condition_checker import AutoFlowConditionChecker
    from .nodes.utilities.condition_assignment import AutoFlowConditionAssignment
    from .nodes.image.load_image_with_background import AutoFlowLoadImageWithBackground
    from .nodes.image.load_images_for_loop_with_background import AutoFlowLoadImagesForLoopWithBackground
    
    # Node class mappings - ComfyUI uses this to identify and load nodes
    NODE_CLASS_MAPPINGS = {
        # Path processing nodes
        "AutoFlowPathParser": PathParser,
        "AutoFlowPathJoiner": PathJoiner,
        "AutoFlowPathValidator": PathValidator,
        
        # String processing nodes
        "AutoFlowStringConcat": StringConcatenator,
        "AutoFlowStringMultiConcat": StringMultiConcatenator,
        "AutoFlowStringReplace": StringReplacer,
        "AutoFlowStringSplit": StringSplitter,
        "AutoFlowStringFormat": StringFormatter,
        "AutoFlowStringCase": StringCase,
        
        # Timestamp processing nodes
        "AutoFlowTimestampGenerator": TimestampGenerator,
        "AutoFlowTimestampFormatter": TimestampFormatter,
        
        # Condition processing nodes
        "AutoFlowConditionChecker": AutoFlowConditionChecker,
        "AutoFlowConditionAssignment": AutoFlowConditionAssignment,
        
        # Image processing nodes
        "AutoFlowLoadImageWithBackground": AutoFlowLoadImageWithBackground,
        "AutoFlowLoadImagesForLoopWithBackground": AutoFlowLoadImagesForLoopWithBackground,
    }
    
    # Display name mappings - friendly names shown in ComfyUI interface
    NODE_DISPLAY_NAME_MAPPINGS = {
        # Path processing nodes
        "AutoFlowPathParser": "Path Parser",
        "AutoFlowPathJoiner": "Path Joiner",
        "AutoFlowPathValidator": "Path Validator",
        
        # String processing nodes
        "AutoFlowStringConcat": "String Concatenator",
        "AutoFlowStringMultiConcat": "Multi String Concatenator",
        "AutoFlowStringReplace": "String Replacer",
        "AutoFlowStringSplit": "String Splitter",
        "AutoFlowStringFormat": "String Formatter",
        "AutoFlowStringCase": "String Case Converter",
        
        # Timestamp processing nodes
        "AutoFlowTimestampGenerator": "Timestamp Generator",
        "AutoFlowTimestampFormatter": "Timestamp Formatter",
        
        # Condition processing nodes
        "AutoFlowConditionChecker": "Condition Checker",
        "AutoFlowConditionAssignment": "Condition Assignment",
        
        # Image processing nodes
        "AutoFlowLoadImageWithBackground": "Load Image with Background",
        "AutoFlowLoadImagesForLoopWithBackground": "Load Images For Loop with Background",
    }
    
    # Successfully loaded nodes list
    LOADED_NODES = list(NODE_CLASS_MAPPINGS.keys())
    
    print(f"✅ [ComfyUI-AutoFlow] Successfully loaded {len(LOADED_NODES)} nodes:")
    print("   Path Processing Nodes:")
    print("   • Path Parser (AutoFlowPathParser)")
    print("   • Path Joiner (AutoFlowPathJoiner)")
    print("   • Path Validator (AutoFlowPathValidator)")
    print("   String Processing Nodes:")
    print("   • String Concatenator (AutoFlowStringConcat)")
    print("   • Multi String Concatenator (AutoFlowStringMultiConcat)")
    print("   • String Replacer (AutoFlowStringReplace)")
    print("   • String Splitter (AutoFlowStringSplit)")
    print("   • String Formatter (AutoFlowStringFormat)")
    print("   • String Case Converter (AutoFlowStringCase)")
    print("   Timestamp Processing Nodes:")
    print("   • Timestamp Generator (AutoFlowTimestampGenerator)")
    print("   • Timestamp Formatter (AutoFlowTimestampFormatter)")
    print("   Condition Processing Nodes:")
    print("   • Condition Checker (AutoFlowConditionChecker)")
    print("   • Condition Assignment (AutoFlowConditionAssignment)")
    print("   Image Processing Nodes:")
    print("   • Load Image with Background (AutoFlowLoadImageWithBackground)")
    print("   • Load Images For Loop with Background (AutoFlowLoadImagesForLoopWithBackground)")
    
except Exception as e:
    print(f"❌ [ComfyUI-AutoFlow] Failed to load nodes: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Create empty mappings to avoid ComfyUI errors
    NODE_CLASS_MAPPINGS = {}
    NODE_DISPLAY_NAME_MAPPINGS = {}
    LOADED_NODES = []

# Web directory (if there are frontend extensions)
WEB_DIRECTORY = "./web"

# Package information
__version__ = "2.1.0"
__author__ = "ComfyUI-AutoFlow"
__description__ = "ComfyUI path processing, string operation and timestamp generation node collection"

# Print loading information
print(f"🚀 [ComfyUI-AutoFlow] v{__version__} initialization complete")
print(f"📁 Node location: {current_dir}")
if LOADED_NODES:
    print(f"💡 Usage: Look for 'AutoFlow' category in the node menu")
    print(f"🔧 Features: Path parsing, string operations, and filesystem-safe timestamp generation")
else:
    print("⚠️ No nodes were successfully loaded, please check error messages")

# Export variables for ComfyUI
__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS", 
    "WEB_DIRECTORY"
]
