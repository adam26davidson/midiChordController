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
    check_lock "sync"
    nohup "$0" --foreground > /tmp/pi_sync.log 2>&1 &
    echo "sync started (PID $!, log: /tmp/pi_sync.log)"
    exit 0
fi

own_lock "sync"
PI_PATH="~/midiChordController"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

EXCLUDES=(
    --exclude='.git/'
    --exclude='.venv/'
    --exclude='__pycache__/'
    --exclude='.DS_Store'
    --exclude='*.pyc'
    --exclude='.python-version'
    --exclude='uv.lock'
)

RESTART_FLAG="/tmp/midichordcontroller_restart"

sync_to_pi() {
    rsync -avz --delete "${EXCLUDES[@]}" "$PROJECT_DIR/" "$PI_SSH:$PI_PATH/"
    # Signal start.sh to restart the app
    ssh "$PI_SSH" "touch $RESTART_FLAG" 2>/dev/null
}

echo "=== Initial sync ==="
sync_to_pi

echo ""
echo "=== Watching for changes (Ctrl+C to stop) ==="
fswatch -o -r "$PROJECT_DIR" \
    --exclude='\.git/' \
    --exclude='\.venv/' \
    --exclude='__pycache__' \
    --exclude='\.DS_Store' \
    | while read -r _; do
        echo "[$(date +%H:%M:%S)] Change detected, syncing..."
        sync_to_pi
    done
