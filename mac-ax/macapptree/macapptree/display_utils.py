import AppKit
import ApplicationServices

def get_display_for_point(point):
    """Find which display contains the given point"""
    for screen in AppKit.NSScreen.screens():
        screen_frame = screen.frame()
        if AppKit.NSPointInRect(point, screen_frame):
            return screen
    return None

def get_display_info():
    """Get information about all available displays"""
    displays = []
    for i, screen in enumerate(AppKit.NSScreen.screens()):
        frame = screen.frame()
        is_primary = i == 0  # First screen is typically primary
        displays.append({
            'index': i,
            'frame': {
                'x': frame.origin.x,
                'y': frame.origin.y,
                'width': frame.size.width,
                'height': frame.size.height
            },
            'scale_factor': screen.backingScaleFactor(),
            'is_primary': is_primary
        })
    return displays

def get_window_display(window_element):
    """Determine which display contains the given window"""
    window_center_x = window_element.position.x + (window_element.size.width / 2)
    window_center_y = window_element.position.y + (window_element.size.height / 2)
    center_point = AppKit.NSMakePoint(window_center_x, window_center_y)
    
    return get_display_for_point(center_point)

def should_record_display(target_display_index, recording_display_index=None):
    """Check if we should record from the display that contains the target window"""
    if recording_display_index is None:
        # Default to primary display (index 0)
        recording_display_index = 0
    
    return target_display_index == recording_display_index

def log_display_mismatch(window_display_index, recording_display_index):
    """Log when window and recording displays don't match"""
    if window_display_index != recording_display_index:
        print(f"WARNING: Window is on display {window_display_index} but recording from display {recording_display_index}")
        print("This may cause AXTree extraction to fail")
        return True
    return False