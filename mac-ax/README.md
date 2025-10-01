# Mac-AX: MacOS Accessibility Tree Parser

The MacOS accessibility parser uses a modified version of [macapptree](https://github.com/MacPaw/macapptree) (found in the `macapptree` directory) to parse the tree.

## Setup

Install `macapptree` and dependencies using your preferred python environment:

```bash
cd macapptree
pip3 install -r requirements.txt
pip3 install -e .
```

## Usage

### Basic Usage
```bash
python3 dump-tree.py -o out.json
```

### Recording Mode (Optimized for demos)
```bash
# Pre-recording capture (full detail, before video starts)
python3 dump-tree.py -e --recording-display 0

# During recording (60s intervals, minimal disruption)
python3 dump-tree.py -e --recording-display 0 --low-frequency
```

### Options
- `--recording-display 0`: Specify primary display for recording context
- `--low-frequency`: Reduce polling frequency for non-intrusive recording
- `-e`: Output in event format with timing data

The tree will output in `out.json` with the following structure:

```json
[
    {
    "application": "Code",
    "tree": {
      "id": "11lfkmfi3930fjfkdnf39",
      "name": "run.py",
      "role": "AXWindow",
      "description": null,
      "role_description": "standard window",
      "value": null,
      "absolute_position": "0.00;44.00",
      "position": "0.00;0.00",
      "size": "1800;1125",
      "enabled": true,
      "bbox": [
        0,
        0,
        1800,
        1125
      ],
      "visible_bbox": [
        0,
        0,
        1800,
        1125
      ],
      "children": []
    },
  }
]
```
