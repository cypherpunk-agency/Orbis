"""Build stories/<lang>/index.json from the English index and the translated story files.
Usage: python3 tools/build/lang_index.py de"""
import json, os, sys
lang = sys.argv[1]
root = os.path.join(os.path.dirname(__file__), "..", "..")
idx = json.load(open(os.path.join(root, "stories/index.json")))
out, missing = [], []
for e in idx:
    f = os.path.join(root, "stories", lang, e["id"] + ".json")
    if os.path.exists(f):
        s = json.load(open(f))
        out.append({"id": e["id"], "cat": e["cat"], "title": s["title"], "hook": s["hook"], "file": f"stories/{lang}/{e['id']}.json"})
    else:
        out.append(e); missing.append(e["id"])   # English fallback
json.dump(out, open(os.path.join(root, "stories", lang, "index.json"), "w"), ensure_ascii=False, indent=1)
print(len(out), "stories;", "untranslated:", missing or "none")
