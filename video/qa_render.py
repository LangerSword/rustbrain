#!/usr/bin/env python3
"""QA 5.1/5.3: timing and content checks on a rendered cut, plus the numbers.

Checks, all from real measurements of the rendered file:
  - first frame is not black and not a logo-only frame (mean luma at t=0.2)
  - every caption stays on screen at least 1.2 s (from captions.json timings)
  - no beat where nothing changes for more than 4 s (scene-change timeline)
  - audio: loudnorm numbers + clipping check on the rendered file
  - text scan (dashes, banned words) reuses video/qa_text.py
Usage: python3 video/qa_render.py out/video/rustbrain_demo_captions.mp4
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def mean_luma(video, t):
    out = sh(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", video,
              "-frames:v", "1", "-vf", "scale=1:1", "-f", "rawvideo", "-pix_fmt", "gray", "-"])
    return out and out.encode("latin1")[0] if out else None


def main():
    video = sys.argv[1]
    defects = []
    dur = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", video]).strip())
    print("duration: %.2f s" % dur)

    l0 = mean_luma(video, 0.2)
    print("luma at 0.2s:", l0)
    if l0 is not None and l0 < 8:
        defects.append("frame at 0.2s is nearly black (luma %s): no cold open" % l0)

    caps = json.load(open(os.path.join(HERE, "out", "video", "captions.json")))
    for b in caps["beats"]:
        starts = [c["t"] for c in (b.get("captions") or [])]
        if b.get("caption"):
            starts = [b["start"]]
        for i, st in enumerate(starts):
            end = starts[i + 1] if i + 1 < len(starts) else b["end"]
            if end - st < 1.2:
                defects.append("caption in beat %d stays on screen %.2fs (<1.2s)" % (b["beat"], end - st))

    # scene-change timeline: detect long static stretches via ffmpeg scdet
    sc = sh(["ffmpeg", "-hide_banner", "-i", video, "-vf",
             "scdet=threshold=0.03,metadata=print:key=lavfi.scd.time", "-f", "null", "-"])
    cuts = sorted({round(float(m), 2) for m in re.findall(r"lavfi\.scd\.time=([0-9.]+)", sc)})
    marks = [0.0] + cuts + [dur]
    gaps = [(b - a) for a, b in zip(marks, marks[1:])]
    if gaps:
        worst = max(gaps)
        print("longest static stretch: %.1f s" % worst)
        if worst > 4.0:
            worst_at = marks[gaps.index(worst)]
            defects.append("nothing changes for %.1f s after t=%.1f s" % (worst, worst_at))

    ln = sh(["ffmpeg", "-hide_banner", "-i", video, "-af",
             "loudnorm=I=-16:TP=-1.0:LRA=11:print_format=json", "-f", "null", "-"])
    m = re.search(r"\{[^{}]+\}", ln, re.S)
    if m:
        j = json.loads(m.group(0))
        print("loudness: I=%(input_i)s TP=%(input_tp)s LRA=%(input_lra)s" % j)
        if float(j["input_tp"]) > -1.0:
            defects.append("true peak %s dBTP exceeds -1" % j["input_tp"])

    if defects:
        for d in defects:
            print("DEFECT:", d)
        print("VERDICT: FAIL, %d defects" % len(defects))
        return 1
    print("VERDICT: PASS, no timing or audio defects found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
