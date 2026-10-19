// Scene 6, honesty and close: limits lines, links, snapshot hash.
// Parent: out/revamp/20_REVAMP.md, scene 6.
import { E, D, ST } from "../tokens.js";

export function build(api, ctx, register) {
  const { gsap, SplitText } = api;
  const root = document.querySelector("#s6");
  if (!root) return () => {};

  const splits = [];
  root.querySelectorAll(".reveal-line").forEach((el) => {
    const split = new SplitText(el, { type: "lines", linesClass: "mv-line", aria: "auto" });
    splits.push(split);
    split.lines.forEach((line) => {
      const mask = document.createElement("span");
      mask.className = "mv-mask";
      line.parentNode.insertBefore(mask, line);
      mask.appendChild(line);
    });
  });

  const tl = gsap.timeline({
    defaults: { ease: E.arrive },
    scrollTrigger: { trigger: root, start: "top 72%", toggleActions: "play none none none" },
  });
  tl.from(splits.flatMap((s) => s.lines), { yPercent: 112, duration: D.reveal, stagger: ST.line }, 0)
    .from(root.querySelectorAll(".reveal-soft"), { opacity: 0, y: 12, duration: D.quote, stagger: ST.line, ease: E.ui }, 0.2);

  register("s6", tl);
  return () => {
    splits.forEach((s) => s.revert());
  };
}
