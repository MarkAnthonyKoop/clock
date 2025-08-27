#!/usr/bin/env python3
"""
Clock v3: Numbers at Hand Tips
Shows actual time digits at the end of each hand!
Hour hand shows hour (1-12), minute hand shows minutes (0-59), second hand shows seconds
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

class NumberPixelClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        screen_width = self.screen.width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"Creating NUMBER pixel clock at ({self.center_x}, {self.center_y})")
        
        # Colors
        self.hour_color = 0x44FF44     # Green
        self.minute_color = 0x4444FF   # Blue  
        self.second_color = 0xFF4444   # Red
        
        # Create squares for hands (fewer since we need room for numbers)
        self.hour_squares = [PixelSquare(self.display, 0, 0, self.hour_color) for _ in range(12)]
        self.minute_squares = [PixelSquare(self.display, 0, 0, self.minute_color) for _ in range(16)]
        self.second_squares = [PixelSquare(self.display, 0, 0, self.second_color) for _ in range(20)]
        
        # Squares for numbers at hand tips (lots needed for digits)
        self.hour_number_squares = [PixelSquare(self.display, 0, 0, self.hour_color) for _ in range(15)]
        self.minute_number_squares = [PixelSquare(self.display, 0, 0, self.minute_color) for _ in range(15)]  
        self.second_number_squares = [PixelSquare(self.display, 0, 0, self.second_color) for _ in range(15)]
        
        # Simple 3x5 bitmap fonts for digits
        self.digit_patterns = {
            0: [[1,1,1],[1,0,1],[1,0,1],[1,0,1],[1,1,1]],
            1: [[0,1,0],[1,1,0],[0,1,0],[0,1,0],[1,1,1]],
            2: [[1,1,1],[0,0,1],[1,1,1],[1,0,0],[1,1,1]],
            3: [[1,1,1],[0,0,1],[1,1,1],[0,0,1],[1,1,1]],
            4: [[1,0,1],[1,0,1],[1,1,1],[0,0,1],[0,0,1]],
            5: [[1,1,1],[1,0,0],[1,1,1],[0,0,1],[1,1,1]],
            6: [[1,1,1],[1,0,0],[1,1,1],[1,0,1],[1,1,1]],
            7: [[1,1,1],[0,0,1],[0,1,0],[1,0,0],[1,0,0]],
            8: [[1,1,1],[1,0,1],[1,1,1],[1,0,1],[1,1,1]],
            9: [[1,1,1],[1,0,1],[1,1,1],[0,0,1],[1,1,1]]
        }
        
        # Hide all initially
        for squares in [self.hour_squares, self.minute_squares, self.second_squares,
                       self.hour_number_squares, self.minute_number_squares, self.second_number_squares]:
            for square in squares:
                square.hide()
        
        self.running = True
        print("🔢 Created NUMBER pixel clock:")
        print("  🕐 Hour hand shows HOUR number at tip!")
        print("  🕑 Minute hand shows MINUTE number at tip!")
        print("  🕒 Second hand shows SECOND number at tip!")
        print("  📊 Real-time digital display at hand ends!")
        
    def position_hand_squares(self, squares, angle, length):
        """Position squares along straight line"""
        for i, square in enumerate(squares):
            if i < len(squares):
                distance = (i + 1) * (length / len(squares))
                x = int(self.center_x + distance * math.sin(angle))
                y = int(self.center_y - distance * math.cos(angle))
                square.move_to(x - 2, y - 2)
                square.show()
    
    def draw_number_at_position(self, number, base_x, base_y, squares):
        """Draw a number using squares at given position"""
        # Hide all squares first
        for square in squares:
            square.hide()
        
        # Convert number to string and draw each digit
        num_str = str(number).zfill(2) if number < 60 else str(number)
        
        square_idx = 0
        for digit_idx, digit_char in enumerate(num_str):
            if digit_char.isdigit():
                digit = int(digit_char)
                pattern = self.digit_patterns[digit]
                
                # Draw this digit
                for row in range(5):
                    for col in range(3):
                        if pattern[row][col] and square_idx < len(squares):
                            x = base_x + digit_idx * 16 + col * 4  # Digits spaced 16 pixels apart
                            y = base_y + row * 4
                            squares[square_idx].move_to(x, y)
                            squares[square_idx].show()
                            square_idx += 1
    
    def update_clock(self):
        while self.running:
            now = datetime.now()
            
            # Calculate angles
            hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
            minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
            second_angle = now.second * math.pi / 30
            
            # Position hands
            self.position_hand_squares(self.hour_squares, hour_angle, 50)
            self.position_hand_squares(self.minute_squares, minute_angle, 70)
            self.position_hand_squares(self.second_squares, second_angle, 90)
            
            # Calculate tip positions for numbers
            hour_tip_x = int(self.center_x + 60 * math.sin(hour_angle))
            hour_tip_y = int(self.center_y - 60 * math.cos(hour_angle))
            
            minute_tip_x = int(self.center_x + 80 * math.sin(minute_angle))  
            minute_tip_y = int(self.center_y - 80 * math.cos(minute_angle))
            
            second_tip_x = int(self.center_x + 100 * math.sin(second_angle))
            second_tip_y = int(self.center_y - 100 * math.cos(second_angle))
            
            # Draw numbers at hand tips!
            hour_display = now.hour if now.hour <= 12 else now.hour - 12
            if hour_display == 0: hour_display = 12
            
            self.draw_number_at_position(hour_display, hour_tip_x - 6, hour_tip_y - 10, self.hour_number_squares)
            self.draw_number_at_position(now.minute, minute_tip_x - 8, minute_tip_y - 10, self.minute_number_squares)  
            self.draw_number_at_position(now.second, second_tip_x - 8, second_tip_y - 10, self.second_number_squares)
            
            time.sleep(1)
    
    def run(self):
        print("\n🔢 NUMBER PIXEL CLOCK RUNNING!")
        print("Watch the numbers change at the tip of each hand!")
        print("Green=Hour, Blue=Minutes, Red=Seconds")
        print("Press Ctrl+C to exit")
        
        update_thread = threading.Thread(target=self.update_clock, daemon=True)
        update_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🔢 Cleaning up numbered clock...")
            self.running = False
            
            all_squares = (self.hour_squares + self.minute_squares + self.second_squares +
                          self.hour_number_squares + self.minute_number_squares + self.second_number_squares)
            for square in all_squares:
                square.hide()
            
            self.display.close()

if __name__ == "__main__":
    clock = NumberPixelClock()
    clock.run()