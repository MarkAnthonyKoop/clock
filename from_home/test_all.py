#!/usr/bin/env python3
"""
Comprehensive click-through test
"""

import subprocess
import time
import pyautogui
import os

def run_test(program_name, command):
    """Test a specific program for click-through"""
    print(f"\n{'='*60}")
    print(f"Testing: {program_name}")
    print(f"{'='*60}")
    
    # Start the program
    print(f"Starting {program_name}...")
    if isinstance(command, list):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for window to appear
    time.sleep(2)
    
    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()
    test_x = screen_width - 150  # Center of 200px window
    test_y = 150  # Center of 200px window
    
    # Take before screenshot
    screenshot_dir = f"/home/tony/clickthrough/{program_name.replace(' ', '_')}"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    before_path = f"{screenshot_dir}/before.png"
    subprocess.run(['scrot', before_path])
    print(f"Before screenshot: {before_path}")
    
    # Move mouse and click
    print(f"Moving mouse to ({test_x}, {test_y})...")
    pyautogui.moveTo(test_x, test_y, duration=0.5)
    time.sleep(0.5)
    
    # Try different click types
    tests = [
        ("single_click", lambda: pyautogui.click()),
        ("right_click", lambda: pyautogui.rightClick()),
        ("double_click", lambda: pyautogui.doubleClick()),
    ]
    
    results = {}
    for test_name, click_func in tests:
        print(f"  Testing {test_name}...")
        click_func()
        time.sleep(1)
        
        # Take screenshot
        screenshot_path = f"{screenshot_dir}/{test_name}.png"
        subprocess.run(['scrot', screenshot_path])
        
        # Check if desktop menu appeared (simple heuristic)
        # We'll manually review screenshots
        results[test_name] = screenshot_path
    
    # Terminate program
    proc.terminate()
    time.sleep(0.5)
    proc.kill()
    
    print(f"Results saved in {screenshot_dir}/")
    return results

def main():
    print("COMPREHENSIVE CLICK-THROUGH TESTING")
    print("====================================")
    
    # Kill any existing test windows
    subprocess.run(['pkill', '-f', 'clickthrough'], stderr=subprocess.DEVNULL)
    subprocess.run(['pkill', 'conky'], stderr=subprocess.DEVNULL)
    time.sleep(1)
    
    # Test programs
    tests = [
        ("C_XShape", "/home/tony/clickthrough/clickthrough"),
        ("Python_Tkinter", ["python3", "/home/tony/clickthrough/simple_window.py"]),
        ("Conky", "conky -c /home/tony/.config/conky/analog_clock.conf"),
    ]
    
    all_results = {}
    for name, command in tests:
        try:
            results = run_test(name, command)
            all_results[name] = results
        except Exception as e:
            print(f"Error testing {name}: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\nScreenshots saved for review:")
    for program, results in all_results.items():
        print(f"\n{program}:")
        for test_type, path in results.items():
            print(f"  - {test_type}: {path}")
    
    print("\n📝 Review screenshots to determine if click-through worked:")
    print("  ✅ Success = No desktop menu or window selection")
    print("  ❌ Failure = Desktop menu appeared or window was selected")
    
    # Now let's also check what the compositor is
    print("\n" + "="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    
    # Check compositor
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'mutter' in result.stdout:
        print("Compositor: Mutter (GNOME)")
    elif 'kwin' in result.stdout:
        print("Compositor: KWin (KDE)")
    elif 'xfwm' in result.stdout:
        print("Compositor: xfwm (XFCE)")
    elif 'compton' in result.stdout or 'picom' in result.stdout:
        print("Compositor: Compton/Picom")
    else:
        print("Compositor: Unknown/None")
    
    # Check if compositor bypass is needed
    print("\nChecking if compositor bypass helps...")
    subprocess.run(['xprop', '-root', '-f', '_NET_WM_BYPASS_COMPOSITOR', '32c', 
                   '-set', '_NET_WM_BYPASS_COMPOSITOR', '1'], stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()