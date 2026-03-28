#!/bin/bash
# Send a remote control event to the Pi's running app.
# Usage: ./tools/test/pi_send_event.sh press SOUTH_BUTTON
#        ./tools/test/pi_send_event.sh analog GYRO_PITCH 0.5

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../pi_config.sh"

if [ ! -f "$CONFIG" ]; then
  echo "Error: $CONFIG not found. Create it with PI_USER, PI_HOST, and PI_SSH vars."
  exit 1
fi

source "$CONFIG"

python3 "$SCRIPT_DIR/send_event.py" --host "$PI_HOST" "$@"
