# 10: the picks, ranked, with verification notes

Source: the GSAP showcase gallery (gsap.com/showcase/, read on 2026-10-19).
Five sites were torn down by parallel sub-agents, then every load-bearing
claim was re-run by me in a fresh scripted session before it could enter this
file. Verification outcomes are stated per row: CONFIRMED EXACT (re-measured
to the stated value), CONFIRMED MECHANIC (behaviour reproduced, numbers within
run variance), CORRECTED (value or label changed after re-measuring), or
SINGLE-RUN (only the sub-agent's run; not independently reproduced).

## Techniques that go into the revamp, ranked

1. Self-measuring stroke draw (Extrafazant, mappy). Each path gets a dash
   array equal to its own runtime length; only the offset animates. Re-verified:
   Extrafazant keeps its transition shape retracted at "0px, 999999px" with
   offset -5106.16, and its underlines carry "length px, 0.1px" (CONFIRMED
   EXACT, 5106.16). mappy's six story edges measure 161.256, 160.214, 138.931,
   139.545, 139.545, 139.545 px in hidden state (CONFIRMED EXACT, matched the
   sub-agent row to 0.001 px). Used in: scene 3 (the SUCCEEDED_BY hop draws
   itself), scene 4 (the true gap stops as a stub line), the gaps page tier
   connectors. Implementation: DrawSVG plus one getTotalLength query per path,
   never a hand-tuned dash value.

2. Pinned stage with scrub (Extrafazant). Its featured section pins from scroll
   1665 to 3825 with scrub 0.3 (CONFIRMED EXACT). Used in: scene 3, the hop
   is the one pinned scene of the story; scrub 0.3 is the starting token.
   The A24 variant of this technique (pin 2160 px) did NOT reproduce in two
   verification runs (its document height measured 900 px with one trivial
   ScrollTrigger; SINGLE-RUN, rejected).

3. Enter-driven multi-speed leader timelines (Staanzza). One trigger per
   section fires a timeline where several speeds run in parallel (0.5 s fades,
   1 s collapses, 3 s pushes). Re-verified: 26 ScrollTriggers (sub-agent said
   27; CORRECTED to 26, both of my runs agree), plugins registered live are
   ScrollTrigger, Flip, Observer and SplitText (CONFIRMED EXACT), and the
   triggers carry scrub 0.8 (sub-agent reported zero scrubbed; CORRECTED: the
   value sits in vars.scrub, 0.8, sampled on six triggers). Used in: every
   scene gets one leader timeline; scene 5 runs its counters and tier bars in
   parallel under one trigger.

4. Masked line and character reveals (Extrafazant measured from tween vars;
   mappy char-per-frame reveal CONFIRMED by length growth 4 to 41 chars at one
   per frame). Used in: scene 1 (RFC 1892 card, masked lines), scene 5
   (tier scope labels), scene 6 (limits lines). Implementation: SplitText with
   an overflow mask wrapper; tokens start from expo.out, lines stagger 0.07 s,
   characters 0.0175 s, duration 1.05 to 1.16 s (source values; SINGLE-RUN for
   the tween vars, mechanic reproduced live).

5. Counter animation as a first-class beat (site rhythm evidence from IKEA:
   loader dot loop 1200 ms linear with 0 / 200 / 400 ms delays, CONFIRMED
   EXACT, plus a 16 s ambient drift CONFIRMED; the 17 / 18.25 / 19 s drift
   variants were SINGLE-RUN). Used in: scene 5, counters run to their
   data.json values over ~1.2 s on one ease family, staggered by row.

6. Flip for the demo result swap (no confirmed live Flip site among the picks:
   Staanzza registers Flip but its own file shows no flip call on the story,
   and A24 has none. This is a designed use, kept inside the licence.) Used
   in: scene 2 to scene 3, the result block swaps archived to successor with
   Flip so the roster table visibly re-groups instead of hard-switching.

## Rejected, with reasons

- Scroll smoothing layers: Lenis at lerp 0.1 to 0.165 (Staanzza, Extrafazant)
  and ScrollSmoother (allowed by licence). Rejected: the revamp requires
  native scroll (keyboard, anchors, back button, reload restore, zoom at 200
  percent). Extrafazant also runs its smoothing with no reduced-motion branch,
  which is the exact failure the revamp must not carry.
- A24's pinned scrub numbers, 32 s marquee tween, 450 ms dot curve and cursor
  strip: SINGLE-RUN and not reproduced in two verification sessions (its page
  measured 900 px tall with no usable triggers in mine). Nothing from A24
  enters the build.
- IKEA ambient desynchronised drift loops (16 s confirmed): rejected as
  decoration on a data page; motion must explain the product. Its locked
  intro video gate (page unusable when media stalls; re-verify note: the video
  did play in my session, so that gate is environment-sensitive, which is its
  own argument against it) is a pattern to avoid.
- MorphSVG (tagged on Staanzza, absent at runtime there and everywhere else
  measured): nothing in the story needs shape morphing.
- Horizontal scroll rails (Staanzza rail -428.4 px, A24): no scene needs one;
  keeps scroll length lean.
- Observer for input capture: refused on the site (do not re-implement any
  input hijack); Observer is used only on the debug page to scrub timelines.
- Canvas-only WebGL architecture (Santioni): never. The revamp is HTML-first
  with progressive enhancement; the teardown's failure list (no reduced
  motion, no keyboard, no no-JS, zoom disabled) is the anti-brief.
- Cursor-follow layers (both candidates measured 0 width or unverified):
  not used on the site; a plain visible focus ring is worth more.

## Cross-cutting numbers adopted as starting tokens

0.5 to 1.2 s scene interior speeds (Staanzza corrected set), 0.3 scrub
(Extrafazant exact), 1.05 to 1.16 s masked reveals with expo.out (Extrafazant),
one character per frame ceilings for type stepping (mappy exact), 0.12 to
0.18 s UI transitions (mappy). All are starting values; the motion tokens
file owns them from here and stage 6 measures what actually ships.
