// Bundles the motion layer into the static site. Two outputs:
//   site/assets/motion.js      the site bundle (minified, licence comments kept)
//   site/debug/motion-debug.js the debug page controller (readable)
// GSAP is bundled from the pinned npm package (gsap 3.15.0, package.json).
// The GSAP licence requires keeping copyright notices; esbuild legalComments
// "inline" keeps every @license banner in the output.
import { build } from "esbuild";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const common = {
  bundle: true,
  format: "iife",
  target: ["es2019"],
  logLevel: "info",
};

await build({
  ...common,
  entryPoints: [path.join(root, "motion/index.js")],
  outfile: path.join(root, "site/assets/motion.js"),
  minify: true,
  legalComments: "inline",
});

await build({
  ...common,
  entryPoints: [path.join(root, "motion/debug.js")],
  outfile: path.join(root, "site/debug/motion-debug.js"),
  minify: false,
});

console.log("motion bundles written to site/assets/motion.js and site/debug/motion-debug.js");
