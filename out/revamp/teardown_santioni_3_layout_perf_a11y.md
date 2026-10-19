# Teardown 3/3: layout, mobile, performance, failures (santionispirits.com, study only)

Scope: one machine, RTX 5060, Chromium 156 headless; desktop 1440x900 and
mobile 390x844 unless noted. Every figure tagged.

## e. Layout

- One full viewport stage: a single canvas (CSS 1440x900, backing store
  2160x1350, a 1.5x render scale) MEASURED. Canvas position absolute, z-index
  auto; DOM overlays (age gate, header menu, footer) sit above it.
- DOM weight: 680 nodes total; LayoutDuration 0.07 s and RecalcStyleDuration
  0.16 s over a 27 s session (CDP metrics MEASURED). This is a canvas-first
  site with a very thin DOM.
- Type, family NAMES only (commercial faces, not reused): Charles Rosie
  Regular (display serif), PP Nikkei Maru Regular and Ultrabold (sans), GT Era
  Text Light (text). Observed sizes: the shell CSS defines .heading1 at 217px
  at >=768 px, uppercase, weight 400, letter-spacing 0.005em (MEASURED from
  the shell stylesheet); a mobile calc value of 81.6667px appears for small
  screens (exact property not isolated).
- Colours: near-black stage. #121212 appears in shell CSS (MEASURED); gate
  background near-black in screenshots; white type; red used as accent within
  the artwork. Beyond these, colour lives in canvas art, not CSS tokens.
- Spacing and grid: no grid system in CSS; composition is a centered stage.
- Layering: canvas first, DOM overlays above; no z-index complexity observed.

## f. Mobile at 390 px (MEASURED, 390x844, DPR 2, touch)

- The full experience loads on mobile, not a stripped fallback. Canvas backing
  780x1688 at 390x844 CSS (2x). touch-action: none on body (the page owns all
  gestures). Device.mobile reports {phone: true}. Tapping YES on the gate via
  a real touch event dismisses it.
- A swipe gesture path was not exercised (unverified); wheel does nothing on
  touch (no wheel device).
- Same DOM labels as desktop; audio toggle present.
- Nothing observed as disabled on mobile: the same story, the same canvas.

## g. Performance (scope tagged per figure)

- Transfer: 10,024,606 bytes (~10.0 MB) in the first ~27 s of a cold run
  (MEASURED, cast run). Split: fetch (JSON, geometry .bin, ktx2 textures)
  9.41 MB; link 377 KB (app bundle + font preloads); css 124 KB; script
  64 KB; img 18 KB. The app bundle is 2,086,900 bytes raw, 377,040 bytes over
  the wire with compression. Loading continues beyond the 27 s window.
- Frame cadence: rAF sampler, 1,820 samples over 31 s: mean interval 17.40 ms,
  p95 17 ms; 20 frames over 25 ms (1.1%), 8 over 50 ms (0.44%) (MEASURED).
- Long tasks: 8 during the journey; boot tasks 54 to 109 ms each; worst 361 ms
  at ~5.9 s (asset compile and init); a 261 ms hitch at the gate-to-intro
  transition in another run (MEASURED, two runs).
- CPU: TaskDuration 5.84 s over ~27 s wall (~21%), ScriptDuration 3.44 s,
  LayoutDuration 0.07 s, RecalcStyleDuration 0.16 s; JS heap 52.8 MB
  (MEASURED, CDP metrics).
- CDP screencast capture: 1,748 frames over 31.4 s, median interval 16.7 ms,
  mean 18.0 ms (~56 fps mean) (MEASURED).
- Heaviest scene: boot (361 ms) and gate-to-intro (261 ms); steady-state
  scenes hold ~60 fps; inter-beat holds are near-static (median frame diff
  0.54 of 255), so the compositor is cheap between beats.
- Availability note: software renderers (SwiftShader, "basic render driver")
  are matched by the site's GPU blocklist and redirected to /unsupported. That
  is a deliberate quality gate (MEASURED); it also means the site is
  unavailable on machines without hardware WebGL.

## h. Failures to avoid (all MEASURED unless tagged)

1. Zoom disabled: viewport meta is "width=device-width, initial-scale=1.0,
   maximum-scale=1.0, user-scalable=no, minimal-ui, viewport-fit=cover".
   Never copy this.
2. No prefers-reduced-motion handling: zero references in the app bundle; the
   full motion experience runs unchanged for reduce users.
3. No keyboard access: 14 consecutive Tab presses left focus on body; the
   gate YES/NO and menu items are DIVs, not buttons; no focusable controls; no
   skip link; no focus styles observed.
4. No-JS: the page shows only "Please enable javascript"; zero content.
5. Story text is canvas-painted: captions are absent from the DOM
   (DERIVED from innerText dumps); screen readers get only gate, nav and
   footer strings.
6. Nav links are "#" placeholders; anchors and back button carry no meaning;
   there is no native scroll position to restore.
7. Input is fully owned end to end (wheel, pointer, touch): a deliberate total
   hijack, workable here because the entire page is one experience, but the
   pattern cannot be transplanted onto a document site.
8. Software-renderer users are redirected away without a path forward
   (availability limitation, by design).

## Copy boundary compliance for this teardown

Nothing from the site (code, text, images, fonts, assets) was copied into this
repository. Study screenshots are local only and gitignored. The app bundle
was examined in memory, only for structure questions (entry points, module
names, engine class names); all findings are recorded as measurements, and no
code was extracted or reused.
