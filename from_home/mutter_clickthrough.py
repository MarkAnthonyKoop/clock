#!/usr/bin/env python3
"""
Click-through solution for Mutter/GNOME
Mutter doesn't respect input shapes properly, so we need a different approach
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo

class MutterClickThroughWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.set_title("Mutter ClickThrough Test")
        self.set_default_size(200, 200)
        self.set_decorated(False)  # Remove window decorations
        self.set_keep_above(True)  # Keep on top
        
        # Position window (top-right)
        screen = self.get_screen()
        monitor = screen.get_monitor_geometry(0)
        self.move(monitor.width - 250, 50)
        
        # Make window transparent
        self.set_app_paintable(True)
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        
        # Drawing area for custom rendering
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)
        
        # CRITICAL: Set input shape region to empty
        # This is the key to click-through on Mutter
        self.connect("realize", self.on_realize)
        
        self.show_all()
        
    def on_realize(self, widget):
        """Called when window is realized (mapped)"""
        window = self.get_window()
        if window:
            print(f"Window realized, applying click-through...")
            
            # Method 1: Set input shape to empty region
            # This should work even with Mutter
            empty_region = cairo.Region()  # Empty region = no input
            window.input_shape_combine_region(empty_region, 0, 0)
            
            print("Applied empty input region for click-through")
            
    def on_draw(self, widget, cr):
        """Draw the window content"""
        # Draw semi-transparent red background
        cr.set_source_rgba(1, 0, 0, 0.5)
        cr.paint()
        
        # Draw text
        cr.set_source_rgba(1, 1, 1, 1)
        cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(16)
        cr.move_to(30, 100)
        cr.show_text("Click Through Test")
        
        return True

def main():
    window = MutterClickThroughWindow()
    window.connect("destroy", Gtk.main_quit)
    
    print("Mutter-compatible click-through window created")
    print("The window should be visible but not capture clicks")
    
    # Test after 2 seconds
    def test_click():
        print("Testing click-through...")
        import pyautogui
        pyautogui.FAILSAFE = False  # Disable fail-safe for corner
        
        screen_width, screen_height = pyautogui.size()
        test_x = screen_width - 150
        test_y = 150
        
        pyautogui.moveTo(test_x, test_y, duration=0.5)
        pyautogui.click()
        print("Click test complete")
        
        return False  # Don't repeat
    
    GLib.timeout_add_seconds(2, test_click)
    
    Gtk.main()

if __name__ == "__main__":
    main()