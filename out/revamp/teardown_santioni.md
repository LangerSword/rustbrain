# Teardown 1/3: method, boot sequence, scroll architecture (santionispirits.com)

Study only. Measurements recorded; nothing from the site enters this repo (see
01_legal_and_licence.md for robots, terms and the copy boundary). Screenshots
are local under out/revamp/shots/ and gitignored.

## Method

- Legal first: robots.txt allows all; the site's legal notice forbids reusing
  its content; no reuse anywhere. See 01_legal_and_licence.md.
- Loads: about 18 sequential single-page loads across all probes, one at a
  time, no crawling, no concurrent loads. Analytics (googletagmanager,
  google-analytics) blocked at the network layer in every measured run.
- Browser: Playwright Chromium 156 (headless), 1440x900, hardware WebGL via
  ANGLE-Vulkan on the RTX 5060. Hardware matters: the site ships a GPU
  blocklist (tokens include "swiftshader", "basic render driver") and replaces
  itself with /unsupported when the WebGL renderer string matches, which is
  what a default headless run hits (~0.8 s in). MEASURED.
- Timing variance: two cold runs differ by seconds (cache, CPU load). Each
  figure carries its run scope. REA (the installed plugin, MCP server
  rea-agents@6.4.0) was additionally driven against a live CDP session for
  passive structure evidence; its evidence ids are recorded at the end.

## a. Boot sequence

- Shell: 32,519 bytes HTML (6,392 bytes compressed transfer). Inline boot
  script runs a feature test, then loads assets/js/app.<cache>.js async
  (2,086,900 bytes raw, 377,040 compressed). A Lottie loader animation
  (lottie.min.js 63,649 + loader.json 17,343) covers the load.
- Observed timeline, cold run (cast2; CPU busy with parallel work):
  - t+0.5 to 0.7 s: navigation commit; first paint 196 to 408 ms across probe
    runs (MEASURED range).
  - t+0.7 to ~9.5 s: loader phase: brand mark plus circular spinner over dark
    background; ~10 MB of assets stream during the first 12 s (155 responses
    in the study1 run; gate text was already live at t+4 s on that warmer run).
  - age gate (DOM): question text first ("ARE YOU OF ... LEGAL AGE?"), YES/NO
    buttons staggered after it; first clickable ~9.6 s cold, ~4 to 8 s warm
    (MEASURED range across runs).
  - click YES: gate exit begins ~430 ms after the click, opacity 1 to 0 over
    ~870 ms, element removed ~1.4 s after click (MEASURED, 15-point series).
  - title card "THE NOCTURNO EXPERIENCE" with a typewriter-style reveal; a
    partial word state was caught mid-reveal; fully visible by ~12.6 s cold.
  - drivable by input from ~12.6 s cold (~5 to 6 s warm).
- What the first 5 seconds look like: black shell, then the loader (logo plus
  spinner) over near-black, no content, no navigation; assets streaming
  behind. No intro video, no fake progress bar. (MEASURED, screenshots
  boot_*.png, cast frames.)

## b. Scroll architecture

- No smooth-scroll library. No native scroll at all: document scrollHeight
  equals the viewport (900 px at 1440x900; 844 px at 390x844), scrollY never
  changes, and wheel events are not preventDefaulted (there is nothing to
  scroll; MEASURED on both runs, 14 logged wheel events).
- Input model: the engine reads wheel, pointer and touch itself; one wheel
  beat advances one story beat. 8 scripted wheels (1,000 px delta, 1.7 s
  apart) produced 8 scene transitions (DERIVED from frame-diff bursts).
- Total scroll length: 0 px of document scroll. The story is a sequence of
  beats; observed at least 10 beats (gate, title, 8 wheel beats). The total
  beat count was not determined; asset paths name at least 10 chapters
  (intro, approach, colosseum, cathedral, wander, drink-selection,
  drink-pour, pillar-crumble, antigravity, target; names only).
- Pinned sections and scrub: not applicable. The viewport never moves, so
  every scene is pinned by construction; there is no scrub value and no
  scroll-to-animation mapping. Beats are discrete; each beat starts a
  transition shown in teardown 2/3 (0.18 to 0.52 s), then the scene holds
  nearly still until the next beat.
- Keyboard: no scroll to drive or break; see teardown 3/3 for keyboard access
  findings (none).

## REA structure evidence

REA drove four calls against the live page through its MCP server
(rea-agents@6.4.0, plugin rea 0.1.0) attached to the keeper browser (CDP
http://127.0.0.1:9223, hardware WebGL, post-gate state, 2026-10-19). Only
structure and measurements were read; nothing is saved from these runs.

- list_browser_targets: one page target, https://santionispirits.com/.
  Evidence ev_241bc4d3...9304e.
- inspect_web_page (2,500 ms window): DOM 334 nodes; accessibility tree 170
  nodes, 1,791 bytes of text retained. The tree exposes the nav labels, audio
  toggle, footer text and studio credits, one marketing paragraph and the
  rotating headline strings; the story captions are not in it. Scripts: 4.
  Worker targets: hydra-thread.js workers attached. Client storage: empty
  (localStorage, sessionStorage, indexedDB and cache all report zero usage).
  Console: one event, the loader's completion string logged from app.js.
  Evidence ev_ab034032...cf34f.
- inspect_web_event_listeners (body): no listeners registered directly on
  body; the evidence notes ancestors and delegates are not enumerated, so the
  wheel and pointer handling lives elsewhere (consistent with the engine's
  Interaction and Mouse classes seen at runtime). Evidence ev_765376c6...4ad.
- analyze_web_bundle: chunk graph contains lottie.min.js (305,542 bytes, sha
  e59aeea2...), the app bundle (sha 871e9123...), the shell inline boot script
  and the worker bootstrap; no third-party animation framework appears (no
  GSAP anywhere), which matches every runtime probe. Route-string candidates
  are audio one-shot paths and asset paths; no external network endpoints
  beyond the geo call; no WebMCP declarations; source maps not requested.
  The tool contract requires source capture; the call ran once inside REA's
  own session and only the structural outputs above were read out. Evidence
  ev_df8a4765...e403b.

Structure conclusion, corroborated by direct probes: the site is a custom
WebGL engine (Hydra, by Active Theory with Plan8, per the footer credits and
the class names observed live), not a GSAP site. Entry points: the shell
inline script, assets/js/app.<cache>.js, the hydra-thread worker bootstrap,
and lottie for the loader. There is no scroll system to name because there is
no scroll.
