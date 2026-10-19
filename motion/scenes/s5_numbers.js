// Scene 5, the numbers: counters to their final values and the three tiers.
// Every final value lives in data-final on the element AND as its text, both
// read from site/data.json at build time and checked by scripts/assert_site_numbers.py.
// Parent: out/revamp/20_REVAMP.md, scene 5.
import { E, D, ST } from "../tokens.js";

function fmt(v) {
  return Number.isInteger(v) ? String(v) : v.toFixed(1);
}

export function build(api, ctx, register) {
  const { gsap } = api;
  const root = document.querySelector("#s5");
  if (!root) return () => {};

  const tl = gsap.timeline({
    defaults: { ease: E.ui },
    scrollTrigger: { trigger: root, start: "top 65%", toggleActions: "play none none none" },
  });

  // counters, staggered by tier order
  let t = 0;
  root.querySelectorAll(".count").forEach((el) => {
    const end = parseFloat(el.getAttribute("data-final"));
    if (!Number.isFinite(end)) return;
    const o = { v: 0 };
    tl.to(
      o,
      {
        v: end,
        duration: D.count,
        snap: Number.isInteger(end) ? { v: 1 } : { v: 0.1 },
        onUpdate() {
          el.textContent = fmt(o.v);
        },
      },
      t
    );
    t += ST.tier;
  });

  tl.from(root.querySelectorAll(".tier"), { opacity: 0, y: 18, duration: 0.6, stagger: ST.tier, ease: E.arrive }, 0.05)
    .from(
      root.querySelectorAll(".tier-bar-fill"),
      { scaleX: 0, transformOrigin: "0 50%", duration: 0.9, stagger: ST.tier, ease: E.arrive },
      0.15
    );

  register("s5", tl);
  return () => {
    // restore final text if a revert happens mid-count
    root.querySelectorAll(".count").forEach((el) => {
      el.textContent = el.getAttribute("data-final");
    });
  };
}
