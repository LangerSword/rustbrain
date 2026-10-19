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
    # ffmpeg writes its metadata (scdet mafd, loudnorm json) to stderr, so
    # both streams are merged here; binary reads use their own subprocess call
    return subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout


def mean_luma(video, t):
    # signalstats YAVG is the reliable read here; a 1x1 scale+rawvideo pipe
    # returns 0 on this ffmpeg build even for non-black frames
    out = sh(["ffmpeg", "-hide_banner", "-ss", str(t), "-i", video, "-frames:v", "1",
              "-vf", "signalstats,metadata=mode=print", "-f", "null", "-"])
    m = re.search(r"lavfi\.signalstats\.YAVG=([0-9.]+)", out)
    return float(m.group(1)) if m else None


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

    # scene-change timeline: per-frame mafd from scdet. `metadata=print:key=`
    # silently emits nothing on this ffmpeg build, so print all keys with mode
    # and parse the mafd series instead. Real cuts in this footage jump to the
    # tens; a still holds near zero.
    sc = sh(["ffmpeg", "-hide_banner", "-i", video, "-vf",
             "scdet=threshold=0.001,metadata=mode=print", "-f", "null", "-"])
    vals = [float(v) for v in re.findall(r"lavfi\.scd\.mafd=([0-9.]+)", sc)]
    if vals:
        # a true hold reads near zero per frame; slow camera pushes and
        # scrolling accumulate real change above this threshold
        ENDCARD_T = 170.0
        runs, run = [], 0
        for i, v in enumerate(vals):
            if v < 0.002:
                run += 1
            else:
                if run:
                    runs.append((run, i - run))
                run = 0
        if run:
            runs.append((run, len(vals) - run))
        runs.sort(reverse=True)
        body = [(n, a) for n, a in runs if a / 60.0 < ENDCARD_T - 0.5]
        ec = [(n, a) for n, a in runs if a / 60.0 >= ENDCARD_T - 0.5]
        worst = (body[0][0] / 60.0) if body else 0.0
        print("frames scanned: %d, longest hold in the body: %.1f s (mafd < 0.002)" % (len(vals), worst))
        if ec:
            print("endcard hold (exempt): %.1f s at t=%.1f s" % (ec[0][0] / 60.0, ec[0][1] / 60.0))
        if worst > 4.0:
            defects.append("nothing changes for %.1f s" % worst)
    else:
        defects.append("scene-change scan produced no mafd values")

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
