#!/bin/bash
# Capture a sequence of screenshots from the Pi's display.
# Usage: ./tools/test/pi_record.sh [--frames N] [--interval MS] [--output DIR] [--grid [COLS]]
#   --frames:   Number of frames to capture (default: 10)
#   --interval: Minimum ms between frames (default: 100, 0 = as fast as possible)
#   --output:   Local output directory (default: /tmp/pi_recording_<timestamp>)
#   --no-grid:  Output individual frame files instead of a stitched grid
#   --cols:     Number of grid columns (default: auto)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../pi_config.sh"

if [ ! -f "$CONFIG" ]; then
  echo "Error: $CONFIG not found. Create it with PI_USER, PI_HOST, and PI_SSH vars."
  exit 1
fi

source "$CONFIG"

# Parse arguments
FRAMES=10
INTERVAL=100
OUTPUT=""
GRID=1
GRID_COLS=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --frames)  FRAMES="$2"; shift 2 ;;
        --interval) INTERVAL="$2"; shift 2 ;;
        --output)  OUTPUT="$2"; shift 2 ;;
        --no-grid) GRID=""; shift ;;
        --cols)    GRID_COLS="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
if [ -z "$OUTPUT" ]; then
    OUTPUT="/tmp/pi_recording_${TIMESTAMP}"
fi
REMOTE_DIR="/tmp/pi_recording_${TIMESTAMP}"

echo "Capturing $FRAMES frames (interval: ${INTERVAL}ms)..."

# Capture all frames on Pi in a single SSH session
ssh "$PI_SSH" bash << REMOTE_SCRIPT
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
mkdir -p $REMOTE_DIR

INTERVAL_S=\$(echo "scale=3; $INTERVAL / 1000" | bc)
START=\$(date +%s%N)

for i in \$(seq -w 1 $FRAMES); do
    grim "$REMOTE_DIR/frame_\${i}.png"
    if [ "$INTERVAL" -gt 0 ] && [ "\$i" -lt "$FRAMES" ]; then
        sleep \$INTERVAL_S
    fi
done

END=\$(date +%s%N)
ELAPSED=\$(( (END - START) / 1000000 ))
echo "Captured $FRAMES frames in \${ELAPSED}ms"
REMOTE_SCRIPT

# Download all frames
mkdir -p "$OUTPUT"
scp -q "$PI_SSH:$REMOTE_DIR/frame_*.png" "$OUTPUT/" 2>/dev/null

# Clean up on Pi
ssh "$PI_SSH" "rm -rf $REMOTE_DIR" 2>/dev/null

FRAME_COUNT=$(ls "$OUTPUT"/frame_*.png 2>/dev/null | wc -l | tr -d ' ')
echo "Saved $FRAME_COUNT frames to $OUTPUT"

# Stitch grid if requested
if [ -n "$GRID" ] && [ "$FRAME_COUNT" -gt 0 ]; then
    GRID_ARGS=("$OUTPUT")
    if [ "$GRID_COLS" -gt 0 ]; then
        GRID_ARGS+=(--cols "$GRID_COLS")
    fi
    python3 "$SCRIPT_DIR/stitch_grid.py" "${GRID_ARGS[@]}"
fi
