#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../pi_config.sh"

if [ ! -f "$CONFIG" ]; then
  echo "Error: $CONFIG not found. Create it with PI_USER, PI_HOST, and PI_SSH vars."
  exit 1
fi

source "$CONFIG"
source "$SCRIPT_DIR/../lock.sh"

# Self-daemonize unless --foreground is passed
if [ "$1" != "--foreground" ]; then
    check_lock "start"
    nohup "$0" --foreground > /tmp/pi_start.log 2>&1 &
    echo "start started (PID $!, log: /tmp/pi_start.log)"
    exit 0
fi

own_lock "start"

ssh "$PI_SSH" bash << 'REMOTE_SCRIPT'
cd ~/midiChordController
export DISPLAY=:0
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

RESTART_FLAG="/tmp/midichordcontroller_restart"

cleanup() {
    echo ""
    echo "Stopping app..."
    kill $APP_PID 2>/dev/null
    wait $APP_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

start_app() {
    # Clean up stale app lock before starting
    if [ -f /tmp/midichordcontroller.lock ]; then
        OLD_PID=$(cat /tmp/midichordcontroller.lock 2>/dev/null)
        if [ -n "$OLD_PID" ]; then
            kill "$OLD_PID" 2>/dev/null
            wait "$OLD_PID" 2>/dev/null
        fi
        rm -f /tmp/midichordcontroller.lock
    fi
    # Clear any pending restart flag
    rm -f "$RESTART_FLAG"

    echo ""
    echo "=== Starting main.py ==="
    uv run --no-sync main.py --remote-control 2>&1 &
    APP_PID=$!
}

# Initial start
start_app

# Poll for restart flag (set by sync.sh after pushing files)
while true; do
    sleep 1
    if [ -f "$RESTART_FLAG" ]; then
        echo "[$(date +%H:%M:%S)] Restart requested, restarting..."
        kill $APP_PID 2>/dev/null
        wait $APP_PID 2>/dev/null
        sleep 1
        start_app
    fi
done
REMOTE_SCRIPT
