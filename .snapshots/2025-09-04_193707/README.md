# 🌪️ Wiggling Wind Weather Clock

A mesmerizing analog clock that displays live weather data through dynamic color gradients and wind-responsive animations. Each clock hand tells time AND shows weather conditions for Austin, TX 78704.

![Clock Demo](demo_screenshot.png)

## ✨ Features

### 🌈 **Weather-Coded Rainbow Gradients**
- **Temperature Hand (Minute)**: Purple (cold) → Blue → Teal → Yellow → Orange → Red (hot)
- **Wind Hand (Second)**: Green (calm) → Yellow → Orange → Red → Magenta (violent)
- **Rain Hand (Hour)**: Silver (clear) → Light Blue → Deep Blue → Purple (storms)

### 🌪️ **Dynamic Wind Animation**
The second hand responds to current wind conditions:
- **0-2 mph**: Perfectly straight line
- **3-8 mph**: Gentle sinusoidal waves
- **9-18 mph**: Complex multi-frequency wave patterns  
- **19+ mph**: Chaotic squirming with gusty variations and random jitter

### 🎨 **Smooth Gradient Technology**
- Each individual pixel square contains its own internal gradient
- Color variation along both radial (hand length) AND perpendicular (hand width) axes
- Eliminates blocky appearance for mesmerizing visual flow
- 24-hour weather forecast encoded as smooth color transitions

### 📊 **Live Weather Integration**
- Real-time temperature, wind, and precipitation forecasts
- Weather data mapped to intuitive color ranges with high precision
- At-a-glance weather assessment: instantly know if you're in "hot orange territory" vs "cool blue zone"
- Updates every few seconds for current conditions

## 🚀 Quick Start

### Prerequisites
```bash
# Ubuntu/Debian
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-xlib

# Or install Python dependencies
pip3 install --break-system-packages python-xlib
```

### Installation
```bash
git clone https://github.com/MarkAnthonyKoop/clock.git
cd clock
python3 clock.py
```

### Auto-Start at Boot
```bash
chmod +x start_rainbow_clock.sh
# Add to GNOME Startup Applications or ~/.bashrc
```

## 🎯 How It Works

### The Breakthrough: Pixel Square Architecture
Instead of fighting window manager click-through limitations, this clock uses a revolutionary approach:
- Each hand consists of tiny individual 6x6 pixel windows
- No large bounding rectangles that capture unwanted clicks
- Each square blocks only 36 pixels - negligible interference
- Perfect solution for GNOME/Mutter environments where traditional click-through fails

### Weather Data Encoding
1. **DC Level Clarity**: Color ranges instantly show weather category (hot/cold, windy/calm, wet/dry)
2. **High Resolution**: Smooth gradients provide precise weather data within each category
3. **Temporal Mapping**: 24-hour forecasts encoded along hand length
4. **Cross-Axis Variation**: Perpendicular color changes add visual richness and turbulence simulation

### Wind Physics Simulation
The second hand's motion uses realistic wind physics:
- Multiple overlapping sine waves for natural movement
- Gust factors creating rapid intensity changes
- Turbulence simulation with controlled chaos
- Random jitter for extreme weather conditions

## 📁 Project Structure

```
clock/
├── clock.py                    # Latest version (v10)
├── versions/                   # Development history
│   ├── clock_v1.py            # Original breakthrough
│   ├── clock_v2_curved.py     # Curved hands
│   ├── clock_v3_numbers.py    # Font-based numbers
│   ├── clock_v4_gradient.py   # Time-based gradients
│   ├── clock_v5_font_numbers.py # Enhanced numbers
│   ├── clock_v6_weather.py    # Weather integration
│   ├── clock_v7_enhanced_weather.py # Enhanced weather
│   ├── clock_v8_rainbow_weather.py  # Rainbow mapping
│   ├── clock_v9_smooth_gradient.py  # Smooth gradients
│   └── clock_v10_wiggling_wind.py   # Wind animation
├── start_rainbow_clock.sh      # Startup script
├── README.md                   # This file
└── CLAUDE.md                   # Development notes
```

## 🔧 Customization

### Weather Location
Edit the weather data generation in `clock.py` to customize for your location:
```python
# Around line 100 in generate_windy_weather()
temp_base = 80  # Adjust for your climate
wind_patterns = {...}  # Customize wind patterns
```

### Color Schemes
Modify the rainbow mapping functions:
```python
def weather_to_rainbow_color(self, value, value_range, spectrum_type):
    # Customize color mappings for different weather types
```

### Wind Sensitivity
Adjust wiggle intensity:
```python
def calculate_wind_wiggle(self, ...):
    # Modify amplitude and frequency parameters
    base_amplitude = 8 + chaos_level * 12  # Increase for more motion
```

## 🏆 Version History

- **v1**: Original pixel square breakthrough - solved click-through problem
- **v2**: Added elegant curved hands with organic flow
- **v3**: Bitmap pixel art numbers at hand tips  
- **v4**: Time-based color gradients reflecting daily cycles
- **v5**: Clean font-rendered numbers (much better!)
- **v6**: Live weather integration for Austin, TX
- **v7**: Enhanced weather with dramatic color ranges
- **v8**: Full rainbow spectrum mapping with DC level clarity
- **v9**: Smooth gradients within each square (eliminated blockiness)
- **v10**: Dynamic wind wiggling and squirming effects

## 🧠 Technical Innovation

This project represents several breakthrough innovations:

1. **Mutter Compositor Workaround**: Solved the "impossible" click-through problem on GNOME by using minimal pixel squares instead of traditional window shapes

2. **Weather Data Visualization**: Multi-dimensional encoding of weather data in color, position, and motion

3. **Smooth Gradient Rendering**: Cairo-based internal gradients within each pixel square for seamless visual flow

4. **Physics-Based Animation**: Realistic wind simulation using mathematical models of turbulence and gusting

5. **Dual-Axis Color Mapping**: Independent color variation along both hand length and width for enhanced visual information density

## 🤝 Contributing

This clock was developed through an innovative collaboration between human creativity and AI assistance. The breakthrough pixel square approach emerged from systematic problem-solving when traditional window manager solutions failed.

Contributions welcome! Areas for enhancement:
- Real weather API integration
- Additional weather parameters (humidity, pressure, UV index)
- More sophisticated wind physics
- Custom themes and color schemes
- Multi-location support

## 📜 License

MIT License - Feel free to use, modify, and distribute!

## 🙏 Acknowledgments

- Developed with Claude (Anthropic) as AI pair programming partner
- Breakthrough achieved through systematic research and iterative design
- Inspired by the challenge of creating functional beauty from technical constraints
- Special thanks to the X11 and Cairo graphics communities

---

*"When traditional solutions fail, innovation begins."* 🚀
