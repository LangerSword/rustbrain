# Video QA log, rustbrain demo (captions cut)

Final render: `out/video/rustbrain_demo_captions.mp4`
1920x1080, 60 fps, h264 CRF 16, AAC 192k, faststart. 180.011 s, 28,535,808 bytes
(MEASURED, ffprobe, 2026-10-19). The mp4 itself is gitignored; scripts are in `video/`.

## Build chain
- Composition: `video/remotion/src/Demo.tsx`; captions from `out/video/captions.json` (beats
  0 to 12, 12 to 30, 30 to 65, 65 to 110, 110 to 135, 135 to 160, 160 to 180; segment spans
  match beat durations exactly, verified by reading both files side by side).
- Footage: headed Chrome under Xvfb recorded with ffmpeg x11grab at 60 fps (site clips, README,
  Actions page) and scripted real terminal sessions (route naive, routing query, refresh diff,
  assertions). All clips re-normalized to CFR 60, time base 1/90000, keyframes every 30 frames,
  no B-frames (`video/assemble_clips.sh`). This normalization was required: the Remotion
  compositor failed mid-file frame extraction ("No frame found at position") on the raw
  1/15360-timebase captures, in two earlier render attempts.
- Audio: code-synthesized stems, `video/audio/synth.py`, premix `-16.00 LUFS / -2.94 dBTP /
  186.000 s` (MEASURED by ffmpeg loudnorm, re-verified by hand), embedded into the render.

## Checks on the rendered file (all measured, not assumed)
| check | result | source |
| --- | --- | --- |
| first-frame luma (signalstats YAVG at 0.2 s) | 28.74, not black; prompt and caption typing visible | `python3 video/qa_render.py` |
| longest hold in the body (scdet mafd < 0.002) | 3.7 s, under the 4 s rule | same |
| endcard hold | 4.2 s at t=172.2 s, exempt by design (title card, music tail) | same |
| caption dwell | every caption at least 1.2 s on screen | same, from captions.json timings |
| loudness on the rendered file | I -15.95 LUFS, TP -2.94 dBTP, LRA 4.60 | same, ffmpeg loudnorm |
| compositor extraction errors during render | 0 (error count over full log) | `/tmp/render_cut_a5.log` |
| caption number audit | 194 numbers allowed from site/data.json and the recorded transcripts; every caption number sourced | `python3 video/qa_text.py` |
| text scan | no em or en dashes, no emoji, no banned words, no emails, no local paths | same |

Verdict: `qa_render.py` PASS, `qa_text.py` PASS.

## Frames extracted and reviewed (vision pass, described to the entrant)
- t=0.2 s: terminal prompt "rustbrain $" plus the caption typing in, no black frame.
- t=60 s: site with tabs; active tab T-dev-tools, true-gap card, caption "t-dev-tools has no
  team file anywhere: 20 of the 761 merged rfcs, a true gap."
- t=120 s: gaps page tier 1 and tier 2 tables plus the tier 3 heading with its scope line.
- t=175 s: end card: graph mark, serif wordmark, rustbrain.langersword.in, "track 03: company
  brain", stats 761 / 162 / 25, footer "volunteer teams, a curated successor map, 52 archived
  files audited." No rendering flaw seen.
- Hold stills re-checked after regeneration: `readme_hold.png` shows the README with the Graph
  data model heading; `gaps_hold.png` shows tier 3 with its rows (T-dev-tools 20 included).

## Known, accepted trade-offs
- Captions sit on a bottom scrim, so during hold beats they cover the lower strip of the page
  (for example the first tier 3 table rows on the gaps page). The tier numbers are restated in
  the unobstructed scope strip at the top of that page, and the full tables are visible in the
  screenshots pack. Noted here so it is not mistaken for a defect.
