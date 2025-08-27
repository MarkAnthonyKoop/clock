#!/usr/bin/env python3
"""
Clock v8: Rainbow Weather Clock - Full Spectrum Mapping
- Temperature: Deep purples/blues (cold) → aquamarine/teal (mild) → yellow/orange/red (hot)
- Wind: Calm greens → energetic yellows → violent reds/magentas
- Rain: Clear whites/silvers → deep blues → storm purples
- 2x bigger size for better visibility
- Rich rainbow gradients within weather-appropriate spectral ranges
"""

from Xlib import X, display
import math
import time
import threading
from datetime import datetime
import random

class PixelSquare:
    def __init__(self, display_obj, x, y, color=None):
        self.display = display_obj
        self.screen = display_obj.screen()
        self.x = x
        self.y = y
        
        # 2x bigger squares for better visibility
        self.window = self.screen.root.create_window(
            x, y, 6, 6, 0,  # 6x6 instead of 4x4
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
        self.window.change_attributes(background_pixel=new_color)
        self.window.clear_area(0, 0, 6, 6)  # Clear 6x6 area
        self.display.sync()
    
    def hide(self):
        if self.visible:
            self.window.unmap()
            self.visible = False
    
    def show(self):
        if not self.visible:
            self.window.map()
            self.visible = True

class RainbowWeatherClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        screen_width = self.screen.width_in_pixels
        # 2x bigger positioning
        self.center_x = screen_width - 250  # More space needed
        self.center_y = 200
        
        print(f"🌈 Creating RAINBOW WEATHER clock at ({self.center_x}, {self.center_y})")
        print("📏 2x bigger size with 6x6 pixel squares")
        
        # More squares for 2x size and smoother gradients
        self.hour_squares = [PixelSquare(self.display, 0, 0) for _ in range(24)]    # Rain 
        self.minute_squares = [PixelSquare(self.display, 0, 0) for _ in range(30)] # Temperature
        self.second_squares = [PixelSquare(self.display, 0, 0) for _ in range(36)] # Wind
        
        # Bigger center squares
        self.center_squares = []
        for dx in range(-9, 12, 6):  # Bigger spacing
            for dy in range(-9, 12, 6):
                square = PixelSquare(self.display, self.center_x + dx, self.center_y + dy)
                self.center_squares.append(square)
        
        # Hide hands initially
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.hide()
        
        # Weather data with broader ranges for better rainbow mapping
        self.weather_data = {
            'temp_range': (65, 105),  # Austin summer range
            'wind_range': (0, 35),    # Calm to very windy
            'rain_range': (0, 100),   # 0-100% probability
            'hourly_temps': [],
            'hourly_winds': [],
            'hourly_rain': []
        }
        
        self.running = True
        self.generate_rainbow_weather()
        
    def generate_rainbow_weather(self):
        """Generate weather with full range for rainbow mapping"""
        print("🌈 Generating full-spectrum Austin weather...")
        
        min_temp, max_temp = self.weather_data['temp_range']
        min_wind, max_wind = self.weather_data['wind_range']
        
        # Generate 24-hour data using full ranges
        for i in range(24):
            # Temperature: Use full range for better rainbow effect
            temp = random.randint(min_temp, max_temp)
            self.weather_data['hourly_temps'].append(temp)
            
            # Wind: Realistic patterns but use full range
            if 10 <= i <= 18:  # Daytime - can be windier
                wind = random.randint(5, max_wind)
            else:  # Night - calmer but can still vary
                wind = random.randint(0, 20)
            self.weather_data['hourly_winds'].append(wind)
            
            # Rain: Full probability range
            if 13 <= i <= 17:  # Afternoon storms
                rain = random.randint(30, 100)
            else:
                rain = random.randint(0, 50)
            self.weather_data['hourly_rain'].append(rain)
        
        print(f"  🌡️ Temp range: {min(self.weather_data['hourly_temps'])}°F - {max(self.weather_data['hourly_temps'])}°F")
        print(f"  💨 Wind range: {min(self.weather_data['hourly_winds'])} - {max(self.weather_data['hourly_winds'])} mph")
        print(f"  🌧️ Rain range: {min(self.weather_data['hourly_rain'])} - {max(self.weather_data['hourly_rain'])}%")
        
    def temp_to_rainbow_color(self, temp_f):
        """Map temperature to rainbow spectrum: Purple(cold) → Blue → Teal → Yellow → Orange → Red(hot)"""
        min_temp, max_temp = self.weather_data['temp_range']
        
        # Normalize temperature to 0-1 range
        normalized = max(0, min(1, (temp_f - min_temp) / (max_temp - min_temp)))
        
        # Map to temperature-appropriate rainbow spectrum
        if normalized < 0.15:      # Very cold: Deep purples/violets
            hue = 280 + normalized * 80  # 280-292° (deep purple to violet)
            sat = 0.9 + normalized * 0.1
            val = 0.6 + normalized * 0.3
            
        elif normalized < 0.3:     # Cold: Blues
            progress = (normalized - 0.15) / 0.15
            hue = 240 + progress * 20    # 240-260° (blue to blue-purple)
            sat = 0.8 + progress * 0.2
            val = 0.7 + progress * 0.2
            
        elif normalized < 0.5:     # Cool: Blue-greens, teals, aquamarine
            progress = (normalized - 0.3) / 0.2
            hue = 200 - progress * 20    # 200-180° (cyan to teal)
            sat = 0.7 + progress * 0.2
            val = 0.8 + progress * 0.1
            
        elif normalized < 0.7:     # Mild: Greens to yellows
            progress = (normalized - 0.5) / 0.2
            hue = 120 - progress * 60    # 120-60° (green to yellow)
            sat = 0.6 + progress * 0.3
            val = 0.9
            
        elif normalized < 0.85:    # Warm: Yellows to oranges
            progress = (normalized - 0.7) / 0.15
            hue = 50 - progress * 20     # 50-30° (yellow to orange)
            sat = 0.9
            val = 0.95
            
        else:                      # Hot: Orange to red
            progress = (normalized - 0.85) / 0.15
            hue = 25 - progress * 25     # 25-0° (orange to red)
            sat = 0.95 + progress * 0.05
            val = 0.9 + progress * 0.1
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def wind_to_rainbow_color(self, wind_mph):
        """Map wind to rainbow: Calm greens → energetic yellows → violent magentas/reds"""
        min_wind, max_wind = self.weather_data['wind_range']
        normalized = max(0, min(1, wind_mph / max_wind))
        
        if normalized < 0.2:       # Calm: Soft greens
            hue = 120 + normalized * 40   # 120-128° (green)
            sat = 0.4 + normalized * 0.3
            val = 0.7 + normalized * 0.2
            
        elif normalized < 0.4:     # Light breeze: Green to yellow-green
            progress = (normalized - 0.2) / 0.2
            hue = 100 - progress * 20     # 100-80° (yellow-green)
            sat = 0.6 + progress * 0.2
            val = 0.8 + progress * 0.1
            
        elif normalized < 0.6:     # Moderate: Yellows
            progress = (normalized - 0.4) / 0.2
            hue = 60 - progress * 10      # 60-50° (yellow)
            sat = 0.8 + progress * 0.1
            val = 0.9 + progress * 0.05
            
        elif normalized < 0.8:     # Strong: Orange to red
            progress = (normalized - 0.6) / 0.2
            hue = 40 - progress * 30      # 40-10° (orange to red)
            sat = 0.9 + progress * 0.1
            val = 0.9
            
        else:                      # Violent: Red to magenta
            progress = (normalized - 0.8) / 0.2
            hue = 350 + progress * 30     # 350-380°→20° (red to magenta)
            sat = 1.0
            val = 0.85 + progress * 0.15
        
        return self.hsv_to_rgb(hue % 360, sat, val)
    
    def rain_to_rainbow_color(self, rain_percent):
        """Map rain to rainbow: Clear silvers → light blues → deep blues → storm purples"""
        normalized = rain_percent / 100.0
        
        if normalized < 0.1:       # No rain: Bright white/silver
            hue = 0
            sat = 0.1
            val = 0.95
            
        elif normalized < 0.3:     # Light chance: Light grays to pale blues
            progress = (normalized - 0.1) / 0.2
            hue = 220
            sat = 0.2 + progress * 0.3
            val = 0.9 - progress * 0.2
            
        elif normalized < 0.6:     # Moderate: Blues
            progress = (normalized - 0.3) / 0.3
            hue = 220 + progress * 20     # 220-240° (light to deeper blue)
            sat = 0.5 + progress * 0.3
            val = 0.7 + progress * 0.1
            
        elif normalized < 0.8:     # High chance: Deep blues
            progress = (normalized - 0.6) / 0.2
            hue = 230 - progress * 10     # 230-220° (blue variations)
            sat = 0.8 + progress * 0.1
            val = 0.6 + progress * 0.2
            
        else:                      # Storm: Blue to purple
            progress = (normalized - 0.8) / 0.2
            hue = 250 + progress * 30     # 250-280° (blue to purple)
            sat = 0.9 + progress * 0.1
            val = 0.5 + progress * 0.3
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB with full precision"""
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
    
    def enhanced_curve_positions(self, angle, length, num_squares, curve_intensity):
        """2x bigger curves"""
        positions = []
        
        for i in range(num_squares):
            t = (i + 1) / num_squares
            distance = t * length
            
            # Enhanced curve with 2x scale
            curve_offset = curve_intensity * length * 0.6 * math.sin(math.pi * t)
            
            # Base position (2x scale)
            base_x = distance * math.sin(angle)
            base_y = -distance * math.cos(angle)
            
            # Apply curve
            perp_x = -math.cos(angle)
            perp_y = -math.sin(angle)
            
            x = int(self.center_x + base_x + curve_offset * perp_x)
            y = int(self.center_y + base_y + curve_offset * perp_y)
            
            positions.append((x - 3, y - 3))  # Center 6x6 squares
        
        return positions
    
    def position_rainbow_weather_hand(self, squares, angle, length, weather_func, wind_curve=False):
        """Position squares with rainbow weather colors"""
        if wind_curve:
            # Use current wind for curve
            current_wind = self.weather_data['hourly_winds'][0] if self.weather_data['hourly_winds'] else 10
            curve_factor = current_wind / 35.0
            positions = self.enhanced_curve_positions(angle, length, len(squares), curve_factor)
        else:
            # Straight line (2x bigger)
            positions = []
            for i in range(len(squares)):
                progress = (i + 1) / len(squares)
                distance = progress * length
                x = int(self.center_x + distance * math.sin(angle))
                y = int(self.center_y - distance * math.cos(angle))
                positions.append((x - 3, y - 3))
        
        for i, square in enumerate(squares):
            progress = i / len(squares)
            color = weather_func(i, progress)
            
            x, y = positions[i]
            square.move_to(x, y)
            square.change_color(color)
            square.show()
    
    def get_temp_rainbow(self, square_index, progress):
        """Temperature rainbow gradient"""
        hour_index = int(progress * 23)
        temp = self.weather_data['hourly_temps'][hour_index]
        return self.temp_to_rainbow_color(temp)
    
    def get_wind_rainbow(self, square_index, progress):
        """Wind rainbow gradient"""
        hour_index = int(progress * 23)
        wind = self.weather_data['hourly_winds'][hour_index]
        return self.wind_to_rainbow_color(wind)
    
    def get_rain_rainbow(self, square_index, progress):
        """Rain rainbow gradient"""
        hour_index = int(progress * 23)
        rain = self.weather_data['hourly_rain'][hour_index]
        return self.rain_to_rainbow_color(rain)
    
    def pulse_rainbow_center(self, second):
        """Rainbow center pulse"""
        for i, square in enumerate(self.center_squares):
            # Cycle through rainbow over time
            hue = (second * 10 + i * 45) % 360
            pulse = 0.7 + 0.3 * math.sin(second * 0.4 + i * 0.6)
            color = self.hsv_to_rgb(hue, 0.8, pulse)
            square.change_color(color)
    
    def update_clock(self):
        while self.running:
            now = datetime.now()
            
            # Calculate angles
            hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
            minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
            second_angle = now.second * math.pi / 30
            
            # Rainbow weather hands (2x bigger lengths)
            self.position_rainbow_weather_hand(
                self.hour_squares, hour_angle, 100,  # 2x length
                self.get_rain_rainbow, wind_curve=False
            )
            
            self.position_rainbow_weather_hand(
                self.minute_squares, minute_angle, 130,  # 2x length
                self.get_temp_rainbow, wind_curve=False
            )
            
            self.position_rainbow_weather_hand(
                self.second_squares, second_angle, 160,  # 2x length
                self.get_wind_rainbow, wind_curve=True
            )
            
            # Rainbow center pulse
            self.pulse_rainbow_center(now.second)
            
            time.sleep(1)
    
    def run(self):
        print("\n🌈 RAINBOW WEATHER CLOCK RUNNING!")
        print("✨ Full spectrum mapping with weather-appropriate ranges")
        print("📏 2x bigger size for mesmerizing detail")
        print("🎨 Temperature: Purple(cold) → Blue → Teal → Yellow → Red(hot)")
        print("💨 Wind: Green(calm) → Yellow → Orange → Red → Magenta(violent)")  
        print("🌧️ Rain: Silver(clear) → Blue → Deep Blue → Purple(storms)")
        print("Press Ctrl+C to exit")
        
        update_thread = threading.Thread(target=self.update_clock, daemon=True)
        update_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🌈 Rainbow cleanup...")
            self.running = False
            
            all_squares = (self.hour_squares + self.minute_squares + 
                          self.second_squares + self.center_squares)
            for square in all_squares:
                square.hide()
            
            self.display.close()

if __name__ == "__main__":
    clock = RainbowWeatherClock()
    clock.run()