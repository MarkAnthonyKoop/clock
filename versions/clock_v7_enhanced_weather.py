#!/usr/bin/env python3
"""
Clock v7: Enhanced Weather-Coded Clock
- More dramatic color gradients for better visibility
- Enhanced curve effects for wind visualization  
- Better weather data simulation
- More pronounced visual effects
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

class EnhancedWeatherClock:
    def __init__(self):
        self.display = display.Display()
        self.screen = self.display.screen()
        
        screen_width = self.screen.width_in_pixels
        self.center_x = screen_width - 150
        self.center_y = 150
        
        print(f"🌈 Creating ENHANCED WEATHER clock at ({self.center_x}, {self.center_y})")
        
        # More squares for better gradients
        self.hour_squares = [PixelSquare(self.display, 0, 0) for _ in range(18)]    # Rain probability  
        self.minute_squares = [PixelSquare(self.display, 0, 0) for _ in range(24)] # Temperature forecast
        self.second_squares = [PixelSquare(self.display, 0, 0) for _ in range(30)] # Wind forecast
        
        # Pulsing center showing current conditions
        self.center_squares = []
        for dx in range(-6, 8, 4):
            for dy in range(-6, 8, 4):
                square = PixelSquare(self.display, self.center_x + dx, self.center_y + dy)
                self.center_squares.append(square)
        
        # Hide hands initially
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.hide()
        
        # Enhanced weather data with more variation
        self.weather_data = {
            'current_temp': 82,
            'current_wind': 12,
            'hourly_temps': [],
            'hourly_winds': [],
            'hourly_rain': []
        }
        
        self.running = True
        self.generate_realistic_weather()
        
        print("🌤️  ENHANCED WEATHER FEATURES:")
        print(f"  🌡️  Current temp: {self.weather_data['current_temp']}°F")
        print(f"  💨 Current wind: {self.weather_data['current_wind']} mph")
        print("  🎨 DRAMATIC color gradients for better visibility")
        print("  🌪️  ENHANCED curve effects for wind visualization")
        print("  ⚡ Pulsing center shows current conditions")
        
    def generate_realistic_weather(self):
        """Generate realistic Austin weather patterns with more drama"""
        now = datetime.now()
        base_temp = 80  # Hot Austin summer
        
        # Current conditions with more variation
        self.weather_data['current_temp'] = base_temp + random.randint(-10, 15)
        self.weather_data['current_wind'] = random.randint(5, 25)
        
        print("🌦️  Generating 24-hour Austin weather forecast...")
        
        # 24-hour forecasts with realistic patterns
        for i in range(24):
            hour = (now.hour + i) % 24
            
            # Temperature: dramatic daily cycle
            if 6 <= hour <= 18:  # Daytime heating
                temp_base = base_temp + (hour - 12) * 1.5  # Peak at 3pm
            else:  # Nighttime cooling
                temp_base = base_temp - 8 + random.randint(-3, 3)
            
            # Add weather front effects
            if 8 <= i <= 12:  # Afternoon storm system
                temp_base -= random.randint(8, 15)  # Cooler with storms
                
            self.weather_data['hourly_temps'].append(int(temp_base + random.randint(-5, 8)))
            
            # Wind: More dramatic variations
            if 10 <= i <= 16:  # Afternoon winds pick up
                wind = random.randint(10, 30)
            elif 20 <= i <= 24 or 0 <= i <= 6:  # Calm overnight
                wind = random.randint(2, 8) 
            else:
                wind = random.randint(5, 15)
                
            self.weather_data['hourly_winds'].append(wind)
            
            # Rain: Realistic Austin storm patterns
            if 14 <= i <= 18:  # Afternoon thunderstorms
                rain = random.randint(40, 90)
            elif 20 <= i <= 24:  # Evening showers
                rain = random.randint(20, 50)
            else:  # Generally clear
                rain = random.randint(0, 25)
                
            self.weather_data['hourly_rain'].append(rain)
        
        # Print sample forecast
        print(f"  📊 Temp range: {min(self.weather_data['hourly_temps'])}°F - {max(self.weather_data['hourly_temps'])}°F")
        print(f"  💨 Wind range: {min(self.weather_data['hourly_winds'])} - {max(self.weather_data['hourly_winds'])} mph")
        print(f"  🌧️ Max rain chance: {max(self.weather_data['hourly_rain'])}%")
    
    def temp_to_color(self, temp_f):
        """Enhanced temperature colors - more dramatic"""
        # Expanded temperature range for more color variation
        temp_clamped = max(60, min(110, temp_f))  # Wider range
        
        if temp_f < 70:      # Cold - deep blues/purples
            hue = 240 + (70 - temp_f) * 2  # 240-280
            sat = 0.9
            val = 0.8
        elif temp_f < 85:    # Moderate - blue to green to yellow  
            progress = (temp_f - 70) / 15
            hue = 240 - progress * 120  # 240 to 120
            sat = 0.8
            val = 0.9
        else:               # Hot - yellow to red
            progress = (temp_f - 85) / 25  
            hue = 60 - progress * 60  # 60 to 0 (yellow to red)
            sat = 0.9 + progress * 0.1  # More saturated when hot
            val = 0.9
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def wind_to_color(self, wind_mph):
        """Enhanced wind colors - more dramatic"""
        wind_clamped = max(0, min(40, wind_mph))
        
        if wind_mph < 5:      # Calm - soft greens
            hue = 120
            sat = 0.4
            val = 0.7
        elif wind_mph < 15:   # Breezy - green to yellow
            progress = (wind_mph - 5) / 10
            hue = 120 - progress * 60  # Green to yellow
            sat = 0.6 + progress * 0.3
            val = 0.8
        elif wind_mph < 25:   # Windy - yellow to orange
            progress = (wind_mph - 15) / 10
            hue = 60 - progress * 30   # Yellow to orange
            sat = 0.9
            val = 0.9
        else:                # Strong - orange to red
            progress = (wind_mph - 25) / 15
            hue = 30 - progress * 30   # Orange to red
            sat = 1.0
            val = 0.9
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def rain_to_color(self, rain_percent):
        """Enhanced rain colors - more dramatic blues"""
        intensity = rain_percent / 100.0
        
        if rain_percent < 20:    # Low chance - light grays
            hue = 220
            sat = 0.2
            val = 0.8
        elif rain_percent < 50:  # Moderate - light blues
            hue = 220
            sat = 0.4 + intensity * 0.3
            val = 0.7 + intensity * 0.2
        else:                   # High chance - deep blues
            hue = 220 + (intensity - 0.5) * 40  # Shift toward purple
            sat = 0.8 + intensity * 0.2
            val = 0.4 + intensity * 0.3
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
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
    
    def enhanced_curve_positions(self, angle, length, num_squares, wind_speed):
        """Enhanced curves that respond dramatically to wind"""
        positions = []
        
        # Curve intensity based on wind speed (more dramatic)
        curve_factor = min(wind_speed / 15.0, 1.5)  # Can curve beyond original range
        
        for i in range(num_squares):
            t = (i + 1) / num_squares
            distance = t * length
            
            # Enhanced curve calculation with multiple harmonics
            primary_curve = curve_factor * length * 0.4 * math.sin(math.pi * t)
            secondary_curve = curve_factor * length * 0.1 * math.sin(2 * math.pi * t)
            total_curve = primary_curve + secondary_curve
            
            # Base position
            base_x = distance * math.sin(angle)
            base_y = -distance * math.cos(angle)
            
            # Perpendicular direction for curve
            perp_x = -math.cos(angle) 
            perp_y = -math.sin(angle)
            
            # Apply curve
            x = int(self.center_x + base_x + total_curve * perp_x)
            y = int(self.center_y + base_y + total_curve * perp_y)
            
            positions.append((x - 2, y - 2))
        
        return positions
    
    def position_enhanced_weather_hand(self, squares, angle, length, weather_func, wind_curve=False):
        """Position squares with enhanced weather effects"""
        if wind_curve:
            positions = self.enhanced_curve_positions(angle, length, len(squares), self.weather_data['current_wind'])
        else:
            # Straight line positioning
            positions = []
            for i in range(len(squares)):
                progress = (i + 1) / len(squares)
                distance = progress * length
                x = int(self.center_x + distance * math.sin(angle))
                y = int(self.center_y - distance * math.cos(angle))
                positions.append((x - 2, y - 2))
        
        for i, square in enumerate(squares):
            progress = i / len(squares)
            color = weather_func(i, progress)
            
            x, y = positions[i]
            square.move_to(x, y)
            square.change_color(color)
            square.show()
    
    def get_temp_gradient(self, square_index, progress):
        """Enhanced temperature gradient"""
        hour_index = int(progress * 23)
        forecast_temp = self.weather_data['hourly_temps'][hour_index]
        return self.temp_to_color(forecast_temp)
    
    def get_wind_gradient(self, square_index, progress):
        """Enhanced wind gradient"""
        hour_index = int(progress * 23)
        wind_speed = self.weather_data['hourly_winds'][hour_index]
        return self.wind_to_color(wind_speed)
    
    def get_rain_gradient(self, square_index, progress):
        """Enhanced rain gradient"""
        hour_index = int(progress * 23)
        rain_chance = self.weather_data['hourly_rain'][hour_index]
        return self.rain_to_color(rain_chance)
    
    def pulse_center(self, second):
        """Enhanced center pulse showing current conditions"""
        for i, square in enumerate(self.center_squares):
            # Pulse with current temperature color
            temp_color = self.temp_to_color(self.weather_data['current_temp'])
            
            # Add pulsing brightness
            pulse = 0.7 + 0.3 * math.sin(second * 0.3 + i * 0.8)
            
            # Apply pulse to existing color (approximate)
            r = (temp_color >> 16) & 0xFF
            g = (temp_color >> 8) & 0xFF  
            b = temp_color & 0xFF
            
            # Brighten/dim based on pulse
            r = int(min(255, r * pulse))
            g = int(min(255, g * pulse))
            b = int(min(255, b * pulse))
            
            pulsed_color = (r << 16) | (g << 8) | b
            square.change_color(pulsed_color)
    
    def update_clock(self):
        while self.running:
            now = datetime.now()
            
            # Calculate angles
            hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
            minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
            second_angle = now.second * math.pi / 30
            
            # Enhanced weather hands
            self.position_enhanced_weather_hand(
                self.hour_squares, hour_angle, 65, 
                self.get_rain_gradient, wind_curve=False
            )
            
            self.position_enhanced_weather_hand(
                self.minute_squares, minute_angle, 85, 
                self.get_temp_gradient, wind_curve=False
            )
            
            self.position_enhanced_weather_hand(
                self.second_squares, second_angle, 105, 
                self.get_wind_gradient, wind_curve=True  # Wind hand curves!
            )
            
            # Enhanced center pulse
            self.pulse_center(now.second)
            
            time.sleep(1)
    
    def run(self):
        print("\n🌈 ENHANCED WEATHER CLOCK RUNNING!")
        print("✨ Dramatic color gradients and enhanced effects")
        print("🌪️  Wind curves second hand dynamically")
        print("⚡ Center pulses with current temperature")
        print("Press Ctrl+C to exit")
        
        update_thread = threading.Thread(target=self.update_clock, daemon=True)
        update_thread.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🌈 Enhanced weather cleanup...")
            self.running = False
            
            all_squares = (self.hour_squares + self.minute_squares + 
                          self.second_squares + self.center_squares)
            for square in all_squares:
                square.hide()
            
            self.display.close()

if __name__ == "__main__":
    clock = EnhancedWeatherClock()
    clock.run()