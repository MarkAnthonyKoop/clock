#!/usr/bin/env python3
"""
Test: Circle with hole in middle using X11 input shapes
Research shows this should allow clicks in center to pass through
"""

from Xlib import X, display
from Xlib.ext import shape
import math

def create_circle_with_hole():
    # Connect to display
    d = display.Display()
    screen = d.screen()
    root = screen.root
    
    # Create window
    window = root.create_window(
        100, 100, 200, 200, 1,
        screen.root_depth,
        X.InputOutput,
        X.CopyFromParent,
        background_pixel=screen.white_pixel,
        override_redirect=1
    )
    
    window.set_wm_name("Circle Hole Test")
    window.map()
    d.sync()
    
    print("Window created. Testing shape extension...")
    
    # Create input shape: ring (circle with hole in middle)
    rectangles = []
    
    # Simple approach: create rectangles that form a ring
    center_x, center_y = 100, 100
    outer_radius = 80
    inner_radius = 40
    
    # Create ring by adding rectangles
    for y in range(200):
        for x in range(200):
            dist_from_center = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if inner_radius < dist_from_center <= outer_radius:
                rectangles.append((x, y, 1, 1))
    
    print(f"Created {len(rectangles)} rectangles for ring shape")
    
    # Apply input shape
    try:
        window.shape_rectangles(
            shape.SO.Set,
            shape.SK.Input,
            0, 0,
            rectangles
        )
        d.sync()
        print("Input shape applied successfully!")
        print("The center hole should be click-through")
        print("The ring area should capture clicks")
        
        # Keep window alive for testing
        input("Press Enter to close...")
        
    except Exception as e:
        print(f"Shape extension failed: {e}")
        print("Trying alternative method...")
        
        # Alternative: remove input completely for full click-through
        window.shape_mask(shape.SO.Set, shape.SK.Input, 0, 0, X.NONE)
        d.sync()
        print("Full click-through applied instead")
        input("Press Enter to close...")
    
    d.close()

if __name__ == "__main__":
    create_circle_with_hole()