import json
import argparse
import time
from macapptree import get_app_bundle, get_tree

def get_tree_with_display_info(bundle, max_depth=None):
    """Wrapper around get_tree for consistency with the rest of the codebase"""
    return get_tree(bundle, max_depth)

from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    kCGWindowOwnerName,
    kCGWindowBounds
)

def get_accessibility_tree():
    INVALID_WINDOWS=['Window Server', 'Dock', 'Spotlight', 'SystemUIServer', 'ControlCenter', 'NotificationCenter', 'Finder', 'clones']
    options = kCGWindowListOptionOnScreenOnly
    windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
    # Convert windowList to a list of Python dictionaries
    app_names = []
    for window in windowList:
        real = False
        for key, value in window.items():
            if key == kCGWindowBounds:
                # Accept windows on any display (Y can be negative for secondary displays)
                # Filter out tiny windows (likely system UI elements)
                if value["Width"] > 100 and value["Height"] > 100:
                    real = True
        for key, value in window.items():
            if key == kCGWindowOwnerName and real == True:
                if value not in INVALID_WINDOWS:
                    app_names.append(value)

    out = []
    for app in app_names:
        try:
            bundle = get_app_bundle(app)
            out.append({
                'name': app,
                'role': 'application',
                'description': '',
                'value': '',
                'bbox': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'children': get_tree_with_display_info(bundle)
            })
        except:
           pass 
    
    return out

def main():
    parser = argparse.ArgumentParser(description='Extract accessibility tree from macOS applications')
    parser.add_argument('-o', '--out', help='Output file path (defaults to stdout)')
    parser.add_argument('-e', '--event', help='Output in event format with timing data', action='store_true')
    parser.add_argument('--recording-display', type=int, help='Display index being used for recording (0=primary)')
    parser.add_argument('--no-focus-steal', action='store_true', help='Use no-focus-steal mode to avoid disrupting user during recording')
    parser.add_argument('--low-frequency', action='store_true', help='Reduce polling frequency to 60s intervals for recording mode')
    args = parser.parse_args()
    
    # Add delay for low-frequency mode
    if args.low_frequency:
        print("Low-frequency mode: This capture is for recording context (60s intervals recommended)")
        # This is just a single capture, but signals the calling system to use 60s intervals

    start_time = int(time.time() * 1000)  # JS equivalent of timestamp_millis
    tree = get_accessibility_tree()
    end_time = int(time.time() * 1000)
    duration = end_time - start_time

    if args.event:
        output = {
            "time": start_time,
            "data": {
                "duration": duration,
                "tree": tree
            }
        }
    else:
        output = tree

    json_output = json.dumps(output)

    if args.out:
        with open(args.out, 'w') as f:
            f.write(json_output)
    else:
        print(json_output)

if __name__ == "__main__":
    main()
