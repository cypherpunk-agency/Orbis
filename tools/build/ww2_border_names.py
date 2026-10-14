"""Date-scoped display names for the WWII CShapes views; geometry is unchanged."""
from pathlib import Path
import copy, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/history/ww2'
SOURCES = {
    'ITA': 'https://history.state.gov/countries/italy/summary',
    'TUR': 'https://www.govinfo.gov/content/pkg/BILLS-115hres924ih/pdf/BILLS-115hres924ih.pdf',
    'DEU': 'https://history.state.gov/countries/germany',
}
ALIASES = {
    'ITA': ('Italy/Sardinia', 'Italy'),
    'TUR': ('Turkey (Ottoman Empire)', 'Turkey'),
    'DEU': ('Germany (Prussia)', 'Germany'),
}

def build():
    OUT.mkdir(parents=True, exist_ok=True)
    index = json.loads((ROOT / 'data/history/borders.json').read_text(encoding='utf-8'))
    index['files'] = {}
    index['retrieved'] = '2026-10-14'
    index['asOf'] = '1938-01-01, 1945-01-01 and 1950-01-01 diplomatic snapshots'
    index['note'] += (' WWII display view: only ITA, TUR and 1938/1945 DEU consolidated aliases are normalized to Italy, Turkey and Germany. Original labels are retained as sourceName; no geometry, codes, ownership, dates or numerical values change. Other source labels remain verbatim, including the distinct 1950 German states. Not a comprehensive audit of every upstream historical label.')
    index['nameSources'] = SOURCES
    index['provenance'] = []
    for year in (1938, 1945, 1950):
        src = ROOT / f'data/history/borders-{year}.json'
        raw = src.read_bytes()
        topology = json.loads(raw)
        original = copy.deepcopy(topology)
        changes = []
        for obj in topology['objects'].values():
            for feature in obj.get('geometries', []):
                p = feature['properties']
                if p.get('id') not in ALIASES:
                    continue
                old, new = ALIASES[p['id']]
                assert p['name'] == old, (year, p)
                p['sourceName'] = old
                p['name'] = new
                changes.append({'id': p['id'], 'sourceName': old, 'name': new, 'source': SOURCES[p['id']]})
        # Reversing the name-only edits must reproduce every original property and coordinate.
        restored = copy.deepcopy(topology)
        for obj in restored['objects'].values():
            for feature in obj.get('geometries', []):
                p = feature['properties']
                if 'sourceName' in p:
                    p['name'] = p.pop('sourceName')
        assert restored == original
        rel = f'data/history/ww2/borders-names-{year}.json'
        (ROOT / rel).write_text(json.dumps(topology, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
        index['files'][str(year)] = rel
        index['provenance'].append({'snapshotDate': f'{year}-01-01', 'input': str(src.relative_to(ROOT)).replace('\\', '/'), 'sha256': hashlib.sha256(raw).hexdigest(), 'nameChanges': changes, 'geometryUnchanged': True})
    (OUT / 'borders-names.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return index

if __name__ == '__main__':
    build()
