#!/usr/bin/env python3
"""
Clock v4: Time-Based Gradient Magic
Colors change throughout the day reflecting natural light cycles
Hands have gradients and rainbow effects that pulse with time
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
    
    def change_color(self, new_color):
        """Change the color of this square"""
        self.window.change_attributes(background_pixel=new_color)
        self.window.clear_area(0, 0, 4, 4)
        self.display.sync()
    
    def hide(self):
        if self.visible:
            self.window.unmap()
            self.visible = False
    
    def show(self):
        if not self.visible:
            self.window.map()
            self.visible = True

class GradientPixelClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        screen_width = self.screen.width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"Creating GRADIENT pixel clock at ({self.center_x}, {self.center_y})")
        
        # Create squares for hands
        self.hour_squares = [PixelSquare(self.display, 0, 0) for _ in range(15)]
        self.minute_squares = [PixelSquare(self.display, 0, 0) for _ in range(20)]
        self.second_squares = [PixelSquare(self.display, 0, 0) for _ in range(25)]
        
        # Center pulse
        self.center_squares = []
        for dx in range(-6, 8, 4):
            for dy in range(-6, 8, 4):
                if abs(dx) <= 2 or abs(dy) <= 2:  # Cross pattern
                    square = PixelSquare(self.display, self.center_x + dx, self.center_y + dy)
                    self.center_squares.append(square)
        
        # Hide all initially
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.hide()
        
        self.running = True
        print("🌈 Created GRADIENT pixel clock:")
        print("  🌅 Morning: Cool blues and purples")
        print("  ☀️  Noon: Bright yellows and oranges")
        print("  🌅 Evening: Warm reds and magentas")
        print("  🌙 Night: Deep purples and blues")
        print("  ⚡ Plus rainbow pulse effects!")
        
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color (returns hex color)"""
        h = h % 360
        c = v * s
        x = c * (1 - abs(((h / 60) % 2) - 1))
        m = v - c
        
        if 0 <= h < 60:
            r, g, b = c, x, 0
        elif 60 <= h < 120:
            r, g, b = x, c, 0
        elif 120 <= h < 180:
            r, g, b = 0, c, x
        elif 180 <= h < 240:
            r, g, b = 0, x, c
        elif 240 <= h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        
        return (r << 16) | (g << 8) | b
    
    def get_time_of_day_palette(self, hour, minute):
        """Get color palette based on time of day"""
        total_minutes = hour * 60 + minute
        
        # Define time periods
        if 5 * 60 <= total_minutes < 10 * 60:  # Dawn: 5-10 AM
            base_hue = 280  # Purple-blue
            warmth = 0.3
        elif 10 * 60 <= total_minutes < 16 * 60:  # Day: 10 AM - 4 PM  
            base_hue = 45   # Yellow-orange
            warmth = 0.8
        elif 16 * 60 <= total_minutes < 20 * 60:  # Sunset: 4-8 PM
            base_hue = 15   # Red-orange
            warmth = 0.9
        elif 20 * 60 <= total_minutes < 23 * 60:  # Evening: 8-11 PM
            base_hue = 300  # Magenta  
            warmth = 0.5
        else:  # Night: 11 PM - 5 AM
            base_hue = 240  # Blue
            warmth = 0.2
            
        return base_hue, warmth
    
    def position_gradient_hand(self, squares, angle, length, base_hue, warmth, second_offset=0):
        """Position squares with gradient colors"""
        for i, square in enumerate(squares):
            # Position
            distance = (i + 1) * (length / len(squares))
            x = int(self.center_x + distance * math.sin(angle))
            y = int(self.center_y - distance * math.cos(angle))
            
            # Gradient color based on position along hand + time effects
            progress = i / len(squares)  # 0 to 1 along hand
            
            # Add rainbow pulse based on seconds
            pulse = math.sin((second_offset + i) * 0.3) * 30
            hue = (base_hue + progress * 60 + pulse) % 360
            
            # Saturation and brightness vary along hand
            saturation = 0.7 + progress * 0.3  
            brightness = 0.6 + progress * 0.4 + math.sin(second_offset * 0.1) * 0.1
            
            color = self.hsv_to_rgb(hue, saturation, brightness)
            
            square.move_to(x - 2, y - 2)
            square.change_color(color)
            square.show()
    
    def pulse_center(self, second):
        """Pulse center squares with rainbow"""
        for i, square in enumerate(self.center_squares):
            hue = (second * 30 + i * 45) % 360  # Rotate rainbow
            pulse_intensity = 0.7 + 0.3 * math.sin(second * 0.5 + i)
            color = self.hsv_to_rgb(hue, 1.0, pulse_intensity)
            square.change_color(color)
    
    def update_clock(self):
        while self.running:
            now = datetime.now()
            
            # Get time-based palette
            base_hue, warmth = self.get_time_of_day_palette(now.hour, now.minute)
            
            # Calculate angles
            hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
            minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
            second_angle = now.second * math.pi / 30
            
            # Position hands with time-based gradients
            self.position_gradient_hand(self.hour_squares, hour_angle, 60, 
                                      base_hue, warmth, now.second)
            self.position_gradient_hand(self.minute_squares, minute_angle, 80, 
                                      (base_hue + 60) % 360, warmth, now.second * 2)
            self.position_gradient_hand(self.second_squares, second_angle, 100, 
                                      (base_hue + 120) % 360, warmth, now.second * 3)
            
            # Pulse center
            self.pulse_center(now.second)
            
            time.sleep(1)
    
    def run(self):
        print("\n🌈 GRADIENT PIXEL CLOCK RUNNING!")
        print("Colors change throughout the day:")
        now = datetime.now()
        hour = now.hour
        if 5 <= hour < 10:
            print("  🌅 Currently: DAWN colors (purple-blue)")
        elif 10 <= hour < 16:
            print("  ☀️  Currently: DAY colors (yellow-orange)")
        elif 16 <= hour < 20:
            print("  🌇 Currently: SUNSET colors (red-orange)")
        elif 20 <= hour < 23:
            print("  🌆 Currently: EVENING colors (magenta)")
        else:
            print("  🌙 Currently: NIGHT colors (deep blue)")
        
        print("Watch colors shift and pulse with time!")
        print("Press Ctrl+C to exit")
        
        update_thread = threading.Thread(target=self.update_clock, daemon=True)
        update_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🌈 Cleaning up gradient magic...")
            self.running = False
            
            all_squares = self.hour_squares + self.minute_squares + self.second_squares + self.center_squares
            for square in all_squares:
                square.hide()
            
            self.display.close()

if __name__ == "__main__":
    clock = GradientPixelClock()
    clock.run()