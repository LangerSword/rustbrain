#!/usr/bin/env bash
# Render cut A: captions + music + sfx, no voice. The complete deliverable.
# H.264 CRF 16, yuv420p, AAC 192k, faststart, 1920x1080 at the composition fps.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/out/video/rustbrain_demo_captions.mp4"

cd "$ROOT/video/remotion"
npx remotion render src/index.ts Demo "$OUT" \
  --codec=h264 --crf=16 --pixel-format=yuv420p --audio-codec=aac --audio-bitrate=192k \
  --concurrency=4 --log=info 2>&1 | tail -6

# faststart rewrite without re-encoding
ffmpeg -hide_banner -loglevel error -y -i "$OUT" -c copy -movflags +faststart "${OUT%.mp4}.fs.mp4"
mv -f "${OUT%.mp4}.fs.mp4" "$OUT"
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_name,width,height,r_frame_rate \
  -of default=nw=1 "$OUT"
ls -la "$OUT"
