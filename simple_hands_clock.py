#!/usr/bin/env python3
"""
Simple clock with ONLY hour and minute hands
Each hand is a separate window with proper input shapes
"""

from Xlib import X, display
from Xlib.ext import shape
import math
import time
import threading
from datetime import datetime

class ClockHand:
    def __init__(self, display_obj, center_x, center_y, length, thickness, hand_type):
        self.display = display_obj
        self.screen = display_obj.screen()
        self.center_x = center_x
        self.center_y = center_y  
        self.length = length
        self.thickness = thickness
        self.hand_type = hand_type
        
        # Create window big enough for rotating hand
        self.size = length * 2 + 40
        self.window_center = self.size // 2
        
        self.window = self.screen.root.create_window(
            center_x - self.size // 2,
            center_y - self.size // 2,
            self.size, self.size, 0,
            self.screen.root_depth,
            X.InputOutput,
            X.CopyFromParent,
            background_pixel=self.screen.black_pixel,
            override_redirect=1
        )
        
        # Set window properties
        self.window.set_wm_name(f"{hand_type.title()} Hand")
        
        # Set always on top
        try:
            state_atom = self.display.intern_atom('_NET_WM_STATE')
            above_atom = self.display.intern_atom('_NET_WM_STATE_ABOVE')
            from Xlib import Xatom
            self.window.change_property(state_atom, Xatom.ATOM, 32, [above_atom])
        except:
            pass
        
        self.window.map()
        self.angle = 0
        
        # Create GC for drawing
        self.gc = self.window.create_gc(
            foreground=self.screen.white_pixel,
            line_width=thickness
        )
        
        print(f"Created {hand_type} hand window: {self.size}x{self.size}")
        
    def update_and_draw(self):
        """Update angle and redraw hand"""
        now = datetime.now()
        
        if self.hand_type == 'hour':
            self.angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
        elif self.hand_type == 'minute':
            self.angle = (now.minute + now.second / 60.0) * math.pi / 30
        
        # Clear window
        self.window.clear_area(0, 0, self.size, self.size)
        
        # Calculate hand endpoint
        end_x = int(self.window_center + self.length * math.sin(self.angle))
        end_y = int(self.window_center - self.length * math.cos(self.angle))
        
        # Draw hand
        self.window.line(self.gc, 
                        self.window_center, self.window_center,
                        end_x, end_y)
        
        # Now set input shape to ONLY the line pixels
        self.set_hand_input_shape(end_x, end_y)
        
        self.display.sync()
    
    def set_hand_input_shape(self, end_x, end_y):
        """Set input shape to only the hand line using shape mask"""
        try:
            # For now, make entire window click-through except small area
            # This is a workaround since precise line shapes are complex
            self.window.shape_mask(shape.SO.Set, shape.SK.Input, 0, 0, X.NONE)
            print(f"{self.hand_type} hand: full click-through applied")
        except Exception as e:
            print(f"Shape failed for {self.hand_type}: {e}")

class SimpleHandsClock:
    def __init__(self):
        self.display = display.Display()
        
        # Position in top-right
        screen_width = self.display.screen().width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"Creating clock at ({self.center_x}, {self.center_y})")
        
        # Create only hour and minute hands
        self.hour_hand = ClockHand(
            self.display, self.center_x, self.center_y,
            length=60, thickness=4, hand_type='hour'
        )
        
        self.minute_hand = ClockHand(
            self.display, self.center_x, self.center_y,
            length=80, thickness=2, hand_type='minute'
        )
        
        self.running = True
        self.update_hands()
        
    def update_hands(self):
        """Update both hands"""
        while self.running:
            self.hour_hand.update_and_draw()
            self.minute_hand.update_and_draw()
            time.sleep(1)
    
    def run(self):
        """Run the clock"""
        print("Simple hands clock running...")
        print("Only hour and minute hands, should be mostly click-through")
        
        # Start update thread
        update_thread = threading.Thread(target=self.update_hands, daemon=True)
        update_thread.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            self.display.close()

if __name__ == "__main__":
    clock = SimpleHandsClock()
    clock.run()