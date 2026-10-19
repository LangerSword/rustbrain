#!/usr/bin/env bash
# Cut B mixing: if out/video/vo/voiceover.wav exists, mix it with the music
# ducked under the voice and the sfx on top, render cut B with keyword
# captions, and exit 0 either way. Absent voiceover: it just says so.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VO="$ROOT/out/video/vo/voiceover.wav"
MUSIC="$ROOT/out/video/audio/music.wav"
SFX="$ROOT/out/video/audio/sfx.wav"
MIX="$ROOT/out/video/audio/cut_b.wav"
OUT="$ROOT/out/video/rustbrain_demo_vo.mp4"
PUB="$ROOT/video/remotion/public/audio"

if [ ! -f "$VO" ]; then
  echo "no voiceover at $VO yet. record one, save it there, then rerun this script."
  exit 0
fi
if [ ! -f "$MUSIC" ] || [ ! -f "$SFX" ]; then
  echo "missing music.wav or sfx.wav under out/video/audio"
  exit 1
fi

# music ducked about 9 dB under the voice (sidechaincompress), then mixed with
# sfx and the voice, mastered to about -16 LUFS, true peak under -1 dBTP.
ffmpeg -hide_banner -loglevel error -y \
  -i "$MUSIC" -i "$VO" -i "$SFX" \
  -filter_complex "[1:a]asplit=2[vo1][sc]; \
    [0:a][sc]sidechaincompress=threshold=0.03:ratio=8:attack=5:release=300[duck]; \
    [duck][vo1][2:a]amix=inputs=3:duration=longest:weights=0.36 1 0.5[mix]; \
    [mix]loudnorm=I=-16:TP=-1.0:LRA=11[out]" \
  -map "[out]" -ar 48000 "$MIX"
ffmpeg -hide_banner -loglevel error -y -i "$MIX" -af loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json -f null - 2>&1 | tail -14

mkdir -p "$PUB"
cp -f "$MIX" "$PUB/cut_b.wav"
cd "$ROOT/video/remotion"
npx remotion render src/index.ts Demo "$OUT" --props='{"vo":true}' \
  --codec=h264 --crf=16 --pixel-format=yuv420p --audio-codec=aac --audio-bitrate=192k \
  --concurrency=4 --log=error 2>&1 | tail -3
ffmpeg -hide_banner -loglevel error -y -i "$OUT" -c copy -movflags +faststart "${OUT%.mp4}.fs.mp4"
mv -f "${OUT%.mp4}.fs.mp4" "$OUT"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
echo "cut B: $OUT"
