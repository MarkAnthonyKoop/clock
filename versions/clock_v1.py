#!/usr/bin/env python3
"""
Clock hands made of tiny 4x4 pixel squares
Each square is its own window - no bounding rectangles!
Diagonal hands work perfectly, could even do curves or dashes
"""

from Xlib import X, display
import math
import time
import threading
from datetime import datetime

class PixelSquare:
    """A single 4x4 pixel window"""
    
    def __init__(self, display_obj, x, y, color=None):
        self.display = display_obj
        self.screen = display_obj.screen()
        self.x = x
        self.y = y
        
        # Create tiny 4x4 window
        self.window = self.screen.root.create_window(
            x, y, 4, 4, 0,
            self.screen.root_depth,
            X.InputOutput,
            X.CopyFromParent,
            background_pixel=self.screen.white_pixel if not color else color,
            override_redirect=1
        )
        
        # Set always on top
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
        """Move square to new position"""
        self.x = new_x
        self.y = new_y
        self.window.configure(x=new_x, y=new_y)
        self.display.sync()
    
    def hide(self):
        """Hide the square"""
        if self.visible:
            self.window.unmap()
            self.visible = False
    
    def show(self):
        """Show the square"""
        if not self.visible:
            self.window.map()
            self.visible = True

class PixelHandClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        # Clock center position
        screen_width = self.screen.width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"Creating pixel square clock at ({self.center_x}, {self.center_y})")
        
        # Create squares for each hand
        # Hour hand: ~15 squares (60 pixels / 4 = 15)
        self.hour_squares = []
        for i in range(15):
            square = PixelSquare(self.display, 0, 0, self.screen.white_pixel)
            square.hide()  # Start hidden
            self.hour_squares.append(square)
        
        # Minute hand: ~20 squares (80 pixels / 4 = 20) 
        self.minute_squares = []
        for i in range(20):
            # Different color for minute hand
            color = 0xCCCCCC  # Light gray
            square = PixelSquare(self.display, 0, 0, color)
            square.hide()
            self.minute_squares.append(square)
        
        # Optional: Center dot made of squares
        self.center_squares = []
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                square = PixelSquare(self.display, 
                                   self.center_x + dx, 
                                   self.center_y + dy, 
                                   0xFF0000)  # Red center
                self.center_squares.append(square)
        
        self.running = True
        print("Created pixel squares:")
        print(f"  Hour hand: {len(self.hour_squares)} × 4x4 squares") 
        print(f"  Minute hand: {len(self.minute_squares)} × 4x4 squares")
        print(f"  Center: {len(self.center_squares)} × 4x4 squares")
        print("Total blocking area: ~600 pixels out of millions!")
        
    def position_hand_squares(self, squares, angle, length):
        """Position squares along a line from center at given angle"""
        squares_to_use = min(len(squares), length // 4)
        
        # Show squares we need, hide others
        for i, square in enumerate(squares):
            if i < squares_to_use:
                # Calculate position for this square
                distance = (i + 1) * 4  # Each square is 4 pixels apart
                x = int(self.center_x + distance * math.sin(angle))
                y = int(self.center_y - distance * math.cos(angle))
                
                square.move_to(x - 2, y - 2)  # Center the 4x4 square
                square.show()
            else:
                square.hide()
    
    def update_clock(self):
        """Update hand positions"""
        while self.running:
            now = datetime.now()
            
            # Calculate angles
            hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
            minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
            
            # Position squares
            self.position_hand_squares(self.hour_squares, hour_angle, 60)   # 60 pixel hour hand
            self.position_hand_squares(self.minute_squares, minute_angle, 80)  # 80 pixel minute hand
            
            time.sleep(1)
    
    def run(self):
        print("\nPixel Square Clock Running!")
        print("Each hand is made of individual 4x4 pixel windows")
        print("No bounding rectangles - diagonal hands work perfectly!")
        print("Press Ctrl+C to exit")
        
        # Start update thread  
        update_thread = threading.Thread(target=self.update_clock, daemon=True)
        update_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nCleaning up...")
            self.running = False
            
            # Hide all squares
            for square in self.hour_squares + self.minute_squares + self.center_squares:
                square.hide()
            
            self.display.close()

if __name__ == "__main__":
    clock = PixelHandClock()
    clock.run()