#!/bin/bash
# Fix Conky click-through on GNOME/Mutter
# The issue: Mutter doesn't respect X11 shape extension properly
# Solution: Use both xprop and shape extension together

echo "Fixing Conky click-through for GNOME/Mutter..."

# Kill existing conky
pkill -9 conky

# Start conky with specific settings for Mutter
cat > /tmp/conky_mutter.conf << 'EOF'
conky.config = {
  alignment = 'top_right',
  background = false,
  
  own_window = true,
  own_window_type = 'normal',  -- Normal window type works better with Mutter
  own_window_argb_visual = true,
  own_window_argb_value = 0,
  own_window_transparent = true,
  own_window_hints = 'undecorated,sticky,skip_taskbar,skip_pager,above',
  
  double_buffer = true,
  update_interval = 1,

  use_xft = true,
  default_color = 'FFFFFF',
  draw_shades = false,
  draw_outline = false,

  minimum_width = 220, minimum_height = 220,
  gap_x = 40, gap_y = 40,

  lua_load = '~/.config/conky/clock.lua',
  lua_draw_hook_pre = 'clock_rings',
};
conky.text = [[]];
EOF

# Start conky
conky -c /tmp/conky_mutter.conf &
CONKY_PID=$!

# Wait for window to appear
sleep 3

# Find the window ID
WINDOW_ID=$(wmctrl -l | grep -i conky | head -1 | awk '{print $1}')

if [ -z "$WINDOW_ID" ]; then
    echo "Conky window not found!"
    exit 1
fi

echo "Found Conky window: $WINDOW_ID"

# Apply multiple fixes for Mutter compatibility
echo "Applying Mutter-specific fixes..."

# 1. Set window type to desktop (helps with some compositors)
xprop -id $WINDOW_ID -f _NET_WM_WINDOW_TYPE 32a \
    -set _NET_WM_WINDOW_TYPE _NET_WM_WINDOW_TYPE_DESKTOP

# 2. Bypass compositor
xprop -id $WINDOW_ID -f _NET_WM_BYPASS_COMPOSITOR 32c \
    -set _NET_WM_BYPASS_COMPOSITOR 2

# 3. Use Python to apply X11 shape (this part still helps even if Mutter ignores it partially)
python3 << EOF
from Xlib import X, display
from Xlib.ext import shape

d = display.Display()
window_id = int("$WINDOW_ID", 16)
window = d.create_resource_object('window', window_id)

# Remove input shape
window.shape_mask(shape.SO.Set, shape.SK.Input, 0, 0, X.NONE)
d.sync()
print("Applied X11 shape mask")
EOF

# 4. Special Mutter workaround: Set window to not accept focus
xprop -id $WINDOW_ID -f WM_HINTS 32i -set WM_HINTS 0

echo "Fixes applied!"
echo ""
echo "Testing click-through..."

# Test with automated click
python3 << 'EOF'
import pyautogui
import time
import subprocess

pyautogui.FAILSAFE = False
screen_width, screen_height = pyautogui.size()

# Click where the clock should be
test_x = screen_width - 110
test_y = 110

print(f"Moving to ({test_x}, {test_y}) and clicking...")
pyautogui.moveTo(test_x, test_y, duration=0.5)
time.sleep(0.5)
pyautogui.click()
time.sleep(1)

# Take screenshot
subprocess.run(["scrot", "/tmp/conky_test.png"])
print("Screenshot saved to /tmp/conky_test.png")
EOF

echo ""
echo "Check /tmp/conky_test.png to see if click-through worked"
echo "If a desktop menu appeared, click-through is NOT working"
echo "If nothing happened, click-through IS working"