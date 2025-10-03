# Mac-AX: MacOS Accessibility Tree Parser

The MacOS accessibility parser uses the original [macapptree](https://github.com/MacPaw/macapptree) package with custom extensions for passive extraction without focus stealing.

## Features

- **Focus-steal Prevention**: Passive accessibility tree extraction that doesn't interrupt user workflow
- **Multi-screen Support**: Detects applications across all displays
- **Permission Flexible**: Works without accessibility permissions using CGWindowList fallback
- **Event-driven Architecture**: Captures UI state on significant user interactions
- **Layout Aware**: Compatible with all keyboard layouts (QWERTY, AZERTY, QWERTZ, etc.)

## Setup

Install dependencies using your preferred python environment:

```bash
pip3 install -r requirements.txt
```

This will automatically install the official `macapptree` package and all its dependencies.

## Usage

### Basic Usage
```bash
# Standard accessibility tree extraction
python3 dump-tree.py -o out.json

# Use passive extraction (no focus stealing)
python3 dump-tree.py --no-focus-steal -o out.json
```

### Recording Mode (Optimized for screen recording)
```bash
# Pre-recording capture (full detail, before video starts)
python3 dump-tree.py -e --recording-display 0 --no-focus-steal

# During recording (event-driven, minimal disruption)
python3 dump-tree.py -e --recording-display 0 --no-focus-steal --low-frequency
```

### Binary Usage
```bash
# Use the compiled binary (faster startup)
./target/macos-arm64/dump-tree --no-focus-steal
```

### Options
- `--no-focus-steal`: Use passive extraction without interrupting user workflow
- `--display-index 0`: Only capture applications on specified display (0=primary, 1=secondary, etc.)
- `--recording-display 0`: Legacy alias for --display-index (for backward compatibility)
- `--low-frequency`: Signal for 60s interval usage in recording mode
- `-e`: Output in event format with timing data
- `-o FILE`: Write output to file instead of stdout

### Single Display Filtering

By default, the parser captures all applications across all displays. For screen recording, you typically only want applications on the display being recorded:

```bash
# Capture only applications on primary display (display 0)
python3 dump-tree.py --display-index 0

# Capture only applications on secondary display (display 1)  
python3 dump-tree.py --display-index 1

# Capture all displays (default behavior)
python3 dump-tree.py
```

This filtering significantly reduces the output size and eliminates irrelevant applications from non-recorded displays.

## Output Format

The parser outputs applications and their windows with display information:

```json
[
  {
    "name": "Microsoft Word",
    "role": "application", 
    "description": "Spans 1 display(s)",
    "value": "",
    "bbox": {"x": 0, "y": 0, "width": 0, "height": 0},
    "children": [
      {
        "name": "Window on display 0",
        "role": "window",
        "description": "Display 0", 
        "value": "",
        "bbox": {"x": 0.0, "y": 25.0, "width": 1440.0, "height": 790.0},
        "display_index": 0,
        "children": []
      }
    ]
  }
]
```

## Architecture

### Core Components

- **`dump-tree.py`**: Main script with event format and recording options
- **`custom_extractors.py`**: Passive extraction functions that extend macapptree
- **`macapptree`**: Original pip-installed package for accessibility tree parsing  
- **Binary**: Compiled version for faster execution in production

The architecture uses the official macapptree package with minimal custom extensions, avoiding code duplication.

### Focus Prevention

The `--no-focus-steal` mode uses:
- CGWindowList for application discovery (no permissions required)
- Passive AX tree traversal without hit-testing
- Event-driven dumps triggered by significant user interactions

### Multi-screen Support

Automatically detects and indexes all connected displays:
- Primary display: index 0
- Secondary displays: index 1, 2, etc.
- Window positioning calculated relative to display bounds

## Building

```bash
# Install PyInstaller
pip install pyinstaller

# Build binary
pyinstaller --onefile dump-tree.py

# Binary will be in ./dist/dump-tree
```

## Integration

The parser integrates with clones-desktop for screen recording:
- Event-driven accessibility dumps during recording
- Pre/post recording snapshots for context
- Keyboard layout aware interaction detection
