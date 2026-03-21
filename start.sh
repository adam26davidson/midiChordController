#!/bin/bash

PI_HOST="adam26davidson@chord-controller.local"
PI_PATH="~/midiChordController"

echo "=== Starting app on Pi with auto-restart ==="
echo "Press Ctrl+C to stop"
echo ""

ssh "$PI_HOST" bash << 'REMOTE_SCRIPT'
cd ~/midiChordController
export DISPLAY=:0
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# Install inotify-tools if not present
if ! command -v inotifywait &> /dev/null; then
    echo "Installing inotify-tools..."
    sudo apt-get install -y inotify-tools
fi

cleanup() {
    echo ""
    echo "Stopping app..."
    kill $APP_PID 2>/dev/null
    wait $APP_PID 2>/dev/null
    exit 0
}
trap cleanup INT TERM

while true; do
    echo ""
    echo "=== Starting main.py ==="
    uv run --no-sync main.py 2>&1 &
    APP_PID=$!

    # Wait for any file changes in the project (quiet mode, output to stderr)
    inotifywait -r -q -e modify,create,delete \
        --exclude '(__pycache__|\.venv|\.git|\.pyc|event_trace\.log)' \
        ~/midiChordController > /dev/null 2>&1

    echo "[$(date +%H:%M:%S)] Files changed, restarting..."
    kill $APP_PID 2>/dev/null
    wait $APP_PID 2>/dev/null
    sleep 1
done
REMOTE_SCRIPT
