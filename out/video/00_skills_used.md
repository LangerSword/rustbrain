# Demo video: skills and setup

Skills named per stage, exactly as installed (`hermes skills list`,
2026-10-19):

| stage | skill | what it gives |
|---|---|---|
| capture | `omh-browser` | policy overlay for browser tasks: auth, confirmation, rate |
| composition | `omh-frontend` | design-system-driven frontend workflow |
| composition | `omh-design-orchestration` | bounded design run preparation |
| QA | `omh-visual-qa` | observed-only visual review |
| QA | `omh-verification-gate` | define and record verification |
| orchestration | `omh-agent-board` | coordinate several Hermes agents on one board |
| orchestration (split) | `ulw-work` | split an accepted plan into disjoint parts |

All seven exist and are enabled. `subagent-delegation` backs the parallel
sub-agent work (footage, audio, Remotion).

## Tool report (MEASURED on this machine, 2026-10-19)

| tool | state | version / note |
|---|---|---|
| node | present | v26.7.0 |
| npm | present | 11.19.0 |
| python3 | present | 3.14.7 (numpy available for audio synth; verify at step 2) |
| ffmpeg | present | 9.0.1 (static build). `x11grab` demuxer present; `lavfi` present |
| ffprobe | present | 9.0.1 |
| chromium / google-chrome | present | Google Chrome for Testing 151.0.7922.34 (`chromium`, `chromium-browser`, `google-chrome`, `google-chrome-stable` all resolve to it) |
| Remotion (npm) | NOT installed | npm registry latest is 4.0.536; will pin `remotion@4.0.536` and `@remotion/cli@4.0.536` in `video/remotion/` |
| asciinema | NOT installed | exact install: `cargo install asciinema` (crates.io, v3.2.0) or `pipx install asciinema` |
| agg | NOT installed | exact install: `cargo install --git https://github.com/asciinema/agg` (docs.asciinema.org/manual/agg/installation) |
| Xvfb / xvfb-run | present | /usr/bin/Xvfb, /usr/bin/xvfb-run |
| kitty (terminal) | present | 0.49.2, with xdotool present |
| playwright browsers | cached | `~/.cache/ms-playwright`: chromium-1194/1234/1243, chromium_headless_shell-1234/1243, firefox-1543, ffmpeg-1011. The `playwright` package itself gets pinned in the video project at step 1. |

Every missing tool is listed with its install command above; nothing is
improvise around. The terminal capture route is decided at step 1.2 after
the fps measurement: asciinema plus agg (installed with the commands above)
or the present fallback Xvfb plus kitty plus ffmpeg x11grab at 60 fps.

Sequencing: the revamp lands first and the footage captures the live site at
https://langersword.github.io/rustbrain/ after the revamp passes its stage 6,
so the video shows the same product the site now is. If the revamp had not
passed, footage would have captured the live site unchanged; both are the
real live site, never a mock.
