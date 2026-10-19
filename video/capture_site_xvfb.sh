#!/usr/bin/env bash
# Browser footage, headed route: headed Chromium under Xvfb plus ffmpeg x11grab
# at 60 fps. Used because the CDP screencast route measured 0.78 to 12.17 fps,
# far under the 50 fps gate in the brief.
# Usage: video/capture_site_xvfb.sh [fhd|uhd]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:-fhd}"
case "$MODE" in
  fhd) DISP=:96; W=1920; H=1080; CHROME_PORT=9222;;
  uhd) DISP=:95; W=3840; H=2160; CHROME_PORT=9223;;
  *) echo "usage: $0 [fhd|uhd]"; exit 2;;
esac
RAW="$ROOT/out/video/raw/site_${MODE}_xvfb"
mkdir -p "$RAW"
PROFILE="/tmp/chrome-vid-${MODE}-$$"

Xvfb "$DISP" -screen 0 "${W}x${H}x24" >/dev/null 2>&1 &
XV=$!
sleep 1

env -i HOME="$HOME" DISPLAY="$DISP" PATH=/usr/bin:/bin \
  /home/lakshaya/.local/bin/google-chrome-stable \
  --no-sandbox --disable-gpu --disable-dev-shm-usage --hide-scrollbars \
  --user-data-dir="$PROFILE" --no-first-run --no-default-browser-check \
  --disable-features=Translate,MediaRouter,HttpsUpgrades,HttpsFirstModeV2,HttpsFirstBalancedModeAutoEnable \
  --disable-infobars \
  --force-device-scale-factor=1 --window-size="${W},${H}" --window-position=0,0 \
  --kiosk --remote-debugging-port="$CHROME_PORT" --app=about:blank \
  >/tmp/chrome-vid-${MODE}.log 2>&1 &
CH=$!
for i in $(seq 1 30); do
  if curl -s "http://127.0.0.1:$CHROME_PORT/json/version" >/dev/null 2>&1; then break; fi
  sleep 0.5
done
echo "chrome devtools: $(curl -s "http://127.0.0.1:$CHROME_PORT/json/version" | head -c 80)"
DISPLAY="$DISP" xdotool getdisplaygeometry

# the Chrome for Testing infobar sits above the page; measure it on a real
# frame and crop it out of the recording so no browser chrome appears.
sleep 1
ffmpeg -hide_banner -loglevel error -y -f x11grab -framerate 1 -video_size "${W}x${H}" \
  -draw_mouse 0 -i "$DISP" -frames:v 1 /tmp/topbar_${MODE}.png
BAR=$(python3 "$ROOT/video/measure_topbar.py" "/tmp/topbar_${MODE}.png" "$W")
H2=$((H - BAR))
echo "infobar height: ${BAR}px, recording ${W}x${H2}"

RUN_URL="${RUN_URL:-}" CDP_PORT="$CHROME_PORT" node "$ROOT/video/capture_site_xvfb.mjs" "$MODE" "$DISP" "$RAW" "$W" "$H2" "$BAR" 2>&1

kill "$CH" 2>/dev/null || true
kill "$XV" 2>/dev/null || true
rm -rf "$PROFILE"
echo "--- clips ---"
for f in "$RAW"/*.mp4; do
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames \
    -show_entries format=duration -of csv=p=0 "$f" | paste -sd' ' - | sed "s|^|$(basename "$f") |"
done
