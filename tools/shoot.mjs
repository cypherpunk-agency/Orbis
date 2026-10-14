// Screenshot every scene of a story and report errors, chart and data lines.
// Usage: node tools/shoot.mjs <story-id or @stories/file.json> <outdir> [width height]
// ORBIS_BROWSER selects an installed browser; ORBIS_BASE_URL selects the review server.
// Needs a local server: python3 -m http.server 8765 (from the repo root). Run `npm install` in tools/ first.
import { createRequire } from "module";
import fs from "fs";
const { chromium } = createRequire(import.meta.url)("playwright");
const [id, out = "shots", w = "1280", h = "800"] = process.argv.slice(2);
if (!id) { console.error("usage: node tools/shoot.mjs <story-id|@stories/file.json> <outdir> [w h]"); process.exit(2); }
fs.mkdirSync(out, { recursive: true });
const exe = process.env.ORBIS_BROWSER || (fs.existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);
const b = await chromium.launch({ executablePath: exe, args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
const errs = [];
try {
const p = await b.newPage({ viewport: { width: +w, height: +h } });
p.on("pageerror", e => errs.push("page: " + e.message));
p.on("response", r => { if (r.status() >= 400) errs.push(r.status() + " " + r.url()); });
const base = process.env.ORBIS_BASE_URL || "http://127.0.0.1:8765/";
await p.goto(base + "#" + id + "/1");
await p.waitForFunction(()=>document.querySelectorAll("#dots .dot").length>0&&document.querySelector("#sTitle")?.textContent,{},{timeout:30000});
const n = await p.$$eval("#dots .dot", x => x.length);
if (!n) errs.push("No story scenes loaded");
const tag = id.replace(/[^a-z0-9]+/gi, "_");
for (let i = 1; i <= n; i++) {
  await p.goto(base + "#" + id + "/" + i); await p.reload();
  await p.waitForFunction(()=>document.querySelectorAll("#dots .dot").length>0&&document.querySelector("#sTitle")?.textContent,{},{timeout:30000});
  await p.waitForLoadState("networkidle"); await p.waitForTimeout(1800);
  await p.screenshot({ path: `${out}/${tag}-${i}.png` });
  const t = s => p.$eval(s, e => e.hidden ? "" : e.innerText.replace(/\s+/g, " ").trim()).catch(() => "");
  console.log(`--- scene ${i}: ${await t("#sTitle")}\n  legend: ${await t("#sLegend")}\n  chart: ${(await t("#sChart")).slice(0, 160)}\n  data: ${await t("#sData")}`);
  const sw = await p.$$("#sSwitch button");
  for (let j = 0; j < sw.length; j++) { await p.click(`#sSwitch button[data-i="${j}"]`); await p.waitForTimeout(400);
    await p.screenshot({ path: `${out}/${tag}-${i}-opt${j}.png` }); console.log(`  option ${j}: ${(await t("#sChart")).slice(0, 120)}`); }
}
} catch (e) {
  errs.push(e.message);
} finally {
  await b.close();
}
console.log(errs.length ? "ERRORS:\n" + errs.join("\n") : "no errors");
if (errs.length) process.exitCode = 1;
