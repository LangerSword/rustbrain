// Flow definitions for the rustbrain demo footage. Real site, real repo, real
// run page. A visible cursor dot follows the mouse; moves are eased and
// human-speed. Used by capture_site_xvfb.mjs (headed chrome under Xvfb).
export const CURSOR_JS = `
(() => {
  const add = () => {
    if (!document.body || document.getElementById("__vid_cursor")) return;
    const d = document.createElement("div"); d.id = "__vid_cursor";
    d.style.left = Math.round(window.innerWidth / 2) + "px";
    d.style.top = Math.round(window.innerHeight * 0.62) + "px";
    const style = document.createElement("style");
    style.textContent = \`
      html, body, * { cursor: none !important; }
      #__vid_cursor { position: fixed; left: 0; top: 0; width: 18px; height: 18px;
        border: 2px solid #ff6a3d; border-radius: 50%;
        background: rgba(255,106,61,0.22); box-shadow: 0 0 0 1px rgba(0,0,0,0.35);
        pointer-events: none; z-index: 2147483647; }
      #__vid_cursor.__click { transform: scale(0.72); transition: transform 110ms ease-out; }
    \`;
    document.head.appendChild(style);
    document.body.appendChild(d);
    window.addEventListener("mousemove", (e) => {
      d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px";
      d.classList.remove("__click");
    }, { passive: true });
    window.addEventListener("mousedown", () => d.classList.add("__click"));
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", add);
  else add();
})();
`;

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export async function easedMove(page, to, ms = 900) {
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

async function settle(page, ms = 1500) {
  await page.waitForLoadState("networkidle").catch(() => {});
  await sleep(ms);
}

const BASE = process.env.BASE_URL || "http://rustbrain.langersword.in/";

export async function flowHero(page) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await settle(page, 2400);
  await easedMove(page, { x: 960, y: 420 }, 700);
  await easedMove(page, await center(page, "#demo"), 1100);
  await sleep(1500);
  await easedMove(page, { x: 640, y: 760 }, 900);
  await sleep(800);
}

export async function flowSuccessorEdge(page) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await settle(page, 2200);
  await easedMove(page, { x: 760, y: 860 }, 900);
  const fig = await page.locator("figure.graph svg").first().boundingBox();
  if (!fig) throw new Error("graph svg not found");
  const sx = fig.width / 520, sy = fig.height / 302;
  const label = { x: fig.x + 280 * sx, y: fig.y + 40 * sy };
  await easedMove(page, label, 1400);
  await sleep(2000);
  await page.mouse.move(label.x + 3, label.y + 1);
  await sleep(700);
  await page.mouse.move(label.x - 2, label.y + 2);
  await sleep(1000);
}

export async function flowTabs(page) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await settle(page, 2200);
  const cargo = await center(page, ".demo-tabs button[data-target='T-cargo']");
  await easedMove(page, cargo, 800);
  await page.mouse.click(cargo.x, cargo.y);
  await sleep(2100);
  const dev = await center(page, ".demo-tabs button[data-target='T-dev-tools']");
  await easedMove(page, dev, 800);
  await page.mouse.click(dev.x, dev.y);
  await sleep(2400);
  const libs = await center(page, ".demo-tabs button[data-target='libs-api']");
  await easedMove(page, libs, 800);
  await page.mouse.click(libs.x, libs.y);
  await sleep(1400);
}

export async function flowGaps(page) {
  await page.goto(BASE + "gaps/", { waitUntil: "domcontentloaded" });
  await settle(page, 2000);
  await easedMove(page, { x: 960, y: 500 }, 700);
  await page.evaluate(() => window.scrollTo({ top: 620, behavior: "smooth" }));
  await sleep(1800);
  await page.locator("h2", { hasText: "tier 3" }).first().scrollIntoViewIfNeeded().catch(() => {});
  await sleep(2400);
}

export async function flowBugs(page) {
  await page.goto(BASE + "bugs/", { waitUntil: "domcontentloaded" });
  await settle(page, 2000);
  await page.evaluate(() => window.scrollTo({ top: window.innerHeight * 1.15, behavior: "smooth" }));
  await sleep(1700);
  await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight * 0.8, behavior: "smooth" }));
  await sleep(2000);
}

export async function flowReadme(page) {
  await page.goto("https://github.com/LangerSword/rustbrain", { waitUntil: "domcontentloaded" });
  await settle(page, 2600);
  await page.locator("h2", { hasText: "Graph data model" }).first()
    .scrollIntoViewIfNeeded().catch(async () => {
      await page.evaluate(() => window.scrollTo({ top: 1200, behavior: "smooth" }));
    });
  await sleep(2600);
}

export async function flowActions(page, runUrl) {
  await page.goto(runUrl || "https://github.com/LangerSword/rustbrain/actions/workflows/ci.yml",
                  { waitUntil: "domcontentloaded" });
  await settle(page, 2600);
  await page.evaluate(() => window.scrollTo({ top: 430, behavior: "smooth" }));
  await sleep(2400);
}

export const FLOWS = {
  fhd: [
    ["hero", (p) => flowHero(p)],
    ["successor_edge", (p) => flowSuccessorEdge(p)],
    ["tabs", (p) => flowTabs(p)],
    ["gaps", (p) => flowGaps(p)],
    ["bugs", (p) => flowBugs(p)],
    ["readme", (p) => flowReadme(p)],
    ["actions", (p, r) => flowActions(p, r)],
  ],
  uhd: [
    ["hero", (p) => flowHero(p)],
    ["successor_edge", (p) => flowSuccessorEdge(p)],
    ["gaps", (p) => flowGaps(p)],
    ["bugs", (p) => flowBugs(p)],
    ["readme", (p) => flowReadme(p)],
  ],
};
