#!/usr/bin/env bash
set -euo pipefail
DATE="${DATE:-$(date +%Y-%m-%d)}"
PLAN="${1:-archive_plan_${DATE}.csv}"
ARCHIVE_DIR="${2:-archive/${DATE}}"
DRY="${DRY_RUN:-0}"
test -f "$PLAN"
mkdir -p "$ARCHIVE_DIR"
has_git=0
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then has_git=1; fi
tail -n +2 "$PLAN" | while IFS=, read -r path size sha reasons; do
  dst="${ARCHIVE_DIR}/${path}"
  mkdir -p "$(dirname "$dst")"
  if [ "$DRY" = "1" ]; then
    echo "[DRY] mv -- '$path' '$dst'"
  else
    if [ "$has_git" = "1" ]; then
      git mv -f -- "$path" "$dst" || { mkdir -p "$(dirname "$dst")"; mv -f -- "$path" "$dst"; }
    else
      mv -f -- "$path" "$dst"
    fi
  fi
done
find . -type d -empty -not -path "./.git/*" -not -path "./.git" -not -path "." -exec rmdir -p --ignore-fail-on-non-empty {} + || true
echo "Archive complete → $ARCHIVE_DIR"