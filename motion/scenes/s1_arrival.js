// Scene 1, arrival: a title sequence, not a scroll reveal. On load (motion
// allowed), the kicker fades, the hairline draws, the headline lines rise out
// of their masks and the RFC card settles in, one family of curves. With no
// JavaScript or reduced motion, the static page is already the final state.
import { E, D, ST } from "../tokens.js";

export function build(api, ctx, register) {
  const { gsap, SplitText } = api;
  const root = document.querySelector("#s1");
  if (!root) return () => {};

  const splits = [];
  root.querySelectorAll(".reveal-line").forEach((el) => {
    // SplitText output keeps an accessible name: aria "auto" labels the parent
    // and hides the generated spans from assistive tech.
    const split = new SplitText(el, { type: "lines", linesClass: "mv-line", aria: "auto" });
    splits.push(split);
    split.lines.forEach((line) => {
      // Wrap each line so the reveal has an overflow mask to rise out of.
      const mask = document.createElement("span");
      mask.className = "mv-mask";
      line.parentNode.insertBefore(mask, line);
      mask.appendChild(line);
    });
  });

  const tl = gsap.timeline({ defaults: { ease: E.arrive }, delay: 0.15 });
  tl.from(root.querySelector(".kicker"), { opacity: 0, y: 10, duration: 0.5, ease: E.ui }, 0)
    .from(root.querySelector(".s1-hair"), { scaleX: 0, duration: 0.9, ease: E.ui }, 0.2)
    .from(splits.flatMap((s) => s.lines), { yPercent: 112, duration: D.reveal, stagger: ST.line }, 0.35)
    .from(root.querySelector(".rfc-card"), { opacity: 0, y: 30, duration: 0.8 }, 0.9)
    .from(root.querySelector(".cta-row"), { opacity: 0, y: 12, duration: D.quote, ease: E.ui }, 1.05);

  // the card drifts up slightly as the hero leaves (depth, not decoration)
  gsap.to(root.querySelector(".rfc-card"), {
    yPercent: -6,
    ease: "none",
    scrollTrigger: { trigger: root, start: "top top", end: "bottom top", scrub: true },
  });

  register("s1", tl);
  return () => {
    splits.forEach((s) => s.revert());
  };
}
