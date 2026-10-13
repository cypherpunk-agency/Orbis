#!/usr/bin/env node
// One-off migration: export the 18 legacy JS stories (js/stories.js) to the JSON story format.
// Evaluates js/stories.js in a sandbox (stub d3), then writes
//   data/legacy/blocs.json   (sets: NATO, Warsaw Pact, EU, BRICS memberships by year)
//   data/legacy/values.json  (series: every DATA table used by a choropleth)
//   data/legacy/routes.json  (lines and points sets: cables, chokepoints, supply chains, …)
//   data/legacy/gravity.json (points list + path: the economic centre of gravity)
//   stories/<id>.json        (one per legacy story, same id)
// Usage: node tools/build/legacy_export.js
"use strict";
const fs = require("fs"), path = require("path"), vm = require("vm");
const root = path.join(__dirname, "..", "..");
const read = f => fs.readFileSync(path.join(root, f), "utf8");

const ctx = { d3: new Proxy({}, { get: () => () => () => "" }) };
vm.createContext(ctx);
vm.runInContext(read("js/stories.js") + "\nthis.X={AFRICA,EU27,SSA,NATO_JOIN,WARSAW,EU_JOIN,BRICS_JOIN,P,SUEZ_ROUTE,SUEZ_YOKO,CAPE_ROUTE,STORIES,DATA,CHOKE_PTS,GRAVITY,ROUTES,DARIEN_NAMES,CABLES,PHONE,PLATE,REMIT,resolveRef};", ctx);
const X = JSON.parse(JSON.stringify(ctx.X, (k, v) => typeof v === "function" ? undefined : v));
const ref = ctx.X.resolveRef;
const clone = v => JSON.parse(JSON.stringify(v));

// ---------- compact pretty printer ----------
const inline = v => v === null || typeof v !== "object" ? JSON.stringify(v)
  : Array.isArray(v) ? "[" + v.map(inline).join(", ") + "]"
  : "{" + Object.entries(v).filter(([, x]) => x !== undefined).map(([k, x]) => JSON.stringify(k) + ": " + inline(x)).join(", ") + "}";
function pretty(v, ind = "", width = 160) {
  const one = inline(v);
  if (one.length + ind.length <= width || v === null || typeof v !== "object") return one;
  const ni = ind + "  ";
  if (Array.isArray(v)) return "[\n" + v.map(x => ni + pretty(x, ni, width)).join(",\n") + "\n" + ind + "]";
  return "{\n" + Object.entries(v).filter(([, x]) => x !== undefined).map(([k, x]) => ni + JSON.stringify(k) + ": " + pretty(x, ni, width)).join(",\n") + "\n" + ind + "}";
}
function write(file, obj) {
  fs.mkdirSync(path.dirname(path.join(root, file)), { recursive: true });
  fs.writeFileSync(path.join(root, file), pretty(obj) + "\n");
  console.log("wrote", file);
}
const META = { asOf: "2026-10", retrieved: "2026-10-13" };
const storyById = Object.fromEntries(X.STORIES.map(s => [s.id, s]));

// ---------- datasets ----------
const plus1 = o => Object.fromEntries(Object.entries(o).map(([k, [a, b]]) => [k, [a, b + 1]]));
write("data/legacy/blocs.json", {
  source: "editorial", ...META,
  note: "Hand-entered membership years (year of accession). " + storyById.blocs.notes +
    " Malta (EU 2004) added; it was missing from the legacy table. Ranges are [first year, first year no longer a member): the Warsaw Pact dissolved in July 1991, so its members are shown through 1991; Albania is shown through 1968.",
  sets: {
    nato: { label: "NATO", members: X.NATO_JOIN },
    warsaw: { label: "Warsaw Pact", members: plus1(X.WARSAW) },
    // the legacy table lacked Malta (EU member since 2004); added here
    eu: { label: "EEC / EC / EU", members: Object.assign({}, X.EU_JOIN, { MLT: 2004, GBR: [X.EU_JOIN.GBR, 2020] }) },
    brics: { label: "BRICS", members: X.BRICS_JOIN }
  }
});

// every DATA table, each a single-year series; one shared years axis with nulls elsewhere
const TABLES = {
  POP: { key: "pop", year: 2025, label: "Population", units: "million people", story: "circle" },
  MEDAGE: { key: "median_age", year: 2024, label: "Median age", units: "years", story: "demography" },
  POWER: { key: "electricity_access", year: 2022, label: "Access to electricity", units: "% of population (countries near universal access omitted)", story: "dark" },
  COBALT: { key: "cobalt_share", year: 2023, label: "Share of world cobalt mining", units: "% of world mine production", story: "minerals" },
  LITHIUM: { key: "lithium_share", year: 2023, label: "Share of world lithium mining", units: "% of world mine production", story: "minerals" },
  RARE: { key: "rare_earth_share", year: 2023, label: "Share of world rare-earth mining", units: "% of world mine production", story: "minerals" },
  REMIT_USD: { key: "remit_usd", year: 2023, label: "Remittances received", units: "billion USD", story: "remittances" },
  REMIT_GDP: { key: "remit_gdp", year: 2023, label: "Remittances received, share of GDP", units: "% of GDP", story: "remittances" },
  LANGS: { key: "languages", year: 2024, label: "Living languages", units: "number of languages (approximate)", story: "languages" }
};
const YEARS = [...new Set(Object.values(TABLES).map(t => t.year))].sort();
const series = {};
for (const [name, t] of Object.entries(TABLES)) {
  const values = {};
  for (const [k, v] of Object.entries(X.DATA[name])) values[k] = YEARS.map(y => y === t.year ? v : null);
  series[t.key] = { label: t.label, units: t.units, values };
}
write("data/legacy/values.json", {
  source: "editorial", ...META, years: YEARS,
  note: "Hand-entered, rounded figures from the original Orbis stories. Each series holds one year only. " +
    [...new Set(Object.values(TABLES).map(t => t.story))].map(sid => {
      const ts = Object.values(TABLES).filter(t => t.story === sid);
      return ts.map(t => `${t.key} (${t.year})`).join(", ") + ": " + storyById[sid].notes; }).join(" "),
  series
});

// lines and points sets
const L = (name, p, extra = {}) => Object.assign({ name, path: p }, extra);
const mines = X.PHONE.mines, ref_ = X.PHONE.refinery, chips = X.PHONE.chips, asm = X.PHONE.assembly;
write("data/legacy/routes.json", {
  source: "editorial", ...META,
  note: "Schematic routes and approximate places drawn for the original Orbis stories; for orientation only. Cables: " + storyById.cables.notes +
    " Chokepoints: " + storyById.chokepoints.notes + " Phone supply chain: " + storyById.phone.notes + " Minerals: " + storyById.minerals.notes +
    " Remittance corridors: " + storyById.remittances.notes + " Breakfast: " + storyById.plate.notes + " Northwest Passage: " + storyById.arctic.notes,
  lines: {
    cables_atlantic: X.CABLES.atl.map(c => L(c.label, c.path)),
    cables_pacific: X.CABLES.pac.slice(0, 2).map(c => L(c.label, c.path)),
    cable_smw6: X.CABLES.pac.slice(2).map(c => L(c.label, c.path)),
    cable_2africa: X.CABLES.afr.slice(0, 1).map(c => L(c.label, c.path)),
    cable_equiano: X.CABLES.afr.slice(1).map(c => L(c.label, c.path)),
    nwp: [L("Northwest Passage", X.ROUTES.NWP)],
    to_refinery_imported: mines.filter(m => m.label.indexOf("China") < 0).map(m => L(m.label + " to refining in China", [m.at, ref_])),
    to_refinery_domestic: mines.filter(m => m.label.indexOf("China") >= 0).map(m => L(m.label + " to refining", [m.at, ref_])),
    phone_chips: [[0, 2, chips], [1, 2, chips], [3, 0, asm], [4, 0, asm], [2, 0, asm]].map(([a, b, to]) => L(chips[a].label + " to " + to[b].label, [chips[a].at, to[b].at])),
    phone_assembly: asm.slice(1).map(a => L("Chips, Taiwan to " + a.label, [chips[2].at, a.at])),
    phone_home: asm.map(a => L(a.label + " to Vienna", [a.at, X.P.vienna])),
    remittances: X.REMIT.map((r, i) => L("Corridor " + (i + 1), r)),
    plate_coffee: X.PLATE.coffee.map(p => L(p.label, [p.at, X.P.vienna])),
    plate_cj: X.PLATE.cj.map(p => L(p.label, [p.at, X.P.vienna])),
    plate_local: X.PLATE.local.map(p => L(p.label, [p.at, X.P.vienna]))
  },
  points: {
    chokepoints: X.CHOKE_PTS.map(p => ({ name: p.label, at: p.at })),
    phone_mines: mines.map(p => ({ name: p.label, at: p.at })),
    phone_chips: chips.map(p => ({ name: p.label, at: p.at })),
    phone_assembly: asm.map(p => ({ name: p.label, at: p.at }))
  }
});

// gravity: one point per year. "centre" is a display size for a symbols layer on the timeline:
// 1 in that point's own year (the current position), 0.15 afterwards (the trail), null before.
const GY = X.GRAVITY.map(g => g.y);
write("data/legacy/gravity.json", {
  source: "editorial", ...META,
  note: "Approximate positions of the economic centre of gravity. " + storyById.gravity.notes,
  periods: GY.map(String),
  units: { centre: "display size only: 1 = position of the centre in the year shown, 0.15 = an earlier position" },
  points: X.GRAVITY.map((g, i) => ({ id: "y" + g.y, name: g.y === 1 ? "Year 1" : String(g.y), at: g.at, centre: GY.map((_, j) => j === i ? 1 : j > i ? 0.15 : null) })),
  lines: { path: [L("Economic centre of gravity, year 1 to 2025", X.ROUTES.GRAVITY)] }
});

// ---------- stories ----------
const V = "data/legacy/values.json", B = "data/legacy/blocs.json", R = "data/legacy/routes.json", G = "data/legacy/gravity.json";
const CHORO = {  // legacy choro.data -> layer
  POP: { series: "pop", year: 2025, mult: 1e6, log: true },
  MEDAGE: { series: "median_age", year: 2024 },
  POWER: { series: "electricity_access", year: 2022, reverse: true, fmt: "pct" },
  COBALT: { series: "cobalt_share", year: 2023, fmt: "pct" },
  LITHIUM: { series: "lithium_share", year: 2023, fmt: "pct" },
  RARE: { series: "rare_earth_share", year: 2023, fmt: "pct" },
  REMIT_USD: { series: "remit_usd", year: 2023, log: true, fmt: "busd" },
  REMIT_GDP: { series: "remit_gdp", year: 2023, fmt: "pct" },
  LANGS: { series: "languages", year: 2024, log: true }
};
const lines = (set, color, width, o = {}) => Object.assign({ type: "lines", data: "routes", set, color, width }, o);
const pts = (set, color, r, o = {}) => Object.assign({ type: "points", data: "routes", set, color, r }, o);
// per story, per scene index: replacement of legacy string refs / timelines with layers
const PORT = {
  chokepoints: { 0: { layers: [pts("chokepoints", "c2", 6)], points: null } },
  cables: {
    0: { layers: [lines("cables_atlantic", "c1", 2, { labels: true, flow: true })], routes: null },
    1: { layers: ["cables_atlantic", "cables_pacific", "cable_smw6"].map(s => lines(s, "c1", 2, { labels: true, flow: true })), routes: null },
    2: { layers: [lines("cable_2africa", "c2", 2.5, { labels: true, flow: true }), lines("cable_equiano", "c2", 2.5, { labels: true, flow: true }), lines("cables_atlantic", "c1", 1.5, { labels: true })], routes: null },
    3: { layers: [lines("cable_2africa", "c1", 2), lines("cable_smw6", "c1", 2)], routes: null }
  },
  phone: {
    0: { layers: [pts("phone_mines", "c3", 5)], points: null },
    1: { layers: [lines("to_refinery_imported", "c3", 2, { flow: true }), lines("to_refinery_domestic", "c3", 2, { flow: true }), pts("phone_mines", "c3", 5)], routes: null, points: null },
    2: { layers: [lines("phone_chips", "c1", 2, { flow: true }), pts("phone_chips", "c1", 5)], routes: null, points: null },
    3: { layers: [lines("phone_assembly", "c1", 2, { flow: true }), pts("phone_assembly", "c2", 6)], routes: null, points: null },
    4: { layers: [lines("phone_home", "c2", 2, { flow: true })], routes: null }
  },
  minerals: { 3: { layers: [lines("to_refinery_imported", "c2", 2, { flow: true })], routes: null } },
  remittances: { 0: { layers: [lines("remittances", "c4", 2, { flow: true })], routes: null } },
  plate: {
    0: { layers: [lines("plate_coffee", "c3", 2, { labels: true, flow: true })], routes: null },
    1: { layers: [lines("plate_cj", "c3", 2, { labels: true, flow: true })], routes: null },
    3: { layers: [lines("plate_local", "c4", 2, { flow: true })], routes: null }  // points stay inline: label priority follows draw order
  },
  arctic: { 3: { layers: [lines("nwp", "c2", 2.5, { labels: true, flow: true })], routes: null } },
  blocs: {
    0: { layers: [{ type: "since", data: "blocs", set: "nato", year: "t", color: "c1", title: "NATO" }, { type: "since", data: "blocs", set: "warsaw", year: "t", color: "c2", title: "Warsaw Pact" }],
      timeline: { years: [1945, 2025], start: 1950 } },
    1: { layers: [{ type: "since", data: "blocs", set: "eu", year: "t", color: "c1", title: "EEC / EC, EU from 1993" }], timeline: { years: [1957, 2025], start: 1958 } },
    2: { layers: [{ type: "since", data: "blocs", set: "brics", year: "t", color: "c3", title: "BRICS" }], timeline: { years: [2008, 2025], start: 2009 } }
  },
  gravity: {
    0: { layers: [{ type: "lines", data: "gravity", set: "path", color: "c2", width: 2.5 },
                  { type: "symbols", data: "gravity", field: "centre", year: "t", color: "c2", maxR: 8, vmax: 1, labels: 0, title: "Economic centre of gravity" }],
      timeline: { years: GY, start: 1, captions: Object.fromEntries(X.GRAVITY.map(g => [g.y, g.note])) } },
    1: { layers: [{ type: "lines", data: "gravity", set: "path", color: "c2", width: 2.5 }], routes: null }
  }
};
const DATAOF = { blocs: { blocs: B }, gravity: { gravity: G } };

const ORDER = ["title", "text", "view", "basemap", "political", "layers", "timeline", "fills", "highlight", "circles", "routes", "points", "legend", "countryLabels", "sources"];
for (const st of X.STORIES) {
  const data = Object.assign({}, DATAOF[st.id] || {});
  const scenes = st.scenes.map((sc0, i) => {
    const sc = clone(sc0), legacy = ctx.X.STORIES.find(s => s.id === st.id).scenes[i];
    const out = {};
    // resolve string references to inline arrays
    if (typeof sc.points === "string") sc.points = clone(ref(sc.points));
    if (typeof sc.routes === "string") sc.routes = clone(ref(sc.routes));
    if (Array.isArray(sc.routes)) sc.routes = sc.routes.map(r => {
      r = clone(r); if (typeof r.path === "string") r.path = clone(ref(r.path));
      if (r.until != null) { r.path = r.path.slice(0, r.until + 1); delete r.until; } return r; });
    if (sc.points) sc.points = sc.points.map(p => { p = clone(p); if (p.label == null) delete p.label; return p; });
    if (sc.routes) sc.routes = sc.routes.map(r => { if (r.label == null) delete r.label; return r; });
    if (sc.choro) {
      const m = CHORO[sc.choro.data]; data.values = V;
      sc.layers = [Object.assign({ type: "choropleth", data: "values" }, m, { title: sc.choro.title, showYear: false })];
      delete sc.choro;
    }
    const p = (PORT[st.id] || {})[i];
    if (p) for (const [k, v] of Object.entries(p)) { if (v === null) delete sc[k]; else sc[k] = clone(v); }
    if (legacy.timeline && !(p && p.timeline)) throw new Error(st.id + " scene " + i + ": timeline not ported");
    if (sc.layers && sc.layers.some(l => l.data === "routes")) data.routes = R;
    for (const k of ORDER) if (sc[k] !== undefined) out[k] = sc[k];
    for (const k of Object.keys(sc)) if (!(k in out)) throw new Error(st.id + " scene " + i + ": unhandled field " + k);
    return out;
  });
  write("stories/" + st.id + ".json", { id: st.id, cat: st.cat, title: st.title, hook: st.hook, notes: st.notes, data, sources: ["editorial"], scenes });
}
