#!/bin/bash
# Take a screenshot of the Pi's display and copy it locally
# Usage: ./tools/test/pi_screenshot.sh [output_path]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../pi_config.sh"

if [ ! -f "$CONFIG" ]; then
  echo "Error: $CONFIG not found. Create it with PI_USER, PI_HOST, and PI_SSH vars."
  exit 1
fi

source "$CONFIG"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="${1:-/tmp/pi_screenshot_${TIMESTAMP}.png}"

ssh "$PI_SSH" "XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-0 grim /tmp/wayland_screenshot.png" \
  && scp "$PI_SSH:/tmp/wayland_screenshot.png" "$OUTPUT" \
  && echo "Screenshot saved to $OUTPUT ($(date '+%H:%M:%S'))"
