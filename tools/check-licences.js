#!/usr/bin/env node
// Checks that every data source is registered, licensed per policy, and documented.
// Usage: node tools/check-licences.js   (exit code 1 on any problem)
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const root = path.join(__dirname, "..");
const read = f => fs.readFileSync(path.join(root, f), "utf8");

const ctx = { d3: new Proxy({}, { get: () => () => () => "" }), module: undefined };
vm.createContext(ctx);
vm.runInContext(read("js/sources.js") + "\nthis.SOURCES=SOURCES;", ctx);
vm.runInContext(read("js/blocs.js") + "\nthis.STORIES=STORIES;", ctx);
const { SOURCES, STORIES } = ctx;
const doc = read("docs/LICENSING.md");
const errs = [];

for (const [id, s] of Object.entries(SOURCES)) {
  for (const k of ["name", "what", "tier", "licence", "use", "credit"]) if (!s[k]) errs.push(`${id}: missing ${k}`);
  if (!["base", "layer"].includes(s.tier)) errs.push(`${id}: tier must be base or layer`);
  if (!["commercial", "noncommercial", "permission"].includes(s.use)) errs.push(`${id}: unknown use "${s.use}"`);
  if (s.tier === "base" && s.use !== "commercial") errs.push(`${id}: base data must allow commercial use`);
  if (s.redistribute !== true) errs.push(`${id}: must be publishable in a public repository`);
  if (s.use === "permission" && !s.grant) errs.push(`${id}: permission sources need a "grant" reference`);
  if (!doc.includes("`" + id + "`")) errs.push(`${id}: no row in docs/LICENSING.md register`);
}
const used = new Set();
STORIES.forEach(st => {
  const ids = [...(st.sources || []), ...st.scenes.flatMap(sc => sc.sources || [])];
  ids.forEach(id => { used.add(id); if (!SOURCES[id]) errs.push(`story ${st.id}: unknown source "${id}"`); });
});

// data-file stories: story/scene sources plus the source declared in every dataset they load
const index = JSON.parse(read("stories/index.json"));
index.forEach(meta => {
  const st = JSON.parse(read(meta.file));
  const ds = {};
  for (const [alias, file] of Object.entries(st.data || {})) {
    const d = JSON.parse(read(file));
    if (!d.source) errs.push(`${file}: dataset has no "source"`);
    else if (!SOURCES[d.source]) errs.push(`${file}: unknown source "${d.source}"`);
    if (!d.asOf) errs.push(`${file}: dataset has no "asOf"`);
    ds[alias] = d;
  }
  [...(st.sources || []), ...st.scenes.flatMap(sc => sc.sources || [])].forEach(id => { if (!SOURCES[id]) errs.push(`story ${st.id}: unknown source "${id}"`); });
  // a scene "switch" fills {placeholders}: check the layers once per option
  const variants = sc => !sc.switch ? [sc] : sc.switch.options.map(op =>
    JSON.parse(JSON.stringify(sc).replace(/\{(\w+)\}/g, (m, k) => op[k] != null ? String(op[k]) : m)));
  st.scenes.forEach((sc0, i) => variants(sc0).forEach(sc => [...(sc.layers || []), ...(sc.chart ? [sc.chart] : [])].forEach(l => {
    if (!ds[l.data]) errs.push(`story ${st.id} scene ${i + 1}: layer uses undeclared data "${l.data}"`);
  })));
});
// campaigns (story series): every chapter must be a listed story
if (fs.existsSync(path.join(root, "stories/campaigns.json"))) JSON.parse(read("stories/campaigns.json")).forEach(c => {
  ["id", "title", "hook", "chapters"].forEach(k => { if (!c[k]) errs.push(`campaign ${c.id}: missing "${k}"`); });
  (c.chapters || []).forEach(id => { if (!index.some(m => m.id === id)) errs.push(`campaign ${c.id}: chapter "${id}" is not in stories/index.json`); });
});
// country atlas: every indicator file must name a registered source and a licence that fits its tier
if (fs.existsSync(path.join(root, "data/atlas/catalog.json"))) JSON.parse(read("data/atlas/catalog.json")).indicators.forEach(it => {
  if (!SOURCES[it.source]) errs.push(`atlas ${it.id}: unknown source "${it.source}"`);
  if (!fs.existsSync(path.join(root, it.file))) errs.push(`atlas ${it.id}: missing ${it.file}`);
  const L = String(it.licence || "").toUpperCase();
  if (it.tier === "base" && !(L.includes("CC BY") && !L.includes("NC"))) errs.push(`atlas ${it.id}: licence "${it.licence}" not allowed in the base tier`);
});
// basemap sources referenced by the engine
const app = read("js/app.js");
for (const m of app.matchAll(/source:"([a-z0-9-]+)"/g)) if (!SOURCES[m[1]]) errs.push(`js/app.js: basemap source "${m[1]}" not registered`);

if (errs.length) { console.error("Licence check failed:\n  " + errs.join("\n  ")); process.exit(1); }
console.log(`Licence check passed: ${Object.keys(SOURCES).length} sources, ${STORIES.length + index.length} stories.`);
