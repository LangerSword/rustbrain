#!/usr/bin/env bash
# QA 5.1: extract frames every 0.25 s and around every cut, build contact
# sheets for vision review. Usage: bash video/qa_frames.sh <video.mp4>
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VIDEO="${1:?usage: qa_frames.sh video.mp4}"
NAME="$(basename "${VIDEO%.mp4}")"
DIR="$ROOT/out/video/qa/$NAME"
mkdir -p "$DIR/frames" "$DIR/sheets"

# every 0.25 s, small jpgs
ffmpeg -hide_banner -loglevel error -y -i "$VIDEO" -vf "fps=4,scale=480:-1" -q:v 4 "$DIR/frames/f_%05d.jpg"

# frames around each cut (cut seconds from the storyboard beats)
for t in 0 12 30 65 110 135 160 170 180; do
  for off in -0.10 -0.025 0.025 0.10; do
    tt=$(python3 -c "print(max(0, $t + $off))")
    ffmpeg -hide_banner -loglevel error -y -ss "$tt" -i "$VIDEO" -frames:v 1 -q:v 3 \
      "$DIR/frames/cut_${t}_${off}.jpg" 2>/dev/null || true
  done
done

# contact sheets, 8 columns, chronological
ls "$DIR/frames"/f_*.jpg | sort > "$DIR/list.txt"
split -l 48 "$DIR/list.txt" "$DIR/chunk_" 2>/dev/null || true
i=0
for chunk in "$DIR"/chunk_*; do
  [ -f "$chunk" ] || continue
  i=$((i+1))
  ffmpeg -hide_banner -loglevel error -y -pattern_type glob -i "$DIR"/frames/f_*.jpg \
    -vf "tile=8x6" "$DIR/sheets/all_$i.jpg" 2>/dev/null || true
  break
done
echo "frames: $(ls "$DIR/frames" | wc -l), sheets: $(ls "$DIR/sheets" 2>/dev/null | wc -l)"
