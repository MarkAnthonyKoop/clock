#!/usr/bin/env python3
"""
Clock v5: Font-Based Numbers at Hand Tips
Small windows with actual font-rendered numbers at the end of each hand
Much cleaner than pixel art numbers!
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import cairo
import math
from datetime import datetime

from Xlib import X, display

class PixelSquare:
    def __init__(self, display_obj, x, y, color=None):
        self.display = display_obj
        self.screen = display_obj.screen()
        self.x = x
        self.y = y
        
        self.window = self.screen.root.create_window(
            x, y, 4, 4, 0,
            self.screen.root_depth,
            X.InputOutput,
            X.CopyFromParent,
            background_pixel=color if color else self.screen.white_pixel,
            override_redirect=1
        )
        
        try:
            state_atom = self.display.intern_atom('_NET_WM_STATE')
            above_atom = self.display.intern_atom('_NET_WM_STATE_ABOVE')
            from Xlib import Xatom
            self.window.change_property(state_atom, Xatom.ATOM, 32, [above_atom])
        except:
            pass
        
        self.window.map()
        self.visible = True
    
    def move_to(self, new_x, new_y):
        self.x = new_x
        self.y = new_y
        self.window.configure(x=new_x, y=new_y)
        self.display.sync()
    
    def hide(self):
        if self.visible:
            self.window.unmap()
            self.visible = False
    
    def show(self):
        if not self.visible:
            self.window.map()
            self.visible = True

class NumberWindow(Gtk.Window):
    """Small window displaying a font-rendered number"""
    
    def __init__(self, text="12", color=(1, 1, 1)):
        super().__init__()
        self.text = text
        self.color = color
        
        # Window setup
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_size_request(24, 16)  # Small window
        
        # Make transparent
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        
        # Drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)
        
    def on_draw(self, widget, cr):
        # Transparent background
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        
        # Draw text
        cr.set_source_rgba(*self.color, 1)
        cr.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(12)
        
        text_extents = cr.text_extents(self.text)
        x = (24 - text_extents.width) / 2
        y = (16 + text_extents.height) / 2
        
        cr.move_to(x, y)
        cr.show_text(self.text)
        
        return True
    
    def update_text(self, new_text):
        self.text = str(new_text)
        self.queue_draw()

class FontNumberClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        screen_width = self.screen.width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"Creating FONT NUMBER clock at ({self.center_x}, {self.center_y})")
        
        # Create hand squares
        self.hour_squares = [PixelSquare(self.display, 0, 0, 0x44FF44) for _ in range(12)]  # Green
        self.minute_squares = [PixelSquare(self.display, 0, 0, 0x4444FF) for _ in range(16)]  # Blue
        self.second_squares = [PixelSquare(self.display, 0, 0, 0xFF4444) for _ in range(20)]  # Red
        
        # Hide hands initially
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.hide()
        
        # Create number windows
        self.hour_number = NumberWindow("12", (0.3, 1.0, 0.3))  # Green text
        self.minute_number = NumberWindow("00", (0.3, 0.3, 1.0))  # Blue text  
        self.second_number = NumberWindow("00", (1.0, 0.3, 0.3))  # Red text
        
        # Show number windows
        self.hour_number.show_all()
        self.minute_number.show_all()
        self.second_number.show_all()
        
        print("🔤 Created FONT NUMBER clock:")
        print("  🟢 Hour hand: Green with font-rendered hour number")
        print("  🔵 Minute hand: Blue with font-rendered minute number")
        print("  🔴 Second hand: Red with font-rendered second number")
        print("  📝 Clean font rendering at hand tips!")
        
        # Start updating
        GLib.timeout_add(1000, self.update_time)
        self.update_time()
        
    def position_hand_squares(self, squares, angle, length):
        """Position squares along straight line"""
        for i, square in enumerate(squares):
            distance = (i + 1) * (length / len(squares))
            x = int(self.center_x + distance * math.sin(angle))
            y = int(self.center_y - distance * math.cos(angle))
            square.move_to(x - 2, y - 2)
            square.show()
    
    def update_time(self):
        now = datetime.now()
        
        # Calculate angles
        hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
        minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
        second_angle = now.second * math.pi / 30
        
        # Position hands
        self.position_hand_squares(self.hour_squares, hour_angle, 50)
        self.position_hand_squares(self.minute_squares, minute_angle, 70)
        self.position_hand_squares(self.second_squares, second_angle, 90)
        
        # Calculate tip positions for number windows
        hour_tip_x = int(self.center_x + 60 * math.sin(hour_angle))
        hour_tip_y = int(self.center_y - 60 * math.cos(hour_angle))
        
        minute_tip_x = int(self.center_x + 80 * math.sin(minute_angle))
        minute_tip_y = int(self.center_y - 80 * math.cos(minute_angle))
        
        second_tip_x = int(self.center_x + 100 * math.sin(second_angle))
        second_tip_y = int(self.center_y - 100 * math.cos(second_angle))
        
        # Position and update number windows
        hour_display = now.hour if now.hour <= 12 else now.hour - 12
        if hour_display == 0: hour_display = 12
        
        self.hour_number.move(hour_tip_x - 12, hour_tip_y - 20)
        self.hour_number.update_text(str(hour_display))
        
        self.minute_number.move(minute_tip_x - 12, minute_tip_y - 20)
        self.minute_number.update_text(f"{now.minute:02d}")
        
        self.second_number.move(second_tip_x - 12, second_tip_y - 20)
        self.second_number.update_text(f"{now.second:02d}")
        
        return True  # Continue timeout

def main():
    print("\n🔤 FONT NUMBER PIXEL CLOCK!")
    print("Clean font-rendered numbers at hand tips")
    print("Press Ctrl+C to exit")
    
    clock = FontNumberClock()
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\n🔤 Cleaning up font number clock...")
        Gtk.main_quit()

if __name__ == "__main__":
    main()