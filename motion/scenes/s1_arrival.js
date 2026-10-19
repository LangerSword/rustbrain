// Scene 1, arrival: RFC 1892 card and its label, masked line reveals.
// Every element here is complete static HTML first; this module only adds the
// reveal. The parent matches out/revamp/20_REVAMP.md, scene 1.
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

  const tl = gsap.timeline({
    defaults: { ease: E.arrive },
    scrollTrigger: { trigger: root, start: "top 70%", toggleActions: "play none none none" },
  });
  tl.from(
    splits.flatMap((s) => s.lines),
    { yPercent: 112, duration: D.reveal, stagger: ST.line },
    0
  )
    .from(root.querySelectorAll(".reveal-soft"), { opacity: 0, y: 14, duration: D.quote, stagger: ST.line, ease: E.ui }, 0.2)
    .from(root.querySelector(".rfc-card"), { opacity: 0, y: 26, duration: 0.7 }, 0.3);

  register("s1", tl);
  return () => {
    splits.forEach((s) => s.revert());
  };
}
