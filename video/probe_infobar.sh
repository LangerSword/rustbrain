#!/usr/bin/env bash
# Probe: can the Chrome for Testing infobar be suppressed by flags? Captures
# one frame per flag set and reports the mean color of the top 20 pixel strip
# (dark page = suppressed; near-white = infobar still visible).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DISP=:94
Xvfb $DISP -screen 0 1280x800x24 >/dev/null 2>&1 &
XV=$!
sleep 1
probe() { # name extra-flags...
  local name="$1"; shift
  local prof="/tmp/chrome-probe-$name"
  rm -rf "$prof"
  env -i HOME="$HOME" DISPLAY=$DISP PATH=/usr/bin:/bin \
    /home/lakshaya/.local/bin/google-chrome-stable \
    --no-sandbox --disable-gpu --no-first-run --no-default-browser-check \
    --user-data-dir="$prof" --window-size=1280,800 --window-position=0,0 \
    --kiosk "$@" --app=http://rustbrain.langersword.in/ >/dev/null 2>&1 &
  local pid=$!
  sleep 6
  ffmpeg -hide_banner -loglevel error -y -f x11grab -framerate 1 -video_size 1280x800 -draw_mouse 0 \
    -i $DISP -frames:v 1 "/tmp/probe_$name.png"
  local rgb
  rgb=$(ffmpeg -hide_banner -loglevel error -i "/tmp/probe_$name.png" \
        -vf "crop=1280:20:0:0,scale=1:1" -f rawvideo -pix_fmt rgb24 - 2>/dev/null | od -An -tu1 | head -1)
  echo "$name top-strip rgb: $rgb"
  kill $pid 2>/dev/null || true
  sleep 1
}
probe baseline
probe infobars --disable-infobars
probe testtype --test-type --disable-infobars
probe features --disable-features=ChromeForTestingInfobar,InfobarChromeForTesting
kill $XV 2>/dev/null || true
echo done
