#!/usr/bin/env bash
# Real terminal footage for the rustbrain demo video.
# Xvfb + kitty + ffmpeg x11grab at 60 fps. The terminal runs real commands in
# the real repo; the visible prompt is clean (no username, no paths), the
# environment is stripped (no tokens), and each clip saves a transcript of what
# was on screen.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/out/video/raw/term"
TR="$ROOT/out/video/transcripts"
mkdir -p "$RAW" "$TR"
DISP=:97
PYDIR="$(dirname "$(command -v python3)")"

Xvfb $DISP -screen 0 1920x1080x24 >/dev/null 2>&1 &
XPID=$!
sleep 1

RC="$(mktemp)"
cat > "$RC" <<EOF
export PS1='rustbrain \$ '
export HISTFILE=/dev/null
export T="$TR"
cd "$ROOT"
clear
EOF

env -i HOME="$HOME" PATH="$PYDIR:/usr/local/bin:/usr/bin:/bin" \
  DISPLAY=$DISP TERM=xterm-256color LIBGL_ALWAYS_SOFTWARE=1 LANG=C.UTF-8 \
  kitty --config NONE -o font_size=20 -o window_padding_width=26 \
        -o remember_window_size=no -o initial_window_width=1820 -o initial_window_height=1000 \
        -o background=#14110e -o foreground=#f2ede4 -o cursor=#ff6a3d -o selection_background=#ff6a3d \
        -T rustbrain-term bash --rcfile "$RC" >/dev/null 2>&1 &
KPID=$!
sleep 3
WIN=$(DISPLAY=$DISP xdotool search --name rustbrain-term 2>/dev/null | head -1 || true)
if [ -z "$WIN" ]; then echo "FAIL: kitty window not found under Xvfb"; kill $XPID 2>/dev/null || true; exit 1; fi
echo "kitty pid=$KPID window=$WIN"

RECPID=""
rec() {
  ffmpeg -hide_banner -loglevel error -y -f x11grab -framerate 60 -video_size 1920x1080 \
    -i $DISP -c:v libx264 -preset veryfast -crf 16 -pix_fmt yuv420p "$RAW/$1.mp4" &
  RECPID=$!
  sleep 2
}
stop() { kill -INT "$RECPID" 2>/dev/null || true; wait "$RECPID" 2>/dev/null || true; }
typ() {
  DISPLAY=$DISP xdotool type --window "$WIN" --delay 45 --clearmodifiers -- "$1"
  DISPLAY=$DISP xdotool key --window "$WIN" Return
  sleep 1.2
}

rec naive
typ 'python3 cmd/route.py 1892 --naive | tee $T/naive.txt | sed "s|$HOME|~|g"'
sleep 4
stop

rec query
typ 'sed -n "1,14p" queries/routing.cypher'
sleep 3
typ 'python3 video/run_query.py | tee $T/query.txt | sed "s|$HOME|~|g"'
sleep 5
stop

rec refresh
typ 'python3 video/run_refresh.py | tee $T/refresh.txt | sed "s|$HOME|~|g"'
sleep 6
stop

rec assertions
typ 'python3 scripts/test_queries.py | tail -22 | tee $T/assertions.txt'
sleep 5
stop

kill "$KPID" 2>/dev/null || true
kill "$XPID" 2>/dev/null || true
rm -f "$RC"
echo "done: $(ls -1 "$RAW" | tr '\n' ' ')"
