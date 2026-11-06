#!/usr/bin/env bash
# autopush.sh — auto-commit and push this repo to GitHub once every minute.
#
# Usage:
#   ./autopush.sh                          # every 60 seconds (default)
#   AUTOPUSH_INTERVAL=10 ./autopush.sh     # every 10 seconds
#
# Runs forever until you stop it with Ctrl+C.
# Commits respect .gitignore, so venv/ and caches are never pushed.

set -u

cd "$(dirname "$0")" || exit 1

INTERVAL="${AUTOPUSH_INTERVAL:-60}"

stop() {
    echo
    echo "[$(date '+%H:%M:%S')] Stopped."
    exit 0
}
trap stop INT TERM

while true; do
    ts="$(date '+%Y-%m-%d %H:%M:%S')"

    # Commit any new or modified files (respects .gitignore).
    if [ -n "$(git status --porcelain)" ]; then
        git add -A
        if out="$(git commit -m "Auto-commit: $ts" 2>&1)"; then
            case "$out" in
                *"nothing to commit"*) : ;;
                *) echo "[$ts] Committed changes." ;;
            esac
        else
            echo "[$ts] Commit failed: $out" >&2
        fi
    fi

    # Push every cycle so a previously failed push gets retried.
    if out="$(git push origin HEAD 2>&1)"; then
        case "$out" in
            *"Everything up-to-date"*) echo "[$ts] Nothing to push." ;;
            *) echo "[$ts] Pushed to GitHub." ;;
        esac
    else
        echo "[$ts] Push failed (retrying next cycle): $out" >&2
    fi

    sleep "$INTERVAL"
done
