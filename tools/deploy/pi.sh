#!/bin/bash
# Unified Pi management script.
# Usage: ./tools/deploy/pi.sh <command> [--autosync]
#
# Commands:
#   up        Sync code and start app (one-shot by default)
#   down      Stop everything (app + any running daemons)
#   restart   Stop app, re-sync, start app (one-shot by default)
#   status    Show app status on Pi (+ daemon info if running)
#   logs      View logs: logs [app|start|sync] [lines]
#   ping      Check if Pi is reachable via SSH
#
# Flags:
#   --autosync  With 'up' or 'restart': start sync daemon + start daemon
#               for continuous file watching and auto-restart (interactive dev mode)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/../pi_config.sh"

if [ ! -f "$CONFIG" ]; then
    echo "Error: $CONFIG not found. Create it with PI_USER, PI_HOST, and PI_SSH vars."
    exit 1
fi

source "$CONFIG"
source "$SCRIPT_DIR/../lock.sh"

APP_LOCK_FILE="/tmp/midichordcontroller.lock"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_is_local_running() {
    local name="$1"
    local lock_file="/tmp/pi_${name}.lock"
    if [ -f "$lock_file" ]; then
        local pid
        pid=$(cat "$lock_file" 2>/dev/null)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "$pid"
            return 0
        fi
        rm -f "$lock_file"
    fi
    return 1
}

_stop_local() {
    local name="$1"
    local pid
    if pid=$(_is_local_running "$name"); then
        kill "$pid" 2>/dev/null
        wait "$pid" 2>/dev/null
        rm -f "/tmp/pi_${name}.lock"
        echo "$name: stopped (was PID $pid)"
    else
        echo "$name: was not running"
    fi
}

_start_sync() {
    if _is_local_running "sync" > /dev/null; then
        echo "sync: already running"
        return 0
    fi
    "$SCRIPT_DIR/sync.sh"
}

_start_app() {
    if _is_local_running "start" > /dev/null; then
        echo "start: already running"
        return 0
    fi
    "$SCRIPT_DIR/start.sh"
}

_stop_app_on_pi() {
    local result
    result=$(ssh -o ConnectTimeout=5 "$PI_SSH" bash << 'STOP_SCRIPT'
        # Kill the app
        if [ -f /tmp/midichordcontroller.lock ] && kill -0 $(cat /tmp/midichordcontroller.lock) 2>/dev/null; then
            PID=$(cat /tmp/midichordcontroller.lock)
            kill "$PID" 2>/dev/null
            rm -f /tmp/midichordcontroller.lock
            echo "app: stopped on Pi (was PID $PID)"
        else
            rm -f /tmp/midichordcontroller.lock
            echo "app: was not running on Pi"
        fi
        # Kill orphaned start.sh bash sessions and inotifywait
        killall inotifywait 2>/dev/null
        rm -f /tmp/midichordcontroller_restart
        # Kill orphaned remote bash sessions (those without a terminal)
        for pid in $(ps -eo pid,tty,comm --no-headers | awk '$2 == "?" && $3 == "bash" {print $1}'); do
            kill "$pid" 2>/dev/null
        done
STOP_SCRIPT
    ) 2>/dev/null
    echo "$result"
}

_app_status_on_pi() {
    local app_pid
    app_pid=$(ssh -o ConnectTimeout=5 "$PI_SSH" \
        "if [ -f $APP_LOCK_FILE ] && kill -0 \$(cat $APP_LOCK_FILE) 2>/dev/null; then cat $APP_LOCK_FILE; fi" 2>/dev/null)
    if [ -n "$app_pid" ]; then
        echo "app: running on Pi (PID $app_pid)"
        return 0
    else
        echo "app: not running on Pi"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# One-shot helpers (no daemons)
# ---------------------------------------------------------------------------

_oneshot_sync() {
    local project_dir
    project_dir="$(cd "$SCRIPT_DIR/../.." && pwd)"
    echo "Syncing to Pi..."
    rsync -avz --delete \
        --exclude='.git/' \
        --exclude='.venv/' \
        --exclude='__pycache__/' \
        --exclude='.DS_Store' \
        --exclude='*.pyc' \
        --exclude='.python-version' \
        --exclude='uv.lock' \
        "$project_dir/" "$PI_SSH:~/midiChordController/"
    echo "Sync complete."
}

_oneshot_start_app() {
    echo "Starting app on Pi..."
    ssh -o ConnectTimeout=5 "$PI_SSH" bash <<'REMOTE'
cd ~/midiChordController
export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

# Kill existing app if running
if [ -f /tmp/midichordcontroller.lock ]; then
    OLD_PID=$(cat /tmp/midichordcontroller.lock 2>/dev/null)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        kill "$OLD_PID" 2>/dev/null
        sleep 1
    fi
    rm -f /tmp/midichordcontroller.lock
fi

nohup uv run --no-sync main.py --remote-control > /tmp/midichordcontroller_app.log 2>&1 &
sleep 2

if [ -f /tmp/midichordcontroller.lock ]; then
    echo "app: started on Pi (PID $(cat /tmp/midichordcontroller.lock))"
else
    echo "app: WARNING - started but lock file not found after 2s"
fi
REMOTE
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

cmd_up() {
    if [ "$AUTOSYNC" = "1" ]; then
        _start_sync

        # Wait for initial sync to complete before starting app
        if ! _is_local_running "start" > /dev/null; then
            echo "Waiting for initial sync..."
            sleep 5
        fi

        _start_app
    else
        _oneshot_sync
        _oneshot_start_app
    fi
}

cmd_down() {
    _stop_app_on_pi
    _stop_local "start"
    _stop_local "sync"
}

cmd_restart() {
    if [ "$AUTOSYNC" = "1" ]; then
        # Stop app and start script
        _stop_app_on_pi
        _stop_local "start"

        # Force a sync before restarting
        if _is_local_running "sync" > /dev/null; then
            echo "Triggering sync..."
            sleep 3
        else
            _start_sync
            echo "Waiting for sync..."
            sleep 5
        fi

        _start_app
    else
        _stop_app_on_pi
        _oneshot_sync
        _oneshot_start_app
    fi
}

cmd_status() {
    local sync_pid start_pid
    if sync_pid=$(_is_local_running "sync"); then
        echo "sync: running (PID $sync_pid, log: /tmp/pi_sync.log)"
    fi

    if start_pid=$(_is_local_running "start"); then
        echo "start: running (PID $start_pid, log: /tmp/pi_start.log)"
    fi

    _app_status_on_pi
}

cmd_logs() {
    local source="${1:-app}"
    local lines="${2:-50}"

    case "$source" in
        app)
            echo "=== App log (Pi: /tmp/midichordcontroller_app.log) ==="
            ssh -o ConnectTimeout=5 "$PI_SSH" "tail -n $lines /tmp/midichordcontroller_app.log 2>/dev/null || echo 'No app log found on Pi.'"
            ;;
        start)
            if [ -f /tmp/pi_start.log ]; then
                tail -n "$lines" /tmp/pi_start.log
            else
                echo "No start log found."
            fi
            ;;
        sync)
            if [ -f /tmp/pi_sync.log ]; then
                tail -n "$lines" /tmp/pi_sync.log
            else
                echo "No sync log found."
            fi
            ;;
        *)
            echo "Usage: pi.sh logs [app|start|sync] [lines]"
            exit 1
            ;;
    esac
}

cmd_ping() {
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$PI_SSH" "echo ok" > /dev/null 2>&1; then
        echo "Pi is reachable ($PI_HOST)"
    else
        echo "Cannot reach Pi ($PI_HOST)"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

COMMAND="${1:-}"
shift 2>/dev/null || true

AUTOSYNC=0
for arg in "$@"; do
    case "$arg" in
        --autosync) AUTOSYNC=1 ;;
    esac
done

case "$COMMAND" in
    up)      cmd_up ;;
    down)    cmd_down ;;
    restart) cmd_restart ;;
    status)  cmd_status ;;
    logs)    cmd_logs "$@" ;;
    ping)    cmd_ping ;;
    *)
        echo "Usage: pi.sh <command> [--autosync]"
        echo ""
        echo "Commands:"
        echo "  up        Sync code and start app (one-shot)"
        echo "  down      Stop app + any running daemons"
        echo "  restart   Stop app, re-sync, start app (one-shot)"
        echo "  status    Show app status on Pi"
        echo "  logs      View logs: logs [app|start|sync] [lines]"
        echo "  ping      Check if Pi is reachable"
        echo ""
        echo "Flags:"
        echo "  --autosync  With 'up' or 'restart': enable continuous sync + auto-restart"
        exit 1
        ;;
esac
