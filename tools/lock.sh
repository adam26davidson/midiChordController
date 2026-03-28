#!/bin/bash
# Shared lock file helper. Source this, then call check_lock or own_lock.
# Prevents multiple instances of the same script from running.

# Check if a lock is held. If so, exit. If stale, clean up.
check_lock() {
    local name="$1"
    local lock_file="/tmp/pi_${name}.lock"

    if [ -f "$lock_file" ]; then
        local existing_pid
        existing_pid=$(cat "$lock_file" 2>/dev/null)
        if [ -n "$existing_pid" ] && kill -0 "$existing_pid" 2>/dev/null; then
            echo "Error: ${name}.sh is already running (PID $existing_pid)."
            echo "Kill it first or run: rm $lock_file"
            exit 1
        fi
        rm -f "$lock_file"
    fi
}

# Write the lock with current PID and set cleanup trap.
# Call this from the foreground (long-running) process.
own_lock() {
    local name="$1"
    local lock_file="/tmp/pi_${name}.lock"
    echo $$ > "$lock_file"
    trap "rm -f '$lock_file'" EXIT INT TERM
}
