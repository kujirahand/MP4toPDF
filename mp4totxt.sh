#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 video.mp4 [output.txt]" >&2
    exit 2
fi

exec uv run --with-requirements "$SCRIPT_DIR/requirements.txt" \
    "$SCRIPT_DIR/src/mp4totxt.py" "$@"
