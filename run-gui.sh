#!/usr/bin/env bash
set -e
cd "$(dirname "$(readlink -f "$0")")" || exit 1
exec python3 poster-gui.py "$@"
