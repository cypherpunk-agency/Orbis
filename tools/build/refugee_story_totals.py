"""Derive Ukraine-only end-year stock links from the licensed UNHCR snapshot.

No network access. Preserve each published origin/asylum pair and Ukraine's
all-destination origin total; destination totals are Ukraine-only. Host pairs
below the source's 5,000-person threshold remain absent, never zero-filled.
"""
import copy
import json
import math
from pathlib import Path


def build(root):
    source_path = root / 'data/people/refugees-flows.json'
    source = json.loads(source_path.read_text(encoding='utf-8'))
    result = {key: copy.deepcopy(value) for key, value in source.items() if key != 'groups'}
    result['derivedFrom'] = 'data/people/refugees-flows.json'
    result['note'] += (' Orbis Ukraine-origin subset: links and asylum-country stocks include only '
                       'Ukraine-origin pairs present in the source (at least 5,000 people). '
                       'Absent host pairs are not zero observations. Ukraine origin totals retain '
                       'the source all-destination total, including destinations omitted from the '
                       'link display. The 2024 Russia coverage break remains a statistical break.')
    original = source['groups']['ref']
    group = {'label': 'Ukraine-origin refugees', 'flows': {}, 'exports': {}, 'imports': {}}
    for year in source['years']:
        key = str(year)
        links = [copy.deepcopy(row) for row in original['flows'].get(key, []) if row[0] == 'UKR']
        hosts = {}
        for row in links:
            assert row[1] not in hosts, f'Duplicate Ukraine/host pair: {year} {row[1]}'
            assert isinstance(row[2], (int, float)) and math.isfinite(row[2]) and row[2] >= 5000
            hosts[row[1]] = row[2]
        origin = original['exports'].get(key, {})
        group['flows'][key] = links
        group['exports'][key] = {'UKR': origin['UKR']} if 'UKR' in origin else {}
        group['imports'][key] = hosts
    result['groups'] = {'ref': group}
    target = root / 'data/history/ukraine/refugee-stock-links.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    result = build(Path(__file__).resolve().parents[2])
    print('Built Ukraine-only refugee stock links for', len(result['years']), 'observation years')
