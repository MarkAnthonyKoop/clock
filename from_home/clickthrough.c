#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/shape.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    Display *display;
    Window root, window;
    XSetWindowAttributes attrs;
    XVisualInfo vinfo;
    int screen;
    
    // Open display
    display = XOpenDisplay(NULL);
    if (!display) {
        fprintf(stderr, "Cannot open display\n");
        return 1;
    }
    
    screen = DefaultScreen(display);
    root = RootWindow(display, screen);
    
    // Get visual for transparency
    XMatchVisualInfo(display, screen, 32, TrueColor, &vinfo);
    
    // Set window attributes
    attrs.colormap = XCreateColormap(display, root, vinfo.visual, AllocNone);
    attrs.background_pixel = 0;
    attrs.border_pixel = 0;
    attrs.override_redirect = True;  // No window manager decorations
    
    // Create window (top-right corner)
    int width = 200, height = 200;
    int x = DisplayWidth(display, screen) - width - 50;
    int y = 50;
    
    window = XCreateWindow(
        display, root,
        x, y, width, height,
        0, vinfo.depth, InputOutput, vinfo.visual,
        CWColormap | CWBackPixel | CWBorderPixel | CWOverrideRedirect,
        &attrs
    );
    
    // Set window name
    XStoreName(display, window, "C ClickThrough Test");
    
    // Map window
    XMapWindow(display, window);
    XFlush(display);
    
    printf("Window created at (%d, %d) size %dx%d\n", x, y, width, height);
    printf("Window ID: 0x%lx\n", window);
    
    // Wait a moment for window to be mapped
    sleep(1);
    
    // Now make it click-through using Shape extension
    printf("Applying click-through with Shape extension...\n");
    
    // Method 1: Set input shape to nothing
    XShapeCombineMask(
        display, window,
        ShapeInput,     // Input shape (not Bounding shape)
        0, 0,          // x, y offset
        None,          // No pixmap = empty input region
        ShapeSet       // Operation
    );
    
    XFlush(display);
    printf("Click-through applied - input shape removed\n");
    
    // Draw something visible
    GC gc = XCreateGC(display, window, 0, NULL);
    XSetForeground(display, gc, 0xFFFF0000); // Red color
    XFillRectangle(display, window, gc, 0, 0, width, height);
    
    XSetForeground(display, gc, 0xFFFFFFFF); // White color  
    XDrawString(display, window, gc, 50, 100, "Click Through Test", 18);
    
    XFlush(display);
    
    printf("Window should be visible and click-through\n");
    printf("Press Ctrl+C to exit\n");
    
    // Keep window alive
    while (1) {
        sleep(1);
    }
    
    XCloseDisplay(display);
    return 0;
}