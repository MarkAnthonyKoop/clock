#!/usr/bin/env python3
"""
Clock v10: Wiggling Wind Weather Clock
- Smooth gradients within each square (no blockiness)
- Second hand WIGGLES and SQUIRMS based on wind gustiness
- High wind = lots of chaotic motion, Low wind = gentle waves, No wind = straight line
- Color variation in both radial AND perpendicular axes
- Dynamic wind animation that changes with current conditions
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
    """Individual square with internal gradient"""
    
    def __init__(self, size=6):
        super().__init__()
        self.size = size
        self.gradient_colors = [(1, 1, 1), (1, 1, 1)]
        
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_size_request(size, size)
        
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)
        
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)
        
    def on_draw(self, widget, cr):
        # Create smooth radial gradient within square
        gradient = cairo.RadialGradient(
            self.size/2, self.size/2, 0,
            self.size/2, self.size/2, self.size/2
        )
        
        r1, g1, b1 = self.gradient_colors[0]
        r2, g2, b2 = self.gradient_colors[1]
        
        gradient.add_color_stop_rgba(0, r1, g1, b1, 1.0)
        gradient.add_color_stop_rgba(0.5, (r1+r2)/2, (g1+g2)/2, (b1+b2)/2, 1.0)
        gradient.add_color_stop_rgba(1, r2, g2, b2, 1.0)
        
        cr.set_source(gradient)
        cr.rectangle(0, 0, self.size, self.size)
        cr.fill()
        
        return True
    
    def update_gradient(self, color1, color2):
        self.gradient_colors = [color1, color2]
        self.queue_draw()
    
    def move_to_position(self, x, y):
        self.move(x, y)

class WigglingWindClock:
    def __init__(self):
        screen = Gdk.Screen.get_default()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        
        self.center_x = geometry.width - 250
        self.center_y = 200
        
        print(f"🌪️ Creating WIGGLING WIND clock at ({self.center_x}, {self.center_y})")
        print("✨ Smooth gradients + dynamic wind wiggle effects")
        
        # Create gradient squares
        self.hour_squares = [GradientSquare(8) for _ in range(20)]
        self.minute_squares = [GradientSquare(8) for _ in range(25)]
        self.second_squares = [GradientSquare(6) for _ in range(30)]
        
        for squares in [self.hour_squares, self.minute_squares, self.second_squares]:
            for square in squares:
                square.show_all()
        
        # Rainbow center
        self.center_squares = []
        for i in range(9):
            square = GradientSquare(10)
            square.show_all()
            self.center_squares.append(square)
        
        # Weather with dynamic wind patterns
        self.weather_data = {
            'temp_range': (55, 115),
            'wind_range': (0, 45),
            'rain_range': (0, 100),
            'current_wind': 15,
            'current_gusts': 22,  # Gust factor for wiggle intensity
            'hourly_temps': [],
            'hourly_winds': [],
            'hourly_rain': []
        }
        
        self.running = True
        self.generate_windy_weather()
        
        # Animation state for wiggling
        self.wiggle_time = 0
        self.wiggle_phase_offsets = [random.random() * 2 * math.pi for _ in range(30)]
        
        # Start updating more frequently for smooth wind animation
        GLib.timeout_add(100, self.update_time)  # 10 FPS for smooth wiggling
        self.update_time()
        
    def generate_windy_weather(self):
        """Generate weather with realistic wind patterns"""
        print("🌪️ Generating dynamic wind patterns...")
        
        for i in range(24):
            # Temperature with realistic daily cycle
            hour = i
            if 6 <= hour <= 18:  # Daytime
                temp_base = 75 + (hour - 12) * 2  # Peak afternoon heat
            else:  # Nighttime
                temp_base = 65 + random.randint(-5, 5)
            
            temp_variation = random.randint(-8, 15)
            self.weather_data['hourly_temps'].append(max(55, min(115, temp_base + temp_variation)))
            
            # Wind with gusty patterns
            if 10 <= hour <= 16:  # Afternoon winds
                base_wind = random.randint(8, 25)
                gust_factor = random.randint(5, 20)  # Additional gusting
            elif 18 <= hour <= 22:  # Evening storms
                base_wind = random.randint(15, 35) 
                gust_factor = random.randint(10, 25)
            else:  # Calm periods
                base_wind = random.randint(2, 12)
                gust_factor = random.randint(0, 8)
                
            total_wind = min(45, base_wind + gust_factor)
            self.weather_data['hourly_winds'].append(total_wind)
            
            # Rain patterns
            if 13 <= hour <= 18:  # Afternoon storms
                rain = random.randint(30, 95)
            else:
                rain = random.randint(0, 45)
            self.weather_data['hourly_rain'].append(rain)
        
        # Set current conditions
        current_hour = datetime.now().hour % 24
        self.weather_data['current_wind'] = self.weather_data['hourly_winds'][current_hour]
        self.weather_data['current_gusts'] = self.weather_data['current_wind'] + random.randint(3, 12)
        
        print(f"  🌪️ Current wind: {self.weather_data['current_wind']} mph")
        print(f"  💨 Current gusts: {self.weather_data['current_gusts']} mph") 
        print(f"  🌡️ Temp range: {min(self.weather_data['hourly_temps'])}°F - {max(self.weather_data['hourly_temps'])}°F")
        print(f"  📊 Wind range: {min(self.weather_data['hourly_winds'])} - {max(self.weather_data['hourly_winds'])} mph")
        
    def calculate_wind_wiggle(self, base_angle, base_length, square_index, current_time):
        """Calculate wiggling motion based on wind conditions"""
        current_wind = self.weather_data['current_wind']
        current_gusts = self.weather_data['current_gusts']
        
        # Base position without wiggle
        progress = square_index / len(self.second_squares)
        distance = progress * base_length
        base_x = distance * math.sin(base_angle)
        base_y = -distance * math.cos(base_angle)
        
        if current_wind <= 2:
            # No wind - perfectly straight line
            wiggle_x = 0
            wiggle_y = 0
            
        elif current_wind <= 8:
            # Light breeze - gentle sinusoidal wave
            wave_freq = 0.8
            wave_amplitude = 3
            phase = self.wiggle_phase_offsets[square_index]
            
            wiggle_x = wave_amplitude * math.sin(current_time * wave_freq + phase + progress * math.pi)
            wiggle_y = wave_amplitude * 0.5 * math.cos(current_time * wave_freq * 1.3 + phase)
            
        elif current_wind <= 18:
            # Moderate wind - more complex wave patterns
            primary_freq = 1.5
            secondary_freq = 2.8
            amplitude = 6 + (current_wind - 8) * 0.8
            phase = self.wiggle_phase_offsets[square_index]
            
            wiggle_x = amplitude * (
                math.sin(current_time * primary_freq + phase + progress * math.pi * 1.5) +
                0.4 * math.sin(current_time * secondary_freq + phase * 1.7)
            )
            wiggle_y = amplitude * 0.6 * (
                math.cos(current_time * primary_freq * 1.2 + phase) +
                0.3 * math.sin(current_time * secondary_freq * 1.4 + phase * 2.1)
            )
            
        else:
            # Strong/gusty wind - chaotic squirming motion
            chaos_level = min(1.0, current_wind / 35.0)
            gust_factor = current_gusts / current_wind if current_wind > 0 else 1.0
            
            # Multiple overlapping frequencies for chaotic motion
            base_amplitude = 8 + chaos_level * 12
            gust_amplitude = base_amplitude * (gust_factor - 1.0) * 0.8
            
            phase = self.wiggle_phase_offsets[square_index]
            
            # Primary chaotic motion
            primary_wiggle_x = base_amplitude * math.sin(current_time * 2.2 + phase + progress * math.pi * 2)
            primary_wiggle_y = base_amplitude * 0.7 * math.cos(current_time * 1.8 + phase * 1.3)
            
            # Secondary turbulence
            secondary_wiggle_x = base_amplitude * 0.6 * math.sin(current_time * 4.1 + phase * 2.7 + square_index * 0.5)
            secondary_wiggle_y = base_amplitude * 0.5 * math.cos(current_time * 3.3 + phase * 1.9)
            
            # Gusty variations (rapid changes)
            gust_wiggle_x = gust_amplitude * math.sin(current_time * 8.5 + phase * 3.1)
            gust_wiggle_y = gust_amplitude * 0.4 * math.cos(current_time * 7.2 + phase * 2.8)
            
            # Random jitter for extreme wind
            jitter_x = chaos_level * 2 * (random.random() - 0.5)
            jitter_y = chaos_level * 2 * (random.random() - 0.5)
            
            wiggle_x = primary_wiggle_x + secondary_wiggle_x + gust_wiggle_x + jitter_x
            wiggle_y = primary_wiggle_y + secondary_wiggle_y + gust_wiggle_y + jitter_y
        
        # Apply wiggle to position
        final_x = int(self.center_x + base_x + wiggle_x)
        final_y = int(self.center_y + base_y + wiggle_y)
        
        return final_x, final_y
    
    def weather_to_rainbow_color(self, value, value_range, spectrum_type):
        """Weather to rainbow color mapping"""
        min_val, max_val = value_range
        normalized = max(0, min(1, (value - min_val) / (max_val - min_val)))
        
        if spectrum_type == 'temperature':
            if normalized < 0.25:     # Cold: Deep blues/purples
                hue = 270 - normalized * 60
                sat = 0.8 + normalized * 0.2
                val = 0.6 + normalized * 0.3
            elif normalized < 0.5:    # Cool: Blues to teals
                progress = (normalized - 0.25) / 0.25
                hue = 210 - progress * 30
                sat = 0.7 + progress * 0.2
                val = 0.8
            elif normalized < 0.75:   # Warm: Greens to yellows
                progress = (normalized - 0.5) / 0.25
                hue = 120 - progress * 60
                sat = 0.8
                val = 0.9
            else:                     # Hot: Yellows to reds
                progress = (normalized - 0.75) / 0.25
                hue = 50 - progress * 50
                sat = 0.9 + progress * 0.1
                val = 0.95
                
        elif spectrum_type == 'wind':
            hue = 120 - normalized * 140  # Green to magenta spectrum
            if hue < 0: hue += 360
            sat = 0.5 + normalized * 0.5
            val = 0.7 + normalized * 0.3
            
        else:  # rain
            hue = 220 + normalized * 50
            sat = 0.3 + normalized * 0.7
            val = 0.9 - normalized * 0.4
        
        return self.hsv_to_rgb(hue, sat, val)
    
    def hsv_to_rgb(self, h, s, v):
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
    
    def position_wiggling_wind_hand(self, squares, angle, length, weather_type):
        """Position hand with dynamic wind wiggling for second hand"""
        is_wind_hand = (weather_type == 'wind')
        
        for i, square in enumerate(squares):
            progress = i / len(squares)
            
            if is_wind_hand:
                # Apply wiggling motion based on wind conditions
                x, y = self.calculate_wind_wiggle(angle, length, i, self.wiggle_time)
            else:
                # Straight line for other hands
                distance = progress * length
                x = int(self.center_x + distance * math.sin(angle))
                y = int(self.center_y - distance * math.cos(angle))
            
            square.move_to_position(x - square.size//2, y - square.size//2)
            
            # Get weather colors
            hour_index = int(progress * 23)
            
            if weather_type == 'temperature':
                primary_value = self.weather_data['hourly_temps'][hour_index]
                value_range = self.weather_data['temp_range']
                spectrum = 'temperature'
                perp_variation = math.sin(i * 0.5) * 8
                
            elif weather_type == 'wind':
                primary_value = self.weather_data['hourly_winds'][hour_index]
                value_range = self.weather_data['wind_range']
                spectrum = 'wind'
                perp_variation = math.cos(i * 0.7 + self.wiggle_time) * 6  # Dynamic wind variation
                
            else:  # rain
                primary_value = self.weather_data['hourly_rain'][hour_index]
                value_range = self.weather_data['rain_range']
                spectrum = 'rain'
                perp_variation = math.sin(i * 0.3) * 12
            
            secondary_value = max(0, primary_value + perp_variation)
            
            color1 = self.weather_to_rainbow_color(primary_value, value_range, spectrum)
            color2 = self.weather_to_rainbow_color(secondary_value, value_range, spectrum)
            
            square.update_gradient(color1, color2)
    
    def update_rainbow_center(self, second):
        """Pulsing rainbow center"""
        for i, square in enumerate(self.center_squares):
            row = i // 3
            col = i % 3
            x = self.center_x - 15 + col * 10
            y = self.center_y - 15 + row * 10
            square.move_to_position(x, y)
            
            hue1 = (second * 12 + i * 40) % 360
            hue2 = (hue1 + 80) % 360
            
            pulse = 0.6 + 0.4 * math.sin(second * 0.6 + i * 0.9)
            
            color1 = self.hsv_to_rgb(hue1, 0.8, pulse)
            color2 = self.hsv_to_rgb(hue2, 0.6, pulse * 0.9)
            
            square.update_gradient(color1, color2)
    
    def update_time(self):
        """Update with dynamic wind wiggling"""
        now = datetime.now()
        self.wiggle_time += 0.1  # Increment animation time
        
        # Calculate angles
        hour_angle = (now.hour % 12 + now.minute / 60.0) * math.pi / 6
        minute_angle = (now.minute + now.second / 60.0) * math.pi / 30
        second_angle = now.second * math.pi / 30
        
        # Update hands
        self.position_wiggling_wind_hand(
            self.hour_squares, hour_angle, 100, 'rain'
        )
        
        self.position_wiggling_wind_hand(
            self.minute_squares, minute_angle, 130, 'temperature'
        )
        
        self.position_wiggling_wind_hand(
            self.second_squares, second_angle, 160, 'wind'  # This one wiggles!
        )
        
        self.update_rainbow_center(now.second)
        
        return True
    
    def cleanup(self):
        all_squares = (self.hour_squares + self.minute_squares + 
                      self.second_squares + self.center_squares)
        for square in all_squares:
            square.destroy()

def main():
    print("\n🌪️ WIGGLING WIND WEATHER CLOCK!")
    print("✨ Smooth gradients + dynamic wind wiggling effects")
    print("💨 Second hand movement based on current wind conditions:")
    print("   🌬️  0-2 mph: Perfectly straight")
    print("   🍃 3-8 mph: Gentle waves")
    print("   🌪️  9-18 mph: Complex wave patterns")
    print("   🌀 19+ mph: Chaotic squirming and gusting!")
    print("Press Ctrl+C to exit")
    
    clock = WigglingWindClock()
    
    def cleanup_and_quit(widget=None):
        clock.cleanup()
        Gtk.main_quit()
    
    if clock.hour_squares:
        clock.hour_squares[0].connect("destroy", cleanup_and_quit)
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\n🌪️ Wind wiggle cleanup...")
        cleanup_and_quit()

if __name__ == "__main__":
    main()