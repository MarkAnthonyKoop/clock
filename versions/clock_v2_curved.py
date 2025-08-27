#!/usr/bin/env python3
"""
Clock v2: Curved Hands with Second Hand
Beautiful curved clock hands that arc gracefully
"""

from Xlib import X, display
import math
import time
import threading
from datetime import datetime

class PixelSquare:
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
            background_pixel=color if color else self.screen.white_pixel,
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

class CurvedPixelClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        # Clock center
        screen_width = self.screen.width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"Creating curved pixel clock at ({self.center_x}, {self.center_y})")
        
        # Color palette
        self.hour_color = 0xFFFFFF    # White
        self.minute_color = 0xCCCCCC  # Light gray  
        self.second_color = 0xFF4444  # Red
        self.center_color = 0x4444FF  # Blue
        
        # Create squares for hands
        self.hour_squares = [PixelSquare(self.display, 0, 0, self.hour_color) for _ in range(18)]
        self.minute_squares = [PixelSquare(self.display, 0, 0, self.minute_color) for _ in range(25)]
        self.second_squares = [PixelSquare(self.display, 0, 0, self.second_color) for _ in range(30)]
        
        # Center squares
        self.center_squares = []
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                square = PixelSquare(self.display, 
                                   self.center_x + dx, self.center_y + dy, 
                                   self.center_color)
                self.center_squares.append(square)
        
        # Hide all initially
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.hide()
        
        self.running = True
        print("✨ Created CURVED pixel clock:")
        print(f"  🕐 Hour hand: {len(self.hour_squares)} curved squares")
        print(f"  🕑 Minute hand: {len(self.minute_squares)} curved squares") 
        print(f"  🕒 Second hand: {len(self.second_squares)} curved squares")
        print("  🎨 Hands have beautiful curves!")
        
    def curved_hand_positions(self, angle, length, num_squares, curve_factor=0.3):
        """Generate positions for a curved hand"""
        positions = []
        
        for i in range(num_squares):
            # Progress along hand (0 to 1)
            t = (i + 1) / num_squares
            distance = t * length
            
            # Add curve - perpendicular offset that peaks at middle
            curve_offset = curve_factor * length * math.sin(math.pi * t)
            
            # Base position along straight line
            base_x = distance * math.sin(angle)
            base_y = -distance * math.cos(angle)
            
            # Perpendicular direction for curve (rotate 90 degrees)
            perp_x = -math.cos(angle)
            perp_y = -math.sin(angle)
            
            # Final curved position
            x = int(self.center_x + base_x + curve_offset * perp_x)
            y = int(self.center_y + base_y + curve_offset * perp_y)
            
            positions.append((x - 2, y - 2))  # Center 4x4 square
            
        return positions
    
    def position_curved_hand(self, squares, angle, length, curve_factor=0.3):
        """Position squares along a curved path"""
        positions = self.curved_hand_positions(angle, length, len(squares), curve_factor)
        
        for i, square in enumerate(squares):
            if i < len(positions):
                x, y = positions[i]
                square.move_to(x, y)
                square.show()
            else:
                square.hide()
    
    def update_clock(self):
        while self.running:
            now = datetime.now()
            
            # Calculate angles
            hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
            minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
            second_angle = now.second * math.pi / 30
            
            # Position curved hands with different curve factors
            self.position_curved_hand(self.hour_squares, hour_angle, 65, curve_factor=0.4)   # Most curved
            self.position_curved_hand(self.minute_squares, minute_angle, 85, curve_factor=0.3) # Medium curve
            self.position_curved_hand(self.second_squares, second_angle, 95, curve_factor=0.2) # Slight curve
            
            time.sleep(1)
    
    def run(self):
        print("\n🎨 CURVED PIXEL CLOCK RUNNING!")
        print("Beautiful graceful curves instead of straight lines")
        print("Each hand arcs elegantly from center")
        print("Press Ctrl+C to exit")
        
        update_thread = threading.Thread(target=self.update_clock, daemon=True)
        update_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n✨ Cleaning up curved beauty...")
            self.running = False
            
            for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
                for square in squares:
                    square.hide()
            
            self.display.close()

if __name__ == "__main__":
    clock = CurvedPixelClock()
    clock.run()