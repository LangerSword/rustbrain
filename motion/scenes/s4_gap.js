// Scene 4, the gap: T-dev-tools finds no team and the route stops.
// The stub line is authored short in the SVG; drawing it fully IS the stop.
// Parent: out/revamp/20_REVAMP.md, scene 4.
import { E, D } from "../tokens.js";

export function build(api, ctx, register) {
  const { gsap } = api;
  const root = document.querySelector("#s4");
  if (!root) return () => {};

  const stub = root.querySelector("#stubPath");
  const tl = gsap.timeline({
    defaults: { ease: E.arrive },
    scrollTrigger: { trigger: root, start: "top 68%", toggleActions: "play none none none" },
  });

  tl.from(stub, { drawSVG: "0%", duration: D.stub, ease: "none" }, 0)
    .from(root.querySelectorAll(".gap-surface"), { opacity: 0, y: 16, duration: 0.6, stagger: 0.1 }, 0.15)
    .from(root.querySelector(".gap-label"), { opacity: 0, duration: 0.5, ease: E.ui }, 0.6);

  register("s4", tl);
  return () => {};
}
