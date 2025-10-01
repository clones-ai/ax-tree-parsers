from macapptree.uielement import UIElement
import AppKit
import ApplicationServices
import macapptree.uielement as uielement
import macapptree.files as files
import macapptree.window_tools as window_tools


# perform a hit test on the specified point across all displays
def hit_test_multi_display(point, window_element):
    """Try hit testing across all available displays"""
    for screen in AppKit.NSScreen.screens():
        screen_frame = screen.frame()
        if AppKit.NSPointInRect(point, screen_frame):
            window_point = window_tools.convert_point_to_window(point, window_element.position)
            system_component = ApplicationServices.AXUIElementCreateSystemWide()
            err, value = ApplicationServices.AXUIElementCopyElementAtPosition(
                system_component, window_point.x, window_point.y, None
            )
            if err == ApplicationServices.kAXErrorSuccess:
                return value
    return None

# perform a hit test on the specified point (legacy single display)
def hit_test(point, window_element):
    window_point = window_tools.convert_point_to_window(point, window_element.position)
    system_component = ApplicationServices.AXUIElementCreateSystemWide()
    err, value = ApplicationServices.AXUIElementCopyElementAtPosition(
        system_component, window_point.x, window_point.y, None
    )
    if err == ApplicationServices.kAXErrorSuccess:
        return value
    return None


def extract_without_hit_test(window, app_bundle, output_file, print_nodes, max_depth):
    """Extract accessibility tree without hit testing to avoid focus stealing"""
    window_offset_x = window.position.x
    window_offset_y = window.position.y

    # Directly use the window element without hit testing
    # This avoids focus stealing but may have slightly less detail
    found_root_element = window.element  # Use the window element directly
    root_element = UIElement(found_root_element, window_offset_x, window_offset_y, max_depth)
    
    # Get children directly from window attributes
    window.children.append(root_element)
    window.calculate_hashes()

    # print the node with its children and attributes
    if print_nodes:
        uielement.print_node(root_element)

    files.store_data_to_file(window, output_file)

    return True

def extract_with_hit_test_multi_display(window, app_bundle, output_file, print_nodes, max_depth):
    """Extract with hit test across multiple displays"""
    window_offset_x = window.position.x
    window_offset_y = window.position.y

    # Try multiple points within the window to increase success rate
    test_points = [
        AppKit.NSMakePoint(window_offset_x + 50, window_offset_y + 50),
        AppKit.NSMakePoint(window_offset_x + window.size.width // 2, window_offset_y + window.size.height // 2),
        AppKit.NSMakePoint(window_offset_x + 10, window_offset_y + 10),
        AppKit.NSMakePoint(window_offset_x + window.size.width - 10, window_offset_y + window.size.height - 10)
    ]
    
    group_element = None
    for point in test_points:
        group_element = hit_test_multi_display(point, window)
        if group_element is not None:
            break

    if group_element is None:
        return False

    # find the root window
    found_root_element = UIElement.find_root_element(group_element)
    root_element = UIElement(found_root_element, window_offset_x, window_offset_y, max_depth)
    parent_window = uielement.element_attribute(
        found_root_element, ApplicationServices.kAXWindowAttribute
    )
    if parent_window is not None:
        parent_window_element = UIElement(
            parent_window, window_offset_x, window_offset_y, max_depth
        )

        if window_tools.windows_are_equal(window, parent_window_element):
            element_not_found = True
            for child in window.children:
                if (
                    child.identifier == root_element.identifier
                    and child.content_identifier == root_element.content_identifier
                ):
                    element_not_found = False
            if element_not_found:
                window.children.append(root_element)
                window.calculate_hashes()
    else:
        window.children.append(root_element)
        window.calculate_hashes()

    # print the node with its children and attributes
    if print_nodes:
        uielement.print_node(root_element)

    files.store_data_to_file(window, output_file)

    return True

def extract_with_hit_test(window, app_bundle, output_file, print_nodes, max_depth):
    window_offset_x = window.position.x
    window_offset_y = window.position.y

    point = AppKit.NSMakePoint(window_offset_x + 50, window_offset_y + 50)
    group_element = hit_test(point, window)

    if group_element is None:
        return False

    # find the root window
    found_root_element = UIElement.find_root_element(group_element)
    root_element = UIElement(found_root_element, window_offset_x, window_offset_y, max_depth)
    parent_window = uielement.element_attribute(
        found_root_element, ApplicationServices.kAXWindowAttribute
    )
    if parent_window is not None:
        parent_window_element = UIElement(
            parent_window, window_offset_x, window_offset_y, max_depth
        )

        if window_tools.windows_are_equal(window, parent_window_element):
            element_not_found = True
            for child in window.children:
                if (
                    child.identifier == root_element.identifier
                    and child.content_identifier == root_element.content_identifier
                ):
                    element_not_found = False
            if element_not_found:
                window.children.append(root_element)
                window.calculate_hashes()
    else:
        window.children.append(root_element)
        window.calculate_hashes()

    # print the node with its children and attributes
    if print_nodes:
        uielement.print_node(root_element)

    files.store_data_to_file(window, output_file)

    return True



# extract the window with multi-display support and no-focus mode
def extract_window(
    window, app_bundle, output_file, perform_hit_test, print_nodes, max_depth, use_multi_display=True, no_focus_steal=False
) -> bool:
    if window is None:
        return False

    # New: No focus steal mode for recording
    if no_focus_steal:
        print("Using no-focus-steal mode for recording")
        return extract_without_hit_test(window, app_bundle, output_file, print_nodes, max_depth)

    if perform_hit_test:
        if use_multi_display:
            # Try multi-display method first
            success = extract_with_hit_test_multi_display(window, app_bundle, output_file, print_nodes, max_depth)
            if not success:
                # Fallback to legacy single-display method
                print("Multi-display hit test failed, falling back to legacy method")
                success = extract_with_hit_test(window, app_bundle, output_file, print_nodes, max_depth)
            return success
        else:
            return extract_with_hit_test(window, app_bundle, output_file, print_nodes, max_depth)

    else:
        files.store_data_to_file(window, output_file)

        return True


