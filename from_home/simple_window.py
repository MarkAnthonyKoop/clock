#!/usr/bin/env python3
"""
Simple transparent window for testing click-through
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import time

class ClickThroughWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClickThrough Test")
        
        # Window size and position (top-right like clock)
        width = 200
        height = 200
        screen_width = self.root.winfo_screenwidth()
        x_pos = screen_width - width - 50
        y_pos = 50
        
        self.root.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        # Make window transparent
        self.root.attributes('-alpha', 0.7)
        
        # Try to make it stay on top
        self.root.attributes('-topmost', True)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Add a colored frame so we can see it
        self.frame = tk.Frame(self.root, bg='red', width=width, height=height)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Add text label
        self.label = tk.Label(self.frame, text="Click Through\nTest Window", 
                             bg='red', fg='white', font=('Arial', 16))
        self.label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Store window ID after it's mapped
        self.root.after(100, self.get_window_id)
        
    def get_window_id(self):
        """Get the X11 window ID"""
        try:
            # Get window ID using xdotool
            result = subprocess.run(['xdotool', 'search', '--name', 'ClickThrough Test'],
                                  capture_output=True, text=True)
            if result.stdout.strip():
                self.window_id = int(result.stdout.strip().split()[0])
                print(f"Window ID: 0x{self.window_id:x}")
                self.make_clickthrough()
        except Exception as e:
            print(f"Could not get window ID: {e}")
            
    def make_clickthrough(self):
        """Apply click-through using X11 shape extension"""
        print("Attempting to make window click-through...")
        try:
            from Xlib import X, display
            from Xlib.ext import shape
            
            d = display.Display()
            window = d.create_resource_object('window', self.window_id)
            
            # Method 1: Remove input shape completely
            window.shape_mask(shape.SO.Set, shape.SK.Input, 0, 0, X.NONE)
            d.sync()
            
            print("Applied shape_mask to remove input")
            
        except Exception as e:
            print(f"Failed to apply click-through: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClickThroughWindow()
    app.run()