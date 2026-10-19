# Stage 1: legal and licence first

All fetches 2026-10-19 with a plain curl user agent,
`rustbrain-study/1.0 (study; contact github LangerSword/rustbrain)`.
One request at a time, no crawling.

## 1.1 santionispirits.com: robots.txt and terms, read before loading

robots.txt, https://santionispirits.com/robots.txt, HTTP 200, 23 bytes. The
whole file, quoted:

```
User-agent: *
Allow: /
```

Automated access is allowed for all user agents. No paths are disallowed.

Terms of use: the site serves one identical JS shell for every route
(homepage and `/policies/terms-of-service` are byte-identical, 32519 bytes,
md5 `ec553ad53c5bf0ac5c87ce2ecff42eb7`; "terms" and "legal" appear zero times
in the shell), so no server-rendered terms page exists. The shell's own data
payload links the brand's legal document: a privacy policy PDF on
`cdn.sanity.io` (path hash `d2513cb8...`, linked from the site's own
`assets/data` JSON), fetched once and read. Its "TERMS OF USE" section,
quoted:

- "By accessing this website, you agree to do so responsibly and in
  accordance with applicable alcohol beverage laws and regulations in your
  place of residence."
- "All content on this website ... is owned by or licensed to Santioni and
  may not be used without prior written consent."

No clause forbids automated access; robots allows all. The content-ownership
clause is the reason nothing from the site may be reused, which matches the
copy boundary below. No further terms-of-use page was found; the legal notice
quoted is the site's operative terms.

## 1.2 GSAP licence

Source: https://gsap.com/licensing, fetched 2026-10-19, page title "Standard
License - GSAP". Quotes:

- "GSAP is now free for everyone, thanks to Webflow's support!"
- Grant: "Webflow grants you a non-exclusive, worldwide license to use,
  reproduce, display, and implement GSAP Products solely for Permitted Uses."
- "Permitted Uses" means "the implementation and/or use of GSAP Products on
  any website, web application, or digital interface by any person or
  entity".
- Restrictions: no Prohibited Uses (tools that let users build visual
  animations without code that compete with Webflow's builder); no reverse
  engineering "for the purpose of creating Competitive Products"; no
  "Remove or alter any proprietary notices or branding from GSAP Products".
- FAQ: "All of GSAP including the plugins that were formerly members-only
  like SplitText and MorphSVG can be used in commercial projects at no
  charge." Effective 2025-04-30, last modified 2025-05-30.

Per plugin, for a public open-source repo and a public site (all promised by
the quotes above): ScrollTrigger allowed, SplitText allowed, DrawSVG allowed,
Flip allowed, MorphSVG allowed, ScrollSmoother allowed, Observer allowed,
MotionPathPlugin allowed, CustomEase allowed, core quickTo and matchMedia
allowed. Conditions kept: plugin copyright notices stay in whatever is
vendored or bundled, no animation-builder product, no competitive reverse
engineering. Nothing was unclear, so nothing is withheld; ScrollSmoother is
allowed but not currently planned (native scroll is a hard requirement).

npm verification: `npm install --save-exact gsap@3.15.0` in the repo root.
`node -e` check on 2026-10-19: version 3.15.0, and
ScrollTrigger.js, SplitText.js, DrawSVGPlugin.js, Flip.js, MorphSVGPlugin.js,
ScrollSmoother.js, Observer.js, MotionPathPlugin.js, CustomEase.js are all
present in `node_modules/gsap`. The version is pinned in package.json.

## 1.3 copy boundary, binding for all stages

Recorded from the live site: measurements only (durations, easings, staggers,
triggers, scroll lengths, layer order, plugin names, font family NAMES,
colour values). Mechanics are rewritten from scratch. Never copied or saved
into the repo: source code, shaders, copy text, images, video, icons, logos,
fonts, brand. Study screenshots live under `out/revamp/shots/` and are
gitignored. Nothing from the site's assets enters the repo. Any bundle or
page inspected during measurement is read for structure only; findings are
recorded as measurements, and no code is extracted or reused.
