#!/usr/bin/env bash
set -e
py=python3; command -v python >/dev/null 2>&1 && py=python
LOGDIR=.logs; mkdir -p "$LOGDIR"
LOG="$LOGDIR/backend.log"
PIDFILE=.run_backend.pid
rotate() { [ -f "$LOG" ] && mv "$LOG" "$LOG.$(date +%s)" || true; }
start() {
  if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then echo "already running"; exit 0; fi
  rotate
  $py heystive_professional/backend_min.py >> "$LOG" 2>&1 &
  echo $! > "$PIDFILE"
  echo "started"
}
stop() {
  if [ -f "$PIDFILE" ]; then
    kill $(cat "$PIDFILE") 2>/dev/null || true
    rm -f "$PIDFILE"
    echo "stopped"
  else echo "not running"; fi
}
status() {
  if [ -f "$PIDFILE" ] && kill -0 $(cat "$PIDFILE") 2>/dev/null; then echo "running"; else echo "stopped"; fi
}
restart() { stop || true; sleep 1; start; }
case "$1" in start|stop|restart|status) "$1";; *) echo "usage: $0 {start|stop|restart|status}"; exit 1;; esac