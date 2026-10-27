"""Summarise tools/qa.mjs output: one block per kind of finding, de-duplicated across widths.

python -I tools/qa_sum.py <qa.json>
"""
import collections
import json
import sys

r = json.load(open(sys.argv[1], encoding='utf-8'))
agg = collections.defaultdict(list)
for x in r:
    p = x.get('probe')
    if not isinstance(p, dict):
        agg['probe-failed'].append((x['page'], x['w'], p))
        continue
    if x['errors']:
        agg['console'].append((x['page'], x['w'], x['errors'][:2]))
    for k, v in p.items():
        if k in ('fontsInUse', 'fontsStatus', 'domNodes', 'contrastChecked', 'contrastUnknown', 'landmarks', 'viewport'):
            continue
        if k == 'h1Count':
            if v != 1:
                agg['h1'].append((x['page'], x['w'], v))
            continue
        if isinstance(v, dict):
            v = {a: b for a, b in v.items() if b and a not in ('count', 'total', 'checked')}
        if v and v != 0:
            agg[k].append((x['page'], x['w'], v))
print('keys:', list(r[0]['probe'].keys()) if isinstance(r[0].get('probe'), dict) else r[0])
for k, v in agg.items():
    print(f'== {k} ({len(v)})')
    seen = set()
    for page, w, val in v:
        s = json.dumps(val, ensure_ascii=False)[:500]
        if (page, s) in seen:
            continue
        seen.add((page, s))
        print(f'  {page} @{w}: {s}')
