#!/usr/bin/env bash
# Starts Django dev server and the background task worker together.

set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python="$repo/.rag~/bin/python"
manage="$repo/manage.py"

if [[ ! -f "$python" ]]; then
    python="$repo/.rag~/Scripts/python.exe"
fi

echo "Starting RAG Knowledge Assistant development environment..."

"$python" "$manage" db_worker &
worker_pid=$!
sleep 2
"$python" "$manage" runserver 0.0.0.0:8000 --noreload &
server_pid=$!

echo "Backend services started. Worker PID: $worker_pid, Server PID: $server_pid"
echo "Press Ctrl+C to stop."

cleanup() {
    echo "Stopping services..."
    kill "$worker_pid" "$server_pid" 2>/dev/null || true
    exit 0
}
trap cleanup INT TERM

wait
