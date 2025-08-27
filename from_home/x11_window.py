#!/usr/bin/env python3
"""
Pure X11 window for testing click-through
"""

from Xlib import X, display, Xatom
from Xlib.ext import shape
import time
import subprocess

class X11ClickThroughWindow:
    def __init__(self):
        # Connect to X server
        self.display = display.Display()
        self.screen = self.display.screen()
        self.root = self.screen.root
        
        # Get screen dimensions
        screen_width = self.screen.width_in_pixels
        screen_height = self.screen.height_in_pixels
        
        # Window dimensions and position (top-right)
        self.width = 200
        self.height = 200
        self.x = screen_width - self.width - 50
        self.y = 50
        
        # Create window
        self.window = self.root.create_window(
            self.x, self.y, self.width, self.height, 1,
            self.screen.root_depth,
            X.InputOutput,
            X.CopyFromParent,
            
            # Window attributes
            background_pixel=self.screen.white_pixel,
            override_redirect=1,  # No window manager decorations
            event_mask=(X.ExposureMask | X.StructureNotifyMask)
        )
        
        # Set window properties
        self.window.set_wm_name("X11 ClickThrough Test")
        self.window.set_wm_class("clickthrough", "ClickThrough")
        
        # Make it stay on top using EWMH hints
        self.set_window_type_utility()
        self.set_always_on_top()
        
        # Map (show) the window
        self.window.map()
        self.display.sync()
        
        print(f"Created X11 window at ({self.x}, {self.y}) size {self.width}x{self.height}")
        print(f"Window ID: 0x{self.window.id:x}")
        
        # Try different methods to achieve click-through
        self.method = 1
        
    def set_window_type_utility(self):
        """Set window type to utility"""
        atom = self.display.intern_atom('_NET_WM_WINDOW_TYPE')
        utility_atom = self.display.intern_atom('_NET_WM_WINDOW_TYPE_UTILITY')
        
        self.window.change_property(
            atom,
            Xatom.ATOM,
            32,
            [utility_atom]
        )
        
    def set_always_on_top(self):
        """Set window to be always on top"""
        state_atom = self.display.intern_atom('_NET_WM_STATE')
        above_atom = self.display.intern_atom('_NET_WM_STATE_ABOVE')
        
        self.window.change_property(
            state_atom,
            Xatom.ATOM,
            32,
            [above_atom]
        )
        
    def make_clickthrough_method1(self):
        """Method 1: Remove input shape completely"""
        print("Method 1: Removing input shape...")
        try:
            self.window.shape_mask(
                shape.SO.Set,
                shape.SK.Input,
                0, 0,
                X.NONE
            )
            self.display.sync()
            print("  - Input shape removed")
            return True
        except Exception as e:
            print(f"  - Failed: {e}")
            return False
            
    def make_clickthrough_method2(self):
        """Method 2: Set empty input region"""
        print("Method 2: Setting empty input region...")
        try:
            # Create an empty region (no rectangles = no input area)
            self.window.shape_rectangles(
                shape.SO.Set,
                shape.SK.Input,
                0, 0,
                []  # Empty list of rectangles
            )
            self.display.sync()
            print("  - Empty input region set")
            return True
        except Exception as e:
            print(f"  - Failed: {e}")
            return False
            
    def make_clickthrough_method3(self):
        """Method 3: Set input shape to a 1x1 pixel region"""
        print("Method 3: Setting minimal input region...")
        try:
            # Set input to just 1 pixel in corner
            self.window.shape_rectangles(
                shape.SO.Set,
                shape.SK.Input,
                0, 0,
                [(0, 0, 1, 1)]  # Just 1 pixel
            )
            self.display.sync()
            print("  - Minimal input region set")
            return True
        except Exception as e:
            print(f"  - Failed: {e}")
            return False
    
    def draw_content(self):
        """Draw something visible on the window"""
        gc = self.window.create_gc(
            foreground=self.screen.black_pixel,
            background=self.screen.white_pixel
        )
        
        # Draw red rectangle
        self.window.fill_rectangle(gc, 0, 0, self.width, self.height)
        
        # Draw text
        self.window.draw_text(gc, 50, 100, b"ClickThrough Test")
        
        self.display.sync()
        
    def run(self):
        """Run the window and test different methods"""
        self.draw_content()
        
        print("\nTrying different click-through methods:")
        
        # Try each method
        methods = [
            self.make_clickthrough_method1,
            self.make_clickthrough_method2,
            self.make_clickthrough_method3
        ]
        
        for i, method in enumerate(methods, 1):
            if method():
                print(f"\nMethod {i} applied. Testing in 3 seconds...")
                time.sleep(3)
                
                # Test with automated click
                self.test_click()
                
                print("Check if click went through...")
                time.sleep(2)
        
        print("\nKeeping window open for manual testing...")
        
        # Keep window alive
        while True:
            event = self.display.next_event()
            if event.type == X.Expose:
                self.draw_content()
                
    def test_click(self):
        """Test clicking through the window"""
        import pyautogui
        
        # Click in the middle of our window
        click_x = self.x + self.width // 2
        click_y = self.y + self.height // 2
        
        print(f"  Clicking at ({click_x}, {click_y})...")
        pyautogui.click(click_x, click_y)

if __name__ == "__main__":
    try:
        window = X11ClickThroughWindow()
        window.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()