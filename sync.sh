#!/bin/bash

PI_HOST="adam26davidson@chord-controller.local"
PI_PATH="~/midiChordController"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

EXCLUDES=(
    --exclude='.git/'
    --exclude='.venv/'
    --exclude='__pycache__/'
    --exclude='.DS_Store'
    --exclude='*.pyc'
    --exclude='.python-version'
    --exclude='uv.lock'
)

sync_to_pi() {
    rsync -avz --delete "${EXCLUDES[@]}" "$PROJECT_DIR/" "$PI_HOST:$PI_PATH/"
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
