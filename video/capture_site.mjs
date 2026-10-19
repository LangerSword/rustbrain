// Real-footage capture for the rustbrain demo video.
// Opens the LIVE site in Chrome for Testing via playwright-core, records the
// Chrome DevTools screencast frame by frame, moves a visible injected cursor at
// human speed with easing, and writes numbered jpg frames plus a meta.json per
// clip. No mocks: every pixel is the real site, the real repo, the real run.
//
// Usage:
//   node video/capture_site.mjs fhd       1920x1080, all clips
//   node video/capture_site.mjs uhd       3840x2160 (DSF 2), punch clips only
// Env:
//   RUN_URL   a real GitHub Actions run page (default: the ci workflow page)
import { chromium } from "playwright-core";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const MODE = process.argv[2] === "uhd" ? "uhd" : "fhd";
const DSF = MODE === "uhd" ? 2 : 1;
const VW = 1920, VH = 1080;
const BASE = "https://langersword.github.io/rustbrain/";
const RUN_URL = process.env.RUN_URL || "https://github.com/LangerSword/rustbrain/actions/workflows/ci.yml";
const OUT = path.join(ROOT, "out", "video", "raw", "site_" + MODE);
const CHROME = process.env.HOME + "/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2); // easeInOutCubic

const CURSOR_CSS = `
html, body, * { cursor: none !important; }
#__vid_cursor { position: fixed; left: 0; top: 0; width: 18px; height: 18px;
  border: 2px solid #ff6a3d; border-radius: 50%;
  background: rgba(255,106,61,0.22); box-shadow: 0 0 0 1px rgba(0,0,0,0.35);
  pointer-events: none; z-index: 2147483647; transform: translate(-1px,-1px); }
#__vid_cursor.__click { transform: scale(0.7); transition: transform 120ms ease-out; }
`;
const CURSOR_JS = `
(() => {
  const add = () => {
    if (!document.body || document.getElementById("__vid_cursor")) return;
    const d = document.createElement("div"); d.id = "__vid_cursor";
    document.body.appendChild(d);
    window.addEventListener("mousemove", (e) => {
      d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px";
    }, { passive: true });
    window.addEventListener("mousedown", () => d.classList.add("__click"));
    window.addEventListener("mouseup", () => d.classList.remove("__click"));
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add);
  else add();
})();
`;

function framesDir(clip) {
  const d = path.join(OUT, clip);
  fs.mkdirSync(d, { recursive: true });
  return d;
}

async function recordClip(browser, clip, fn) {
  const ctx = await browser.newContext({
    viewport: { width: VW, height: VH }, deviceScaleFactor: DSF,
    reducedMotion: "no-preference",
  });
  await ctx.addInitScript({ content: CURSOR_JS });
  const page = await ctx.newPage();
  const session = await ctx.newCDPSession(page);
  const dir = framesDir(clip);
  const stamps = [];
  let n = 0;
  session.on("Page.screencastFrame", (f) => {
    const file = path.join(dir, "frame_" + String(++n).padStart(6, "0") + ".jpg");
    fs.writeFileSync(file, Buffer.from(f.data, "base64"));
    stamps.push(f.metadata.timestamp);
    session.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
  });
  await session.send("Page.startScreencast", {
    format: "jpeg", quality: 82, maxWidth: VW * DSF, maxHeight: VH * DSF, everyNthFrame: 1,
  });
  const t0 = Date.now();
  try { await fn(page); } finally {
    await session.send("Page.stopScreencast").catch(() => {});
    const secs = (Date.now() - t0) / 1000;
    const fps = stamps.length && stamps.length > 1 ? stamps.length / (stamps[stamps.length - 1] - stamps[0]) : 0;
    fs.writeFileSync(path.join(dir, "meta.json"), JSON.stringify({
      clip, mode: MODE, viewport: VW + "x" + VH, dsf: DSF, frames: stamps.length,
      wall_seconds: Math.round(secs * 100) / 100,
      measured_fps: Math.round(fps * 100) / 100,
      first_ts: stamps[0] || null, last_ts: stamps[stamps.length - 1] || null,
    }, null, 1));
    console.log("CLIP %s frames=%d fps=%s secs=%s", clip, stamps.length,
      Math.round(fps * 100) / 100, Math.round(secs * 100) / 100);
    await ctx.close();
  }
}

async function easedMove(page, to, ms = 900) {
  const from = await page.evaluate(() => {
    const c = document.getElementById("__vid_cursor");
    return c ? { x: parseFloat(c.style.left) || 960, y: parseFloat(c.style.top) || 540 } : { x: 960, y: 540 };
  });
  const steps = Math.max(20, Math.round(ms / 16));
  for (let i = 1; i <= steps; i++) {
    const t = ease(i / steps);
    await page.mouse.move(from.x + (to.x - from.x) * t, from.y + (to.y - from.y) * t);
    await sleep(ms / steps);
  }
}

async function center(page, sel) {
  const box = await page.locator(sel).first().boundingBox();
  if (!box) throw new Error("no box for " + sel);
  return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
}

async function settle(page, ms = 1500) { await page.waitForLoadState("networkidle").catch(() => {}); await sleep(ms); }

async function flowHero(page) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await settle(page, 2200);
  await easedMove(page, { x: 960, y: 420 }, 700);
  await easedMove(page, await center(page, "#demo"), 1100);
  await sleep(1400);
  await easedMove(page, { x: 620, y: 700 }, 900);
  await sleep(700);
}

async function flowSuccessorEdge(page) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await settle(page, 2000);
  const fig = await page.locator("figure.graph svg").first().boundingBox();
  if (!fig) throw new Error("graph svg not found");
  const sx = fig.width / 520, sy = fig.height / 302;
  const label = { x: fig.x + 280 * sx, y: fig.y + 40 * sy };
  await easedMove(page, label, 1200);
  await sleep(1600);
  await page.mouse.move(label.x + 3, label.y + 1);
  await sleep(600);
  await page.mouse.move(label.x - 2, label.y + 2);
  await sleep(900);
}

async function flowTabs(page) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await settle(page, 2000);
  await easedMove(page, await center(page, ".demo-tabs button[data-target='T-cargo']"), 800);
  await page.mouse.click(...Object.values(await center(page, ".demo-tabs button[data-target='T-cargo']")));
  await sleep(1500);
  const dev = await center(page, ".demo-tabs button[data-target='T-dev-tools']");
  await easedMove(page, dev, 700);
  await page.mouse.click(dev.x, dev.y);
  await sleep(1900);
  const libs = await center(page, ".demo-tabs button[data-target='libs-api']");
  await easedMove(page, libs, 700);
  await page.mouse.click(libs.x, libs.y);
  await sleep(1100);
}

async function flowGaps(page) {
  await page.goto(BASE + "gaps/", { waitUntil: "domcontentloaded" });
  await settle(page, 1800);
  await easedMove(page, { x: 960, y: 500 }, 700);
  await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight * 0.55, behavior: "smooth" }));
  await sleep(1600);
  await page.locator("h2", { hasText: "tier 3" }).first().scrollIntoViewIfNeeded().catch(() => {});
  await sleep(2000);
}

async function flowBugs(page) {
  await page.goto(BASE + "bugs/", { waitUntil: "domcontentloaded" });
  await settle(page, 1800);
  await page.evaluate(() => window.scrollTo({ top: window.innerHeight * 1.2, behavior: "smooth" }));
  await sleep(1500);
  await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight * 0.82, behavior: "smooth" }));
  await sleep(1800);
}

async function flowReadme(page) {
  await page.goto("https://github.com/LangerSword/rustbrain", { waitUntil: "domcontentloaded" });
  await settle(page, 2500);
  await page.locator("h2", { hasText: "Graph data model" }).first()
    .scrollIntoViewIfNeeded().catch(async () => {
      await page.evaluate(() => window.scrollTo({ top: 1200, behavior: "smooth" }));
    });
  await sleep(2600);
}

async function flowActions(page) {
  await page.goto(RUN_URL, { waitUntil: "domcontentloaded" });
  await settle(page, 2500);
  await page.evaluate(() => window.scrollTo({ top: 400, behavior: "smooth" }));
  await sleep(2200);
}

const FHD_FLOWS = [
  ["hero", flowHero], ["successor_edge", flowSuccessorEdge], ["tabs", flowTabs],
  ["gaps", flowGaps], ["bugs", flowBugs], ["readme", flowReadme], ["actions", flowActions],
];
const UHD_FLOWS = [
  ["hero", flowHero], ["successor_edge", flowSuccessorEdge],
  ["gaps", flowGaps], ["bugs", flowBugs], ["readme", flowReadme],
];

const browser = await chromium.launch({
  headless: true, executablePath: CHROME,
  args: ["--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-color-profile=srgb"],
});
for (const [name, fn] of (MODE === "uhd" ? UHD_FLOWS : FHD_FLOWS)) {
  console.log("=== recording", MODE, name);
  await recordClip(browser, name, fn);
}
await browser.close();
console.log("done", MODE);
