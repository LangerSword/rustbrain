# Skills used, by stage (revamp)

Command run: `hermes skills list` (2026-10-19, 284 enabled). Plugin state:
`hermes plugins list --plain --no-bundled`. Names below are exactly as installed.

## (a) design taste and design review

- `design-taste-frontend` (installed, local, enabled): the anti-slop frontend
  taste skill. Also present and related: `design-taste-frontend-v1`,
  `gpt-taste`, `high-end-visual-design`, `minimalist-ui`,
  `stitch-design-taste`, `industrial-brutalist-ui`, `redesign-existing-projects`.
- `omh-design-quality-gate` (installed, external, enabled): runs over each
  scene at stage 6.4 as the brief requires.

## (b) GSAP

Installed, all enabled, loaded when the build starts:
`gsap-core`, `gsap-scrolltrigger`, `gsap-timeline`, `gsap-plugins`,
`gsap-performance`, `gsap-utils`, `gsap-react`, `gsap-frameworks`.
Also `gsap-static-site` (project site in TypeScript plus GSAP), the closest
build workflow skill to this revamp.

Hub check: `hermes skills search gsap` shows the official set on skills.sh as
`skills-sh/greensock/gsap-skills/<name>` (upstream: greensock/gsap-skills),
verified ids include `skills-sh/greensock/gsap-skills/gsap-core`,
`.../gsap-plugins`, `.../gsap-performance`, `.../gsap-react`,
`.../gsap-frameworks`; community duplicates exist from other authors
(mengto, mindrally, ...). The official set is already installed, so nothing
was missing and nothing needed installing. If an install had been needed the
documented command is `hermes skills install <identifier>`.

## (c) REA

REA (Reverse Engineer Anything) is not a skill; it is the official Hermes
plugin `rea` (rea.tools). Install is done: `hermes plugins install rea`, then
`hermes plugins enable rea` (both run 2026-10-19). Result:
`catalog:official@6dacaadd 0.1.0`, location `~/.hermes/plugins/rea`, enabled
(MCP takes effect next session; the same server also runs directly as
`npx -y rea-agents@6.4.0 mcp`). Needs Node 22.19+/24.11+/26+; machine has
Node v26.7.0. Docs: https://hermes-agent.nousresearch.com/docs/plugins/rea.
Stage 2 use is structure only: which GSAP plugins load, how timelines are
organised, what the entry points are. Findings are recorded as measurements;
no code is extracted or reused; REA's ask-before-execute list is respected.

## (d) OMH

All installed (external, enabled):

- `omh-browser`: policy overlay for browser tasks (auth, confirmation, rate)
- `omh-frontend`: design-system-driven frontend workflow
- `omh-design-orchestration`: bounded design run preparation
- `omh-visual-qa`: observed-only visual review
- `omh-verification-gate`: define and record verification

## Also used

`subagent-delegation` (parallel teardowns at stages 2 and 3),
`reference-site-teardown` (study method for reference sites),
`web-perf` (page weight and performance method), `web-app-verification`
(scripted-browser checks at stage 6), `grounded-citations` (quotes carry
sources).
