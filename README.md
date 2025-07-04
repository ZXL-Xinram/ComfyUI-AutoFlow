# ComfyUI-AutoFlow

A collection of utility nodes for ComfyUI focused on path processing and string operations.

## Features

### Path Processing Nodes
- **Path Parser**: Extract directory, filename, and extension from file paths
- **Path Joiner**: Combine directory, filename, and extension into a complete path
- **Path Validator**: Validate path format and check if paths exist

### String Processing Nodes
- **String Concatenator**: Join two strings with optional separator
- **Multi String Concatenator**: Join multiple strings with separator
- **String Replacer**: Replace text with regex and case-sensitivity options
- **String Splitter**: Split strings by delimiter into multiple parts
- **String Formatter**: Format strings using Python format syntax
- **String Case Converter**: Convert string case (upper, lower, title, etc.)

## Installation

1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/your-username/ComfyUI-AutoFlow.git
   ```

3. Restart ComfyUI

## Usage

After installation, you can find all AutoFlow nodes in the node menu under the "AutoFlow" category.

### Path Processing Example

1. **Path Parser**: 
   - Input: `C:\workspace\hello.png`
   - Output: Directory: `C:\workspace\`, Filename: `hello`, Extension: `.png`

2. **Path Joiner**:
   - Input: Directory: `C:\workspace\`, Filename: `hello`, Extension: `.png`
   - Output: `C:\workspace\hello.png`

### String Processing Example

1. **String Concatenator**:
   - Input: String A: `Hello`, String B: `World`, Separator: ` `
   - Output: `Hello World`

2. **String Formatter**:
   - Input: Template: `{v1}_{n1:03d}.png`, Value 1: `image`, Number 1: `42`
   - Output: `image_042.png`

## Node Categories

All nodes are organized under the **AutoFlow** category in ComfyUI:

- **AutoFlow/Utilities**
  - Path Parser
  - Path Joiner
  - Path Validator
  - String Concatenator
  - Multi String Concatenator
  - String Replacer
  - String Splitter
  - String Formatter
  - String Case Converter

## Requirements

- ComfyUI
- Python 3.7+

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

