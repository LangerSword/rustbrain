// Cinematic staging: the veil that lifts off each scene as it enters, the
// top progress hairline, and light parallax on scene furniture. Motion-only;
// reduced motion never builds this (matchMedia gate in index.js), and no-JS
// pages never see a curtain because they are created here.
import { E, D } from "../tokens.js";

export function build(api, ctx, register) {
  const { gsap, ScrollTrigger } = api;
  const cleanups = [];

  // top progress hairline: one scrub across the whole document
  const bar = document.createElement("div");
  bar.className = "progress-rail";
  bar.setAttribute("aria-hidden", "true");
  document.body.appendChild(bar);
  gsap.to(bar, {
    scaleX: 1,
    ease: "none",
    scrollTrigger: { trigger: document.documentElement, start: "top top", end: "bottom bottom", scrub: 0.3 },
  });
  cleanups.push(() => bar.remove());

  // scene veils: every scene after the first is covered, then unveiled
  document.querySelectorAll("main .scene").forEach((sec) => {
    if (sec.id === "s1") return;
    const curtain = document.createElement("div");
    curtain.className = "curtain";
    curtain.setAttribute("aria-hidden", "true");
    sec.appendChild(curtain);
    ScrollTrigger.create({
      trigger: sec,
      start: "top 85%",
      once: true,
      onEnter: () => {
        gsap.to(curtain, {
          yPercent: -101,
          duration: D.curtain,
          ease: "expo.inOut",
          onComplete: () => curtain.remove(),
        });
        // the shared stage headline gets its own small entrance; scenes with
        // their own reveal timelines keep them (no double reveals)
        if (sec.id === "s2") {
          gsap.from(sec.querySelectorAll(".stage-left > h2"), { opacity: 0, y: 20, duration: 0.7, ease: E.arrive, delay: 0.15 });
        }
      },
    });
    cleanups.push(() => curtain.remove());
  });

  // light parallax on the kicker lines and figures (transform only)
  document.querySelectorAll("main .scene").forEach((sec) => {
    const kick = sec.querySelector(".mono-label");
    if (kick) {
      gsap.fromTo(kick, { yPercent: -20 }, {
        yPercent: 0, ease: "none",
        scrollTrigger: { trigger: sec, start: "top bottom", end: "top 40%", scrub: true },
      });
    }
    const fig = sec.querySelector("figure");
    if (fig) {
      gsap.fromTo(fig, { yPercent: 7 }, {
        yPercent: 0, ease: "none",
        scrollTrigger: { trigger: sec, start: "top bottom", end: "center center", scrub: true },
      });
    }
  });

  return () => cleanups.forEach((fn) => fn());
}
