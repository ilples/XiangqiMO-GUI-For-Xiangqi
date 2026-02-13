#!/usr/bin/env python
"""
XiangqiMO - Main entry point
Run this file from the root directory to start the application.
"""

import os
import sys
import runpy

def main():
    """
    Launch XiangqiMO from the src directory.
    """
    # Get the directory where this script is located
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to src directory
    src_dir = os.path.join(root_dir, 'src')
    
    # Path to main script in src
    main_script = os.path.join(src_dir, 'main.py')
    
    # Check if src/main.py exists
    if not os.path.exists(main_script):
        print("Error: Could not find src/main.py")
        print(f"Looking in: {main_script}")
        input("Press Enter to exit...")
        return
    
    # Add src directory to Python path
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # Change working directory to src (optional, but helps with relative paths)
    os.chdir(src_dir)
    
    try:
        # Run the main script
        runpy.run_path(main_script, run_name='__main__')
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()