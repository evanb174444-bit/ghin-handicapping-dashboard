#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-8000}"
cd "$(dirname "$0")/.."
echo "Serving dashboard at http://127.0.0.1:${PORT}/"
echo "Press Ctrl+C to stop."
exec python3 -m http.server "$PORT" --bind 127.0.0.1
