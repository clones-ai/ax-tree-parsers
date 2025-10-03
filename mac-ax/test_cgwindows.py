#!/usr/bin/env python3
"""
Test direct CGWindowList to see all open applications without hit-testing
"""

from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    kCGWindowOwnerName,
    kCGWindowBounds
)
import json

def test_all_windows():
    """Get all visible windows using CGWindowList directly"""
    options = kCGWindowListOptionOnScreenOnly
    windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
    
    app_windows = {}
    
    for window in windowList:
        app_name = None
        bounds = None
        
        for key, value in window.items():
            if key == kCGWindowOwnerName:
                app_name = value
            elif key == kCGWindowBounds:
                bounds = value
        
        if app_name and bounds:
            # Filter out tiny windows (likely system UI elements)
            if bounds["Width"] > 100 and bounds["Height"] > 100:
                if app_name not in app_windows:
                    app_windows[app_name] = []
                
                app_windows[app_name].append({
                    'bounds': bounds,
                    'display': 'primary' if bounds['Y'] >= 0 else 'secondary'
                })
    
    # Sort by app name for easier reading
    sorted_apps = dict(sorted(app_windows.items()))
    
    print("=== ALL DETECTED APPLICATIONS ===")
    for app_name, windows in sorted_apps.items():
        print(f"\n📱 {app_name}: {len(windows)} window(s)")
        for i, window in enumerate(windows):
            bounds = window['bounds']
            print(f"   Window {i+1}: {bounds['Width']}x{bounds['Height']} at ({bounds['X']}, {bounds['Y']}) - {window['display']}")
    
    return sorted_apps

if __name__ == "__main__":
    apps = test_all_windows()
    print(f"\n🎯 TOTAL: {len(apps)} applications with visible windows")