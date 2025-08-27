#!/usr/bin/env python3
"""
Clock v9: Smooth Gradient Weather Clock
- Each individual square contains its own gradient (no more solid blocks!)
- Color variation in both radial axis (along hand) AND perpendicular axis (across hand width)
- Eliminates blocky appearance with smooth gradient squares
- Uses Cairo for smooth gradient rendering within each square
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import time
import threading
from datetime import datetime
import random

class GradientSquare(Gtk.Window):
    """Individual square with internal gradient - no more solid blocks!"""
    
    def __init__(self, size=6):
        super().__init__()
        self.size = size
        self.gradient_colors = [(1, 1, 1), (1, 1, 1)]  # Default white
        
        # Window setup
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_size_request(size, size)
        
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
        """Draw gradient within this square"""
        # Create radial gradient for each square
        gradient = cairo.RadialGradient(
            self.size/2, self.size/2, 0,  # Inner circle (center)
            self.size/2, self.size/2, self.size/2  # Outer circle (edge)
        )
        
        # Add color stops for smooth internal gradient
        r1, g1, b1 = self.gradient_colors[0]
        r2, g2, b2 = self.gradient_colors[1]
        
        gradient.add_color_stop_rgba(0, r1, g1, b1, 1.0)    # Center
        gradient.add_color_stop_rgba(0.7, (r1+r2)/2, (g1+g2)/2, (b1+b2)/2, 1.0)  # Mid
        gradient.add_color_stop_rgba(1, r2, g2, b2, 1.0)    # Edge
        
        cr.set_source(gradient)
        cr.rectangle(0, 0, self.size, self.size)
        cr.fill()
        
        return True
    
    def update_gradient(self, color1, color2):
        """Update the gradient colors for this square"""
        self.gradient_colors = [color1, color2]
        self.queue_draw()
    
    def move_to_position(self, x, y):
        """Move square to position"""
        self.move(x, y)

class SmoothGradientClock:
    def __init__(self):
        # Get screen dimensions
        screen = Gdk.Screen.get_default()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        
        self.center_x = geometry.width - 250
        self.center_y = 200
        
        print(f"🎨 Creating SMOOTH GRADIENT clock at ({self.center_x}, {self.center_y})")
        print("✨ Each square contains smooth internal gradients")
        print("🌈 Color variation in both radial AND perpendicular axes")
        
        # Create gradient squares for each hand
        self.hour_squares = [GradientSquare(8) for _ in range(20)]    # Rain - bigger squares
        self.minute_squares = [GradientSquare(8) for _ in range(25)] # Temperature
        self.second_squares = [GradientSquare(6) for _ in range(30)] # Wind - thinner
        
        # Show all squares
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.show_all()
        
        # Rainbow center
        self.center_squares = []
        for i in range(9):  # 3x3 grid
            square = GradientSquare(10)  # Bigger center squares
            square.show_all()
            self.center_squares.append(square)
        
        # Weather data
        self.weather_data = {
            'temp_range': (60, 110),   # Wider range for better gradients
            'wind_range': (0, 40), 
            'rain_range': (0, 100),
            'hourly_temps': [],
            'hourly_winds': [], 
            'hourly_rain': []
        }
        
        self.running = True
        self.generate_smooth_weather()
        
        # Start updating
        GLib.timeout_add(1000, self.update_time)
        self.update_time()
        
    def generate_smooth_weather(self):
        """Generate weather data with smooth variations"""
        print("🌈 Generating smooth weather gradients...")
        
        for i in range(24):
            # Temperature with smooth daily curve
            time_of_day = i / 24.0  # 0 to 1
            base_temp = 80 + 15 * math.sin(2 * math.pi * (time_of_day - 0.25))  # Sine wave
            temp_variation = random.randint(-8, 8)
            self.weather_data['hourly_temps'].append(int(base_temp + temp_variation))
            
            # Wind with realistic patterns
            wind_base = 8 + 12 * math.sin(2 * math.pi * time_of_day + 1)  # Different phase
            wind_variation = random.randint(-5, 10)
            self.weather_data['hourly_winds'].append(max(0, int(wind_base + wind_variation)))
            
            # Rain with storm patterns
            if 0.5 <= time_of_day <= 0.75:  # Afternoon storms
                rain = random.randint(40, 95)
            else:
                rain = random.randint(0, 40)
            self.weather_data['hourly_rain'].append(rain)
        
        print(f"  🌡️ Smooth temp curve: {min(self.weather_data['hourly_temps'])}°F - {max(self.weather_data['hourly_temps'])}°F")
        print(f"  💨 Wind patterns: {min(self.weather_data['hourly_winds'])} - {max(self.weather_data['hourly_winds'])} mph")
    
    def weather_to_rainbow_color(self, value, value_range, spectrum_type):
        """Convert weather value to rainbow color with smooth mapping"""
        min_val, max_val = value_range
        normalized = max(0, min(1, (value - min_val) / (max_val - min_val)))
        
        if spectrum_type == 'temperature':
            # Cold purples → warm reds with smooth spectrum
            if normalized < 0.2:    # Cold: Deep purples/blues
                hue = 280 - normalized * 50  # 280-230°
                sat = 0.8 + normalized * 0.2
                val = 0.6 + normalized * 0.3
            elif normalized < 0.5:  # Cool: Blues to teals
                progress = (normalized - 0.2) / 0.3
                hue = 230 - progress * 50    # 230-180°
                sat = 0.7 + progress * 0.2
                val = 0.8
            elif normalized < 0.8:  # Warm: Greens to yellows
                progress = (normalized - 0.5) / 0.3
                hue = 120 - progress * 60    # 120-60°
                sat = 0.8
                val = 0.9
            else:                   # Hot: Yellows to reds
                progress = (normalized - 0.8) / 0.2
                hue = 45 - progress * 45     # 45-0°
                sat = 0.9 + progress * 0.1
                val = 0.95
                
        elif spectrum_type == 'wind':
            # Calm greens → violent magentas
            hue = 120 - normalized * 150  # 120° to -30° (wraps to 330°)
            if hue < 0: hue += 360
            sat = 0.6 + normalized * 0.4
            val = 0.7 + normalized * 0.3
            
        else:  # rain
            # Clear whites → storm purples
            hue = 220 + normalized * 40  # 220-260°
            sat = 0.2 + normalized * 0.8
            val = 0.9 - normalized * 0.4
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB tuple (0-1 range)"""
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
        
        return (r + m, g + m, b + m)
    
    def position_smooth_gradient_hand(self, squares, angle, length, weather_type, wind_curve=False):
        """Position squares with smooth gradients in both axes"""
        
        for i, square in enumerate(squares):
            # Position along hand
            progress = i / len(squares)
            distance = progress * length
            
            # Base position
            base_x = distance * math.sin(angle)
            base_y = -distance * math.cos(angle)
            
            # Add curve for wind
            if wind_curve and len(self.weather_data['hourly_winds']) > 0:
                current_wind = self.weather_data['hourly_winds'][0]
                curve_factor = current_wind / 40.0
                curve_offset = curve_factor * length * 0.5 * math.sin(math.pi * progress)
                perp_x = -math.cos(angle)
                perp_y = -math.sin(angle)
                base_x += curve_offset * perp_x
                base_y += curve_offset * perp_y
            
            # Final position
            x = int(self.center_x + base_x - 4)  # Center square
            y = int(self.center_y + base_y - 4)
            
            square.move_to_position(x, y)
            
            # Get weather values for this position
            hour_index = int(progress * 23)
            
            if weather_type == 'temperature':
                primary_value = self.weather_data['hourly_temps'][hour_index]
                value_range = self.weather_data['temp_range']
                spectrum = 'temperature'
                
                # Add perpendicular axis variation
                perp_variation = math.sin(i * 0.5) * 10  # Vary across width
                secondary_value = primary_value + perp_variation
                
            elif weather_type == 'wind':
                primary_value = self.weather_data['hourly_winds'][hour_index]
                value_range = self.weather_data['wind_range']
                spectrum = 'wind'
                
                # Wind turbulence variation
                perp_variation = math.cos(i * 0.7) * 5
                secondary_value = primary_value + perp_variation
                
            else:  # rain
                primary_value = self.weather_data['hourly_rain'][hour_index]
                value_range = self.weather_data['rain_range']
                spectrum = 'rain'
                
                # Rain intensity variation
                perp_variation = math.sin(i * 0.3) * 15
                secondary_value = primary_value + perp_variation
            
            # Get gradient colors
            color1 = self.weather_to_rainbow_color(primary_value, value_range, spectrum)
            color2 = self.weather_to_rainbow_color(max(0, secondary_value), value_range, spectrum)
            
            # Update square gradient
            square.update_gradient(color1, color2)
    
    def update_rainbow_center(self, second):
        """Rainbow pulsing center with gradients"""
        for i, square in enumerate(self.center_squares):
            # Position in 3x3 grid
            row = i // 3
            col = i % 3
            x = self.center_x - 15 + col * 10
            y = self.center_y - 15 + row * 10
            square.move_to_position(x, y)
            
            # Rainbow colors with time-based animation
            hue1 = (second * 15 + i * 40) % 360
            hue2 = (hue1 + 60) % 360
            
            pulse = 0.7 + 0.3 * math.sin(second * 0.5 + i * 0.8)
            
            color1 = self.hsv_to_rgb(hue1, 0.8, pulse)
            color2 = self.hsv_to_rgb(hue2, 0.6, pulse * 0.8)
            
            square.update_gradient(color1, color2)
    
    def update_time(self):
        """Update all hands with smooth gradients"""
        now = datetime.now()
        
        # Calculate angles
        hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
        minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
        second_angle = now.second * math.pi / 30
        
        # Update hands with smooth gradients
        self.position_smooth_gradient_hand(
            self.hour_squares, hour_angle, 100, 'rain', wind_curve=False
        )
        
        self.position_smooth_gradient_hand(
            self.minute_squares, minute_angle, 130, 'temperature', wind_curve=False
        )
        
        self.position_smooth_gradient_hand(
            self.second_squares, second_angle, 160, 'wind', wind_curve=True
        )
        
        # Update rainbow center
        self.update_rainbow_center(now.second)
        
        return True  # Continue timeout
    
    def cleanup(self):
        """Clean up all squares"""
        all_squares = (self.hour_squares + self.minute_squares + 
                      self.second_squares + self.center_squares)
        for square in all_squares:
            square.destroy()

def main():
    print("\n🎨 SMOOTH GRADIENT WEATHER CLOCK!")
    print("✨ No more blocky squares - smooth gradients within each square")
    print("🌈 Color variation in radial AND perpendicular axes")
    print("Press Ctrl+C to exit")
    
    clock = SmoothGradientClock()
    
    def cleanup_and_quit(widget=None):
        clock.cleanup()
        Gtk.main_quit()
    
    # Connect cleanup to any square destruction
    if clock.hour_squares:
        clock.hour_squares[0].connect("destroy", cleanup_and_quit)
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\n🎨 Smooth gradient cleanup...")
        cleanup_and_quit()

if __name__ == "__main__":
    main()