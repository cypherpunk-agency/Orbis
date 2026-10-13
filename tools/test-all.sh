#!/bin/sh
# Screenshot every listed story (3 in parallel) and print one line per story: id and "no errors" or the errors.
# Usage: sh tools/test-all.sh <outdir>   (needs the local server on :8765)
OUT=${1:-shots}
python3 -c "import json;print('\n'.join(x['id'] for x in json.load(open('stories/index.json'))))" |
  xargs -P 3 -I{} sh -c 'r=$(node tools/shoot.mjs {} '"$OUT"' 2>&1 | sed -n "/^no errors/p;/^ERRORS/,\$p" | tr "\n" " "); echo "{}: $r"'
