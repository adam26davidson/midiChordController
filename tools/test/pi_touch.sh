#!/bin/bash
# Simulate a touch gesture on the Pi's display and return an annotated screenshot.
# Usage:
#   ./tools/test/pi_touch.sh --tap X,Y                    # Single tap
#   ./tools/test/pi_touch.sh --from X1,Y1 --to X2,Y2      # Drag gesture
#   --steps N:    Number of interpolation steps for drag (default: 10)
#   --duration MS: Total drag duration in ms (default: 200)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../pi_config.sh"

if [ ! -f "$CONFIG" ]; then
  echo "Error: $CONFIG not found. Create it with PI_USER, PI_HOST, and PI_SSH vars."
  exit 1
fi

source "$CONFIG"

# Parse arguments
TAP=""
FROM=""
TO=""
STEPS=10
DURATION=200

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tap)      TAP="$2"; shift 2 ;;
        --from)     FROM="$2"; shift 2 ;;
        --to)       TO="$2"; shift 2 ;;
        --steps)    STEPS="$2"; shift 2 ;;
        --duration) DURATION="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate args
if [ -n "$TAP" ]; then
    FROM_X="${TAP%%,*}"
    FROM_Y="${TAP##*,}"
    TO_X="$FROM_X"
    TO_Y="$FROM_Y"
    IS_TAP=1
elif [ -n "$FROM" ] && [ -n "$TO" ]; then
    FROM_X="${FROM%%,*}"
    FROM_Y="${FROM##*,}"
    TO_X="${TO%%,*}"
    TO_Y="${TO##*,}"
    IS_TAP=0
else
    echo "Usage:"
    echo "  pi_touch.sh --tap X,Y"
    echo "  pi_touch.sh --from X1,Y1 --to X2,Y2"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="/tmp/pi_touch_${TIMESTAMP}.png"

# Execute the touch gesture on the Pi using absolute screen coordinates
ssh "$PI_SSH" bash << REMOTE_SCRIPT
export DISPLAY=:0

STEP_DELAY=\$(echo "scale=4; $DURATION / 1000 / $STEPS" | bc)

xdotool mousemove $FROM_X $FROM_Y
xdotool mousedown 1

if [ "$IS_TAP" = "0" ]; then
    for i in \$(seq 1 $STEPS); do
        X=\$(echo "$FROM_X + ($TO_X - $FROM_X) * \$i / $STEPS" | bc)
        Y=\$(echo "$FROM_Y + ($TO_Y - $FROM_Y) * \$i / $STEPS" | bc)
        xdotool mousemove \$X \$Y
        sleep \$STEP_DELAY
    done
fi

sleep 0.05
xdotool mouseup 1
echo "ok"
REMOTE_SCRIPT

# Take screenshot after gesture
sleep 0.2
SCREENSHOT="/tmp/pi_touch_raw_${TIMESTAMP}.png"
"$SCRIPT_DIR/pi_screenshot.sh" "$SCREENSHOT" > /dev/null 2>&1

# Overlay gesture annotation
python3 "$SCRIPT_DIR/annotate_touch.py" "$SCREENSHOT" "$OUTPUT" "$FROM_X" "$FROM_Y" "$TO_X" "$TO_Y"

echo "Touch result saved to $OUTPUT"
