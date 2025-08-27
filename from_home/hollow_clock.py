#!/usr/bin/env python3
"""
Hollow clock with separate transparent windows for each component
Using the <50% opacity trick for click-through
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import time
from datetime import datetime

class HollowClockPart(Gtk.Window):
    """Base class for clock parts with <50% opacity for click-through"""
    
    def __init__(self, width, height, x, y):
        super().__init__()
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_size_request(width, height)
        self.move(x, y)
        
        # Make window transparent
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        
        # Drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)
        
        # Set opacity to 49% for click-through
        self.set_opacity(0.49)
        
    def on_draw(self, widget, cr):
        # Override in subclasses
        pass

class ClockRim(HollowClockPart):
    """Just the outer rim/circle of the clock - hollow center"""
    
    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        cx, cy = width / 2, height / 2
        radius = min(width, height) / 2 - 5
        
        # Draw only the rim (hollow center)
        cr.set_source_rgba(1, 1, 1, 1)  # White, full alpha (but window is 49%)
        cr.set_line_width(3)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.stroke()
        
        # Draw hour marks
        for i in range(12):
            angle = i * math.pi / 6
            x1 = cx + (radius - 10) * math.sin(angle)
            y1 = cy - (radius - 10) * math.cos(angle)
            x2 = cx + radius * math.sin(angle)
            y2 = cy - radius * math.cos(angle)
            
            cr.set_line_width(2 if i % 3 == 0 else 1)
            cr.move_to(x1, y1)
            cr.line_to(x2, y2)
            cr.stroke()
        
        return True

class ClockHand(HollowClockPart):
    """Individual clock hand as separate window"""
    
    def __init__(self, width, height, x, y, length, thickness, color, hand_type):
        super().__init__(width, height, x, y)
        self.length = length
        self.thickness = thickness
        self.color = color
        self.hand_type = hand_type  # 'hour', 'minute', or 'second'
        self.angle = 0
        
    def update_angle(self):
        now = datetime.now()
        
        if self.hand_type == 'hour':
            self.angle = (now.hour % 12 + now.minute / 60) * math.pi / 6
        elif self.hand_type == 'minute':
            self.angle = (now.minute + now.second / 60) * math.pi / 30
        elif self.hand_type == 'second':
            self.angle = now.second * math.pi / 30
            
        self.queue_draw()
        
    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        cx, cy = width / 2, height / 2
        
        # Draw hand
        cr.save()
        cr.translate(cx, cy)
        cr.rotate(self.angle)
        
        cr.set_source_rgba(*self.color, 1)  # Full alpha (window is 49%)
        cr.set_line_width(self.thickness)
        cr.move_to(0, 0)
        cr.line_to(0, -self.length)
        cr.stroke()
        
        # Draw a small circle at center
        cr.arc(0, 0, self.thickness, 0, 2 * math.pi)
        cr.fill()
        
        cr.restore()
        return True

class HollowClock:
    """Manager for all clock components"""
    
    def __init__(self):
        # Screen dimensions
        screen = Gdk.Screen.get_default()
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Clock position and size
        self.clock_size = 200
        self.clock_x = self.screen_width - self.clock_size - 50
        self.clock_y = 50
        
        # Create clock components as separate windows
        self.rim = ClockRim(self.clock_size, self.clock_size, self.clock_x, self.clock_y)
        
        # Create hands (each in its own window)
        self.hour_hand = ClockHand(
            self.clock_size, self.clock_size, 
            self.clock_x, self.clock_y,
            50, 4, (0.8, 0.8, 0.8), 'hour'
        )
        
        self.minute_hand = ClockHand(
            self.clock_size, self.clock_size,
            self.clock_x, self.clock_y,
            70, 3, (0.9, 0.9, 0.9), 'minute'
        )
        
        self.second_hand = ClockHand(
            self.clock_size, self.clock_size,
            self.clock_x, self.clock_y,
            80, 1, (1, 0.3, 0.3), 'second'
        )
        
        # Show all windows
        self.rim.show_all()
        self.hour_hand.show_all()
        self.minute_hand.show_all()
        self.second_hand.show_all()
        
        # Update hands every second
        GLib.timeout_add_seconds(1, self.update_time)
        self.update_time()
        
    def update_time(self):
        self.hour_hand.update_angle()
        self.minute_hand.update_angle()
        self.second_hand.update_angle()
        return True  # Continue timeout
        
    def quit(self):
        Gtk.main_quit()

def main():
    print("Starting hollow clock with <50% opacity for click-through...")
    print("Each component is a separate window at 49% opacity")
    print("Theory: Areas with <50% opacity should be click-through")
    
    clock = HollowClock()
    
    # Connect destroy signal
    clock.rim.connect("destroy", lambda w: clock.quit())
    
    # Test click-through after 3 seconds
    def test_click():
        import pyautogui
        pyautogui.FAILSAFE = False
        
        screen_width, screen_height = pyautogui.size()
        test_x = screen_width - 150
        test_y = 150
        
        print(f"\nTesting click at ({test_x}, {test_y})...")
        pyautogui.moveTo(test_x, test_y, duration=0.5)
        pyautogui.click()
        print("If nothing happened, click-through might be working!")
        
        return False  # Don't repeat
    
    GLib.timeout_add_seconds(3, test_click)
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()