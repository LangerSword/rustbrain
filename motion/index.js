// Motion entry. Builds every scene inside gsap.matchMedia, so reduced motion
// gets the static final states with no pins, no scrub and no SplitText work,
// and every scene reverts on media change or resize. The debug registry
// (window.rbDebug) is what site/debug/ scrubs.
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { Flip } from "gsap/Flip";
import { E, D } from "./tokens.js";
import * as s1 from "./scenes/s1_arrival.js";
import * as s23 from "./scenes/s23_route.js";
import * as s4 from "./scenes/s4_gap.js";
import * as s5 from "./scenes/s5_numbers.js";
import * as s6 from "./scenes/s6_close.js";
import * as fx from "./scenes/transitions.js";

gsap.registerPlugin(ScrollTrigger, SplitText, DrawSVGPlugin, Flip);

// the title-sequence CSS gate can stand down as soon as the bundle runs
document.documentElement.classList.add("fx-ready");

const api = { gsap, ScrollTrigger, SplitText, DrawSVGPlugin, Flip };

// debug registry for site/debug/: timelines by scene, plus live triggers
const debug = { scenes: {}, triggers: () => ScrollTrigger.getAll() };
window.rbDebug = debug;
const register = (name, tl) => {
  debug.scenes[name] = tl;
};

function setRail(id) {
  document.querySelectorAll(".scene-rail a").forEach((a) => {
    a.classList.toggle("on", a.getAttribute("href") === "#" + id);
  });
}

const mm = gsap.matchMedia();

mm.add(
  {
    reduce: "(prefers-reduced-motion: reduce)",
    desktop: "(prefers-reduced-motion: no-preference) and (min-width: 960px)",
    mobile: "(prefers-reduced-motion: no-preference) and (max-width: 959px)",
  },
  (ctx) => {
    if (ctx.conditions.reduce) {
      // nothing to build: the static HTML already shows every final state
      return;
    }
    const cleanups = [];
    cleanups.push(s1.build(api, ctx, register));
    cleanups.push(s23.build(api, ctx, register));
    cleanups.push(s4.build(api, ctx, register));
    cleanups.push(s5.build(api, ctx, register));
    cleanups.push(s6.build(api, ctx, register));
    cleanups.push(fx.build(api, ctx, register));

    // scene rail state
    document.querySelectorAll("main .scene").forEach((sec) => {
      ScrollTrigger.create({
        trigger: sec,
        start: "top 45%",
        end: "bottom 45%",
        onToggle: (self) => {
          if (self.isActive) setRail(sec.id);
        },
      });
    });

    // Flip: the result panel re-groups when the demo target changes, instead
    // of hard-switching. site.js stays the fallback renderer (no GSAP path).
    const tabs = document.querySelectorAll(".demo-tabs button[data-target]");
    const onClick = (ev) => {
      const btn = ev.currentTarget;
      if (!window.RB || !window.RB.render) return;
      ev.stopImmediatePropagation();
      const target = btn.getAttribute("data-target");
      const box = document.querySelector("#demo");
      gsap.set(box, { opacity: 1 }); // a tab click is an explicit request to see the result
      const state = box ? Flip.getState(box) : null;
      Promise.resolve(window.RB.render(target)).then(() => {
        if (state && box) {
          Flip.from(state, {
            duration: D.flip,
            ease: E.ui,
            scale: true,
            absolute: true,
            onEnter: (els) => gsap.fromTo(els, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: E.ui }),
            onLeave: (els) => gsap.to(els, { opacity: 0, duration: 0.15, ease: E.leave }),
          });
        }
      });
    };
    tabs.forEach((b) => b.addEventListener("click", onClick, true));
    cleanups.push(() => tabs.forEach((b) => b.removeEventListener("click", onClick, true)));

    return () => cleanups.forEach((fn) => fn());
  }
);

// pins measure layout; fonts and full load change layout, so re-measure after both
if (document.fonts && document.fonts.ready) {
  document.fonts.ready.then(() => ScrollTrigger.refresh());
}
window.addEventListener("load", () => ScrollTrigger.refresh());
