# Teardown 2/3: motion spec and easing (santionispirits.com, study only)

Method: measurements from live runs; every row tagged MEASURED (observed value),
DERIVED (computed from observations) or PARTIAL (direction known, exact value
not isolated). Canvas-internal curves are deliberately not extracted (copy
boundary, see 01_legal_and_licence.md). Scope: one machine, RTX 5060, Chromium
156 headless, 1440x900 unless noted.

## c. Motion spec, one row per animated element role

| # | element role | trigger | property | from to | duration | ease | stagger | tag |
|---|---|---|---|---|---|---|---|---|
| 1 | age gate question text | on load | opacity | 0 to 1 | render lands between t+7.2 s and t+9.8 s cold | not isolated | question first | PARTIAL |
| 2 | age gate YES/NO buttons | after question | opacity | 0 to 1 | clickable within ~1.4 to 2.5 s after the question; exact curve not isolated | not isolated | delayed after question | PARTIAL |
| 3 | age gate exit | click YES | opacity | 1 to 0 | ~870 ms starting ~430 ms after click; element removed ~1.4 s after click | decay matches ease-in-out shape (15 samples: 1.00, .99, .97, .95, .90, .83, .73, .57, .39, .24, .14, .08, .04, .016, .004) | none | MEASURED |
| 4 | age gate button hover | hover | border-color + color | token change | 0.1 s | ease-in-out | none | MEASURED |
| 5 | header link (span) | hover | opacity | 0 to 1 | 0.4 s | ease-out | none | MEASURED |
| 6 | footer underline link | hover | transform (before/after rules) | hidden to shown | 0.3 s, plus 0.1 s delayed variant | CSS default | none | MEASURED |
| 7 | close (X) button | hover | opacity | low to 1 | 0.2 s | ease-out | none | MEASURED |
| 8 | story scene transition | wheel beat | whole canvas frame | scene A to scene B | 0.18 to 0.52 s per burst, mean ~0.32 s (8 bursts from 8 beats) | curve not extractable from canvas | beats independent | DERIVED |
| 9 | inter-beat hold | after transition | whole frame | stable | median frame difference 0.54 (0-255 scale), p90 7.1 | n/a | n/a | MEASURED |
| 10 | title card reveal | after gate | canvas mask/text reveal | partial to full | mid-reveal state observed (partial word); full by ~1.6 s after gate removal | not isolated | per letter | PARTIAL |
| 11 | boot loader | during load | Lottie animation loop | n/a | loop length not timed | Lottie JSON drives it | n/a | UNKNOWN |
| 12 | cursor | pointer move | in-canvas pointer effects | n/a | no DOM cursor element exists (queried; empty) | n/a | n/a | MEASURED |
| 13 | story captions and comic text | beat | canvas-painted | n/a | not DOM text (absent from innerText at story states) | n/a | n/a | DERIVED |
| 14 | audio toggle | click | audio state | on/off | not analyzed (out of scope) | n/a | n/a | UNKNOWN |

Text reveals by split: the DOM has no split-text elements; the only type
reveal observed is the canvas title card (typewriter/mask style). DOM text
(gate, nav, footer) enters via the transitions above, no per-line masks.
Image or video reveals: none in DOM; reveal work happens in the WebGL layer
(scene overlays). Horizontal scroll sequences: none observed. Page or section
transitions: the scene transitions (row 8). Menu open and close: header links
fade in (row 5); no full-page menu was opened during the study passes.
Canvas or WebGL layer: yes, the entire story; one full viewport canvas.

## d. Easing vocabulary and duration distribution

CSS layer, MEASURED from computed styles and rules:

- ease-out: 0.4 s (header link opacity), 0.2 s (close button opacity)
- ease-in-out: 0.1 s (gate button border-color and color)
- defaults: 0.1 s (footer social color), 0.3 s and 0.3 s + 0.1 s delay (footer
  underline transforms)
- @keyframes rules in the shell: zero. All CSS motion is transitions.

Gate exit decay, MEASURED: see row 3 above; closest standard shape is
ease-in-out; total ~870 ms.

Engine layer (names only, structure): fixed 60 Hz render loop
(Render.REFRESH_RATE = 60, FRAME_HZ_MULTIPLIER = 1.002 MEASURED from the live
page). The engine ships tween and curve classes (names observed in the global
class list: TweenManager, MathTween, TweenTimeline, FrameTween, CurveTweener)
and math primitives named smoothStep and lerp. No custom bezier definitions
are exposed in DOM or CSS; canvas tween curves cannot be named without reading
their code, which the copy boundary forbids.

Duration distribution over everything measured: min 0.1 s, median ~0.35 to
0.4 s, max ~0.87 s. Distinct observed values: 0.1, 0.2, 0.3, 0.4 s (exact,
CSS), ~0.87 s (gate), 0.167 to 0.517 s (scene transitions). The site's motion
recipe is short, discrete, and concentrated: quick bursts on each input beat,
near-still scenes in between.
