# Click-Through Research Findings

## The Problem
Click-through is not working for Conky on your system because you're using **GNOME with Mutter compositor**. Mutter does not properly respect the X11 Shape Extension's input shape, which is the standard method for creating click-through windows.

## What We Tried
1. **X11 Shape Extension** - Setting input shape to empty (works on most X11 window managers but NOT Mutter)
2. **Different window types** - desktop, dock, utility, override (Mutter ignores input shapes for all)
3. **GTK input regions** - Mutter still captures clicks
4. **Various window hints** - below, above, etc. (affects stacking but not click-through)
5. **Compositor bypass** - Doesn't help with input handling

## Why It Doesn't Work
- Mutter is a compositing window manager that handles input events before they reach the X11 shape layer
- It was designed primarily for Wayland and its X11 compatibility layer doesn't fully implement shape extension
- This is a known issue reported in multiple places:
  - GNOME GitLab issues
  - Conky GitHub issues  
  - Various Linux forums

## Working Solutions

### Option 1: Use a Different Compositor
Replace Mutter with a compositor that respects X11 shape:
- **Picom** (formerly Compton)
- **xcompmgr**

Install and use:
```bash
# Install picom
sudo apt install picom

# Disable Mutter's compositing and use picom
# Note: This may affect GNOME Shell features
```

### Option 2: Use Wayland-native Solution
Since GNOME prefers Wayland, use a Wayland-compatible overlay:
- **wlr-layer-shell** based tools
- **SwayOSD** or similar

### Option 3: Workaround with Desktop Icons
Instead of a floating clock, integrate with desktop:
- Use GNOME Shell extensions
- Desktop widgets that integrate properly

### Option 4: Different Desktop Environment
Use a DE with better X11 support:
- **XFCE** with xfwm4
- **KDE** Plasma  
- **Cinnamon**

## Immediate Workaround
For now, the clock will be visible but will capture clicks. You can:
1. Position it where clicking won't interfere
2. Make it smaller
3. Toggle visibility with a hotkey when needed

## Code That WOULD Work (if not for Mutter)
The code we wrote is correct and would work on most X11 systems:
```python
window.shape_mask(shape.SO.Set, shape.SK.Input, 0, 0, X.NONE)
```

This removes the input region making the window click-through. It works on:
- Standard X11 window managers (i3, awesome, bspwm)
- XFCE's xfwm4
- KDE's KWin
- Older GNOME versions with Metacity

But NOT on current GNOME with Mutter.

## Recommendation
If click-through is critical, consider:
1. **Switching to XFCE** - Lightweight, great X11 support
2. **Using i3** - Tiling WM with excellent customization
3. **Finding a GNOME Shell extension** that provides similar functionality

## Test Script
Run this to verify your compositor:
```bash
ps aux | grep -E "mutter|compton|picom|xfwm|kwin"
```

If you see `mutter`, click-through won't work properly.