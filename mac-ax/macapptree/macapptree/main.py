import AppKit
import macapptree.apps as apps
from macapptree.window_tools import store_screen_scaling_factor
from macapptree.uielement import UIElement
from macapptree.extractor import extract_window
from macapptree.screenshot_app_window import screenshot_window_to_file
from macapptree.window_tools import segment_window_components
from macapptree.display_utils import get_display_info, get_window_display, log_display_mismatch
import argparse
import shutil
import json
import time
import os


def get_main_window(windows, max_depth):
    ui_windows = [UIElement(window, max_depth=max_depth) for window in windows]
    main_window = max([(window, len(window.recursive_children())) for window in ui_windows], key=lambda x: x[1])[0]
    return main_window


def main(app_bundle, output_accessibility_file, output_screenshot_file, max_depth, recording_display_index=None):
    # store the screen scaling factor
    store_screen_scaling_factor()

    # Log display information for debugging
    displays = get_display_info()
    print(f"Available displays: {len(displays)}")
    for display in displays:
        print(f"Display {display['index']}: {display['frame']} (primary: {display['is_primary']})")

    workspace = AppKit.NSWorkspace.sharedWorkspace()

    app = apps.application_for_bundle(app_bundle, workspace)
    
    if not app:
        return

    application = apps.application_for_process_id(app.processIdentifier())

    windows = apps.windows_for_application(application)
    window_element = get_main_window(windows, max_depth)

    # Determine which display the window is on
    window_display = get_window_display(window_element)
    window_display_index = 0  # Default to primary
    if window_display:
        for i, screen in enumerate(AppKit.NSScreen.screens()):
            if screen == window_display:
                window_display_index = i
                break
    
    print(f"Target window is on display {window_display_index}")
    
    # Check for display mismatch with recording system
    if recording_display_index is not None:
        log_display_mismatch(window_display_index, recording_display_index)

    # output_accessibility_file_hit = output_accessibility_file.replace(".tmp", "_hit.tmp")

    # Use multi-display extraction by default, with optional no-focus mode
    extracted = extract_window(
            window_element, app_bundle, output_accessibility_file, False, False, max_depth, use_multi_display=True, no_focus_steal=recording_display_index is not None
        )
    
    # extracted_hit = extract_window(
    #         window_element, app_bundle, output_accessibility_file_hit, True, False, max_depth
    #     )
    
    if not extracted:
        raise "Couldn't extract accessibility"
    
    # if extracted:
    #     if os.path.getsize(output_accessibility_file) < os.path.getsize(output_accessibility_file_hit):
    #         shutil.move(output_accessibility_file_hit, output_accessibility_file)
    #     else:
    #         os.remove(output_accessibility_file_hit)
    # elif extracted_hit:
    #     shutil.move(output_accessibility_file_hit, output_accessibility_file)
    
    if output_screenshot_file:
        output_croped, _ = screenshot_window_to_file(app.localizedName(), window_element.name, output_screenshot_file)
        output_segmented = segment_window_components(window_element, output_croped)

        print(json.dumps({
            "croped_screenshot_path": output_croped,
            "segmented_screenshot_path": output_segmented
        }))
        

# main function
if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-a", type=str, required=True, help="The application bundle identifier")
    arg_parser.add_argument("--oa", type=str, required=True, help="Accessibility output file")
    arg_parser.add_argument("--os", type=str, default=None, required=False, help="Screenshot output file")
    arg_parser.add_argument("--max-depth", type=int, required=False, help="Maximum depth of the accessibility")
    arg_parser.add_argument("--recording-display", type=int, required=False, help="Display index being used for recording (0=primary)")

    args = arg_parser.parse_args()
    app_bundle = args.a
    output_accessibility_file = args.oa
    output_screenshot_file = args.os
    max_depth = args.max_depth
    recording_display_index = args.recording_display

    # start processing all the running applications or the specified application
    main(app_bundle, output_accessibility_file, output_screenshot_file, max_depth, recording_display_index)
