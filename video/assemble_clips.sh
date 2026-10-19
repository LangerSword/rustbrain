#!/usr/bin/env bash
# Assemble captured clips into the Remotion public folder: clips, stills for
# holds, audio, fonts, captions, durations. All footage is real and already
# 60 fps from ffmpeg x11grab or the terminal recordings.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RAW="$ROOT/out/video/raw"
CLIPS="$ROOT/out/video/clips"
PUB="$ROOT/video/remotion/public"
mkdir -p "$CLIPS" "$PUB/clips" "$PUB/audio" "$PUB/fonts" "$PUB/stills"

# named clips the composition expects
copy_as() { # src destname
  [ -f "$1" ] || { echo "missing $1"; return 0; }
  cp -f "$1" "$CLIPS/$2.mp4"
}
for c in hero successor_edge tabs gaps bugs readme actions; do
  copy_as "$RAW/site_fhd_xvfb/$c.mp4" "site_fhd_xvfb_$c"
  copy_as "$RAW/site_uhd_xvfb/$c.mp4" "site_uhd_xvfb_$c"
done
for c in naive query refresh assertions; do
  copy_as "$RAW/term/$c.mp4" "$c"
done

# real stills for holds, picked inside each clip
still() { ffmpeg -hide_banner -loglevel error -y -ss "$2" -i "$CLIPS/$1" -frames:v 1 "$PUB/stills/$3" 2>/dev/null || echo "still failed for $1"; }
still site_uhd_xvfb_hero.mp4 5 hero_hold.png
still site_uhd_xvfb_successor_edge.mp4 5 edge_hold.png
still site_uhd_xvfb_gaps.mp4 6 gaps_hold.png
still site_uhd_xvfb_bugs.mp4 5 bugs_hold.png
still site_uhd_xvfb_readme.mp4 8 readme_hold.png

# public assets
for f in "$CLIPS"/*.mp4; do ln -f "$f" "$PUB/clips/$(basename "$f")" 2>/dev/null || cp -f "$f" "$PUB/clips/"; done
[ -f "$ROOT/out/video/audio/premix.wav" ] && cp -f "$ROOT/out/video/audio/premix.wav" "$PUB/audio/premix.wav"
cp -f "$ROOT/site/assets/fonts/newsreader-400-normal.woff2" "$PUB/fonts/" 2>/dev/null || true
cp -f "$ROOT/site/assets/fonts/inter-100-900-normal.woff2" "$PUB/fonts/" 2>/dev/null || true
cp -f "$ROOT/out/video/captions.json" "$PUB/captions.json"
cp -f "$ROOT/out/video/captions.json" "$ROOT/video/remotion/src/captions.json"

python3 - <<PY
import json, subprocess, os
meta = {}
for f in sorted(os.listdir("$CLIPS")):
    if not f.endswith(".mp4"): continue
    d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",
                        os.path.join("$CLIPS",f)], capture_output=True, text=True).stdout.strip()
    if d:
        meta[f[:-4]] = round(float(d), 3)
json.dump(meta, open(os.path.join("$PUB","clips_meta.json"),"w"), indent=1, sort_keys=True)
print(json.dumps(meta, indent=1, sort_keys=True))
PY
echo "public ready: $PUB"
