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
vm.runInContext(read("js/stories.js") + "\nthis.STORIES=STORIES;", ctx);
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

if (errs.length) { console.error("Licence check failed:\n  " + errs.join("\n  ")); process.exit(1); }
console.log(`Licence check passed: ${Object.keys(SOURCES).length} sources, ${STORIES.length} stories.`);
