# Patterns across the eight sites (Part 2.4)

Sources: the eight teardowns in `out/design/teardowns/` (linear.app, vercel.com,
stripe.com, resend.com, supabase.com, fly.io, pudding.cool,
informationisbeautiful.net), all measured live on 2026-10-19 and spot-checked.

## Patterns that recur

1. **The fold carries proof.** Every developer site puts a product artifact inside
   the first viewport: Linear's app capture starts at y=485 of 900; Supabase's
   bento cards are cut by the fold; Stripe states promise with art plus a logo
   band; Vercel renders a full-bleed canvas. Only the two editorial sites open
   with type alone.
2. **One accent, spent only on actions.** Linear #5E6AD2, Stripe #533AFD, Fly
   #7C3AED, Supabase green oklch(0.525 0.12 157.5), IiB pink #F06292. Hierarchy
   elsewhere comes from three grey tiers on one surface (Linear: #F7F8F8 /
   #8A8F98 / #D0D6E0 on #08090A), not from hue.
3. **Two type roles, tight tracking at display sizes.** Display plus UI face at
   most (Resend: serif + grotesque + mono for code; Pudding: serif display +
   grotesk + mono microlabels). Negative tracking scales with size (Resend
   -0.96px at 96, -2.8px at 56; Linear -1.408px at 64). Mono is functional
   (serial numbers, code) when it appears.
4. **Rhythm from hairlines and one dark band.** Supabase splits nine sections
   with 8 percent hairlines and no shadows; Stripe interrupts an all-white page
   with one navy band carrying three big numbers; Fly uses a constant 96px
   bottom pad with no top pad so content sets the cadence.
5. **Motion is quiet and budgeted.** Pudding runs transform-only transitions at
   0.2s and 0.25s ease, nothing on load, one prefers-reduced-motion rule.
   Nothing on load anywhere except product demos; several teardowns flag
   unreadable cross-origin stylesheets as a limit, so this is a floor.
6. **Weight is where they stopped caring.** Vercel ships 2.1 MB of JS in a
   2.76 MB page, Resend 2.98 MB of JS in 6.3 MB, Stripe 1.16 MB of JS.
   Pudding's index is 67 KB of JS; IiB's measurable subset is 8 KB. A fast data
   page here is a differentiator, not a compromise.

## Overused or generic (do not reuse)

- Logo strips directly under the hero (Linear, Stripe, Supabase, and Fly's word
  rows): trust filler as a default band. Six of eight sites.
- Bento grids as the default feature shape (Stripe, Supabase).
- The dark hero with promo pill, aspirational two-liner and two CTAs (Resend
  names it as the default developer-tool opener).
- Mono labels as decoration-free developer signalling (Vercel) without a
  functional reason.
- Hero art as gradient or anthropomorphic characters (Fly, Stripe).
- Fixed blurred top bars (Linear) and animated colour-cycling text (Stripe's
  measured 2.39:1 contrast failure).
- Card art as story screenshots or background images (Pudding spends 4.2 MB; IiB
  ships charts as background-image with no alt text).
- Dateable proofs (Supabase's GitHub star count in the nav).

## Five most transferable ideas for a data-product site, ranked

1. **Real data in the fold.** Linear's product-in-fold becomes rustbrain's live
   route for RFC 1892 (T-libs-api through SUCCEEDED_BY to 37 reviewers) rendered
   from the real snapshot, plus the graph as inline SVG, not an illustration.
2. **One accent for actions, three grey tiers on one dark surface.** Steal the
   economy, not the palette: rustbrain's accent fires only on links, focused
   controls and the successor hop; structure comes from rules and type.
3. **Type-only hero, numbers band as the only loud surface.** IiB's text hero
   plus Stripe's numbers band: 761 RFCs, 162 routing-only-through-the-hop, 138
   and 24 by team, 25 true-gap RFCs, each with scope on the same line.
4. **Editorial index rows with functional mono microlabels.** Pudding's serial
   plus date over each title, minus its art: rustbrain's RFC examples and gap
   table carry number, date and tier as real text, copyable and accessible.
5. **Budgets as design.** Transform-only 0.2s motion, one reduced-motion rule,
   near-zero JS until interaction, total JS under 150 KB, stated beside the
   measured weight of the sites it learned from.
