// Scenes 2 and 3 share one pinned stage: the dead end, then the hop.
// Statically the stage shows the final state (the hop done, 37 reviewers).
// With motion, the scrubbed timeline opens on the dead-end state (0 current
// members, empty fan, no edge) and plays the hop as the reader scrolls.
// Parent: out/revamp/20_REVAMP.md, scenes 2 and 3.
import { E, D, ST, SCRUB } from "../tokens.js";

export function build(api, ctx, register) {
  const { gsap } = api;
  const root = document.querySelector("#s2");
  if (!root) return () => {};

  const isDesktop = !!(ctx.conditions && ctx.conditions.desktop);
  // Desktop pins the stage (1.5vh dead end + 2.5vh hop). Mobile gets a
  // lighter timeline: the same beats, scrubbed across the section, no pin.
  const stConfig = isDesktop
    ? {
        trigger: root,
        start: "top top",
        end: "+=400%",
        pin: true,
        scrub: SCRUB.hop,
        anticipatePin: 1,
        invalidateOnRefresh: true, // pin length stays right when fonts or resize change layout
      }
    : {
        trigger: root,
        start: "top 72%",
        end: "bottom 60%",
        scrub: 0.5,
        invalidateOnRefresh: true,
      };

  const q = (sel) => root.querySelector(sel);
  const fan = root.querySelectorAll(".rnode");
  const edge = q("#edgePath");
  const quote = q("#edgeQuote");
  const rows = root.querySelectorAll(".reviewers tbody tr");
  const countEl = q("#rosterCount");
  const resultBox = q("#demo");
  const counter = { v: 0 };

  // The story starts at the dead end: archived, nobody left. These start
  // states are set once; the scrubbed timeline below releases them.
  // The result box belongs to the hop beat, so it stays out of the way
  // (opacity only, no layout change) until the edge has drawn. A small
  // motion-only note explains the empty space while the dead end holds.
  gsap.set(fan, { opacity: 0, y: -8 });
  gsap.set(rows, { opacity: 0 });
  if (resultBox) gsap.set(resultBox, { opacity: 0 });
  if (countEl) countEl.textContent = "0";
  const deadNote = document.createElement("p");
  deadNote.className = "dead-note mono-label";
  deadNote.textContent = "no reviewers to show: the archived team has none today.";
  if (resultBox && resultBox.parentNode) resultBox.parentNode.insertBefore(deadNote, resultBox);

  const tl = gsap.timeline({
    defaults: { ease: E.arrive },
    scrollTrigger: {
      ...stConfig,
      // the rail follows the beat: 02 while the dead end holds, 03 once the
      // hop is playing (the stage is one section with two beats)
      onUpdate: (self) => {
        const on = self.progress > 0.42;
        document.querySelectorAll(".scene-rail a").forEach((a) => {
          a.classList.toggle("on", a.getAttribute("href") === (on ? "#s3" : "#s2"));
        });
      },
    },
  });

  tl.addLabel("dead")
    .from(q(".dead-chip"), { opacity: 0, y: 12, duration: 0.5 }, 0.1)
    .to(q(".dead-chip"), { scale: 1.03, duration: 0.4, yoyo: true, repeat: 1, ease: E.ui }, 0.6)
    .addLabel("hop", 1.2)
    .from(edge, { drawSVG: "0%", duration: D.draw, ease: "none" }, "hop")
    .to(fan, { opacity: 1, y: 0, duration: 0.5, stagger: ST.fan }, "hop+=0.25")
    .from(quote, { yPercent: 112, duration: D.quote }, "hop+=0.8")
    .to(
      counter,
      {
        v: 37,
        duration: 0.8,
        ease: E.ui,
        snap: { v: 1 },
        onUpdate() {
          if (countEl) countEl.textContent = String(Math.round(counter.v));
        },
      },
      "hop+=0.9"
    )
    .from(rows, { opacity: 0, y: 14, duration: D.rowIn, stagger: ST.row }, "hop+=1.05")
    .to(deadNote, { opacity: 0, duration: 0.5, ease: E.ui }, "hop+=1.05")
    .to(resultBox, { opacity: 1, duration: 0.5, ease: E.ui }, "hop+=1.35")
    .to({}, { duration: 0.35 });

  register("s23", tl);
  return () => {
    // Start states were set on shared DOM (fan, rows, counter, result box). On
    // cleanup (media change), restore the static final state.
    gsap.set(fan, { clearProps: "opacity,transform" });
    gsap.set(rows, { clearProps: "opacity,transform" });
    if (resultBox) gsap.set(resultBox, { clearProps: "opacity" });
    if (countEl) {
      countEl.textContent = countEl.dataset.final || "37";
    }
    if (deadNote.parentNode) deadNote.parentNode.removeChild(deadNote);
  };
}
