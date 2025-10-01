import os
import sys
import time

def log(msg):
    with open('ui_gen_log.txt', 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def generate_main_window():
    log("Starting extraction...")
    try:
        with open('multi.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        log(f"Read {len(lines)} lines.")

        # Extract parts
        header = ''.join(lines[:13])
        imports = "from .drop_area import SingleDropArea, MultiDropArea\n\n"
        image_utils = ''.join(lines[15:98])
        multi_window = ''.join(lines[552:1689])

        content = header + imports + image_utils + '\n\n' + multi_window

        temp_path = 'ui/main_window_temp.py'
        target_path = 'ui/main_window.py'

        log(f"Writing to {temp_path}...")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log("Replacing target file...")
        if os.path.exists(target_path):
            os.remove(target_path)
        
        os.rename(temp_path, target_path)
        log("Success!")
    except Exception as e:
        log(f"Error: {e}")

if __name__ == "__main__":
    generate_main_window()
