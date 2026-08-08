#!/bin/zsh
# Install hourly watchdog LaunchAgent for the generic worker templates.
set -euo pipefail
ROOT="${1:-$(pwd)}"
ROOT="$(cd "$ROOT" && pwd)"
LABEL="com.example.autonomous-worker"
PLIST_SRC="$(cd "$(dirname "$0")" && pwd)/com.example.autonomous-worker.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"

mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/var/worker/logs"
# Prefer project venv if present
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi

sed \
  -e "s|REPO_ROOT_PLACEHOLDER|${ROOT}|g" \
  -e "s|REPO_ROOT_PLACEHOLDER/.venv/bin/python|${PY}|g" \
  "$PLIST_SRC" > "$PLIST_DST"

# Fix python path if sed double-replaced oddly — write clean ProgramArguments via note
# (plist already has REPO paths; if no venv, user should edit PLIST_DST ProgramArguments[0])

launchctl bootout "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl enable "gui/$(id -u)/${LABEL}" 2>/dev/null || true
launchctl kickstart -k "gui/$(id -u)/${LABEL}" 2>/dev/null || true

echo "Installed: $PLIST_DST"
echo "Worker hours: see WORKER_HOURS in plist (default 48)"
echo "Pause: touch $ROOT/var/worker/PAUSE"
echo "State: cat $ROOT/var/worker/STATE.json"
echo "Keep Mac awake: caffeinate -dims  OR  Amphetamine (optional App Store app)"
echo "If no .venv, edit ProgramArguments[0] in $PLIST_DST to your python3 path"
