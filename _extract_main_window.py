import os
import sys

try:
    print("Starting extraction...")
    with open('multi.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Read {len(lines)} lines from multi.py")

    # Header imports (lines 1-13)
    # Note: lines are 0-indexed in list, so line 1 is index 0.
    # Lines 1-13 correspond to indices 0-13 (slice [:13])
    header = ''.join(lines[:13])
    
    # Additional imports for the new module
    imports = "from .drop_area import SingleDropArea, MultiDropArea\n\n"
    
    # ImageUtils class (lines 16-98 in original file, check indices)
    # Line 16 is index 15.
    # Line 98 is index 97.
    # Let's verify context.
    # Line 16: class ImageUtils:
    # Line 99: class DropZone(QLabel): -> We stop before this.
    image_utils = ''.join(lines[15:98])
    
    # MultiWindow class (lines 553-1689)
    # Line 553: class MultiWindow(QMainWindow): -> index 552
    # Line 1690: def run_multi_mode(): -> We stop before this.
    multi_window = ''.join(lines[552:1689])

    content = header + imports + image_utils + '\n\n' + multi_window

    with open('ui/main_window.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Successfully wrote {len(content)} characters to ui/main_window.py")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
