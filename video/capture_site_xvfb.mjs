// Drive the headed Chromium (started under Xvfb by capture_site_xvfb.sh) over
// CDP and record each flow with ffmpeg x11grab at 60 fps, one mp4 per clip.
import { chromium } from "playwright-core";
import { spawn, execSync } from "node:child_process";
import path from "node:path";
import fs from "node:fs";
import { FLOWS, CURSOR_JS, sleep } from "./flows.mjs";

const MODE = process.argv[2] === "uhd" ? "uhd" : "fhd";
const DISP = process.argv[3] || ":96";
const RAW = process.argv[4];
const W = process.argv[5] || "1920";
const H = process.argv[6] || "1080";
const BAR = parseInt(process.argv[7] || "0", 10);
const RUN_URL = process.env.RUN_URL || "";
const CDP_PORT = process.env.CDP_PORT || "9222";

fs.mkdirSync(RAW, { recursive: true });
const browser = await chromium.connectOverCDP("http://127.0.0.1:" + CDP_PORT);
const ctx = browser.contexts()[0];
const page = ctx.pages()[0] || (await ctx.newPage());
await page.addInitScript({ content: CURSOR_JS });

for (const [name, fn] of FLOWS[MODE]) {
  const out = path.join(RAW, name + ".mp4");
  console.log("=== recording", MODE, name, "->", out);
  const ff = spawn("ffmpeg", [
    "-hide_banner", "-loglevel", "error", "-y",
    "-f", "x11grab", "-framerate", "60", "-video_size", `${W}x${H}`,
    "-draw_mouse", "0", "-i", `${DISP}+0,${BAR}`,
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", out,
  ], { stdio: "ignore" });
  await sleep(1800);
  await fn(page, RUN_URL).catch((e) => console.log("flow error:", String(e).slice(0, 120)));
  await sleep(900);
  ff.kill("SIGINT");
  await new Promise((r) => ff.on("close", r));
  // execSync here is a fixed ffprobe invocation; `out` is built from our own
  // RAW dir plus the clip names in FLOWS, never from user input.
  const probe = execSync(
    `ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate,nb_frames -show_entries format=duration -of csv=p=0 "${out}"`
  ).toString().trim().split("\n").join(" ");
  console.log("CLIP", name, probe);
}
await browser.close();
console.log("done", MODE);
