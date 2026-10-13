// ---------- interface strings ----------
// The site is English only. Interface text goes through t() so a language can be added later:
// t("Distances from {x}", {x: "Vienna"}) fills {placeholders}.
const t = (s, vars) => { let r = s; if (vars) for (const k in vars) r = r.replace("{" + k + "}", vars[k]); return r; };
// static markup marks translatable text with data-t / data-t-aria; with English only this leaves it as written
function applyStaticStrings() {}
