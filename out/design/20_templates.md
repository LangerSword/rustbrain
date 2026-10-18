# Templates and fonts (Part 3)

Licences verified 2026-10-19 by fetching each licence file and reading its first
line (HTTP 200 on every fetch; the quoted text is the opening licence line).

## 3.1 Candidate templates and component sets

| candidate | URL | licence, quoted | stack | provides | lacks |
|---|---|---|---|---|---|
| Astro Paper | github.com/satnaing/astro-paper | MIT License | Astro, TypeScript, Tailwind | complete blog/portfolio theme, dark mode, SEO, a11y baseline | no data/table components, blog-shaped IA, would fight a custom product hero |
| Pico CSS | github.com/picocss/pico | MIT License | classless CSS | semantic defaults, tiny, dark mode | no components, no layout system, no motion |
| GOV.UK Frontend | github.com/alphagov/govuk-frontend | The MIT License (MIT) | Nunjucks, SCSS | heavily tested a11y components (tabs, tables, accordions) | government look, no editorial type, Nunjucks build |
| IBM Carbon | github.com/carbon-design-system/carbon | Apache License (2.0) | React, SCSS | full enterprise design system, tokens | heavy React runtime, 150 KB+ CSS, generic enterprise look |
| shadcn/ui | github.com/shadcn-ui/ui | MIT License | React, Tailwind, Radix | copy-in components, good a11y primitives | React runtime, Tailwind toolchain, not static-first |

Decision (5 lines): build from scratch with design tokens, no template base. The
hero is a live product demo with a custom inline SVG graph, which no template
ships; every candidate would be removed faster than it is adopted. A classless
base (Pico) is tempting but its defaults would be overridden by the editorial
palette anyway, and the site needs under 150 KB of JS, which rules out the React
systems. The verified MIT/Apache licences above remain options if the entrant
prefers one later; nothing from them is copied into this repository.

## 3.2 Fonts (at most two families, open licence, self-hosted, no remote calls)

| family | role | licence, quoted | source | fallback stack |
|---|---|---|---|---|
| Newsreader | display and headlines | "This Font Software is licensed under the SIL Open Font License, Version 1.1." | github.com/google/fonts ofl/newsreader | Georgia, 'Times New Roman', serif |
| Inter | body, UI and tables | "This Font Software is licensed under the SIL Open Font License, Version 1.1." | github.com/google/fonts ofl/inter | system-ui, -apple-system, 'Segoe UI', sans-serif |

Both are OFL-1.1: bundling the woff2 files with the site is permitted, the fonts
may not be sold on their own, and the licence file ships next to the font files.
Part 5 downloads the woff2 files into the site's assets and serves them from the
same origin; no call to any font CDN. JetBrains Mono (also OFL-1.1, verified)
stays out to keep the family count at two; tabular figures come from Inter's
font-feature-settings.
