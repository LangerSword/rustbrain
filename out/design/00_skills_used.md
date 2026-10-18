# Skills used, by part

Named as required: the OMH skills for research, orchestration, frontend, browser,
screenshot and verification, plus the skill called REA.

Installed skills were listed with `hermes skills list` (2026-10-19). The OMH entries
below are external skills the list shows as enabled. Mechanisms also come from the
non-OMH skills named at the end.

| part | need | skill | what it gives |
|---|---|---|---|
| Part 1 | verification | omh-verification-gate | define and record verification; keep claims and evidence separate |
| Part 1.5 | self-audit | evidence-bounded-dataset-research | numbers measured with scope, not asserted |
| all parts | research | omh-best-practice-research | bounded official/upstream best-practice research with sources |
| all parts | research (deep) | ulw-research | deep research engine for grounding specs and decisions |
| Part 2.2 | source shortlist | omh-source-finder | typed source candidate inventory |
| Part 2 | orchestration | omh-agent-board | coordinate several Hermes agents on one board |
| Part 2.3 | orchestration (split) | ulw-work | split an accepted plan into disjoint parts |
| Part 2.3 | browser | omh-browser | policy overlay for browser tasks: auth, confirmation, rate |
| Part 2.3 | live info | omh-live-info | live lookups with provider and freshness, so every measured value carries a source |
| Parts 2, 6 | screenshot | omh-visual-qa | observed-only visual review workflow |
| Parts 4, 5 | frontend | omh-frontend | design-system-driven frontend workflow |
| Parts 4, 5 | frontend (orchestration) | omh-design-orchestration | bounded design run preparation |
| Parts 4, 5 | frontend (gate) | omh-design-quality-gate | design quality gate enforcement |
| Part 6 | verification (audit) | omh-production-audit | release evaluation against evidence |

Also used, not OMH: `subagent-delegation` (background subagents),
`web-app-verification` (scripted-browser checks), `web-perf` (page weight and LCP),
`design-taste-frontend` (frontend taste rules), `grounded-citations` (quotes with
sources).

## REA

REA is not one of the OMH skills and is not installed on this machine: neither
`hermes skills list` nor `~/.hermes/plugins/` contains it (checked 2026-10-19).

Identified from the Hermes docs, https://hermes-agent.nousresearch.com/docs/plugins/rea,
which say it is the official plugin "Reverse engineer programs with REA (rea.tools)".
One line: REA (Reverse Engineer Anything) inspects programs, including native
binaries, .NET assemblies, Electron and JavaScript apps, Android packages, firmware,
and packet or browser captures, through its MCP server, and returns structured
evidence for the agent to explain or build from.

Install if wanted: `hermes plugins install rea` then `hermes plugins enable rea`;
it needs Node.js 22.19+/24.11+/26+ with npx. This brief has no reverse-engineering
step, so REA is named here and not used.
