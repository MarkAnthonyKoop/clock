#!/usr/bin/env python3
"""
Automated test for click-through functionality
"""

import subprocess
import time
import pyautogui
import os

def test_clickthrough():
    print("Starting click-through test...")
    
    # Start the test window
    print("1. Starting test window...")
    proc = subprocess.Popen(['python3', '/home/tony/clickthrough/simple_window.py'])
    time.sleep(2)
    
    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()
    
    # Calculate where our test window should be (top-right)
    test_x = screen_width - 150  # Middle of our 200px window
    test_y = 150  # Middle of our 200px window
    
    print(f"2. Test window should be at approximately ({test_x}, {test_y})")
    
    # Take initial screenshot
    subprocess.run(['scrot', '/home/tony/clickthrough/before_click.png'])
    print("3. Screenshot saved: before_click.png")
    
    # Move mouse to test position
    print(f"4. Moving mouse to ({test_x}, {test_y})...")
    pyautogui.moveTo(test_x, test_y, duration=0.5)
    time.sleep(1)
    
    # Try single click
    print("5. Performing single click...")
    pyautogui.click()
    time.sleep(1)
    subprocess.run(['scrot', '/home/tony/clickthrough/after_single_click.png'])
    
    # Try right click
    print("6. Performing right click...")
    pyautogui.rightClick()
    time.sleep(1)
    subprocess.run(['scrot', '/home/tony/clickthrough/after_right_click.png'])
    
    # Try double click
    print("7. Performing double click...")
    pyautogui.doubleClick()
    time.sleep(1)
    subprocess.run(['scrot', '/home/tony/clickthrough/after_double_click.png'])
    
    print("\n8. Test complete! Check screenshots in ~/clickthrough/")
    print("   - If desktop menu appeared, click-through NOT working")
    print("   - If nothing happened, click-through IS working")
    
    # Kill the test window
    proc.terminate()
    
    return True

if __name__ == "__main__":
    test_clickthrough()