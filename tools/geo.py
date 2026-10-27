"""The flash map's ground: historic Palestine, with the West Bank and Gaza drawn on it.

python -I tools/geo.py   -> tools/out/geo.json  (SVG paths in a 400 x 860 box + projection)

Natural Earth 10 m (public domain) admin-0 shapes for Israel and Palestine, simplified
(Douglas-Peucker, 0.004 deg) and projected equirectangular at the land's mean latitude.
Places are projected with the same numbers in shell.py, so a flash lands where it happened.
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'ne10.geojson')
W, H, M = 400, 860, 18
LAT0 = 31.6
K = math.cos(math.radians(LAT0))


def simplify(pts, tol):
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        if a == b:
            d = math.dist(p, a)
        else:
            d = abs((b[0] - a[0]) * (a[1] - p[1]) - (a[0] - p[0]) * (b[1] - a[1])) / math.dist(a, b)
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        return simplify(pts[:idx + 1], tol)[:-1] + simplify(pts[idx:], tol)
    return [a, b]


feats = {}
for ft in json.load(open(SRC, encoding='utf-8'))['features']:
    if ft['properties']['ADM0_A3'] in ('ISR', 'PSX'):
        g = ft['geometry']
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        feats[ft['properties']['ADM0_A3']] = [[(x * K, y) for x, y in poly[0]] for poly in polys]

allp = [p for polys in feats.values() for ring in polys for p in ring]
x0, x1 = min(p[0] for p in allp), max(p[0] for p in allp)
y0, y1 = min(p[1] for p in allp), max(p[1] for p in allp)
S = min((W - 2 * M) / (x1 - x0), (H - 2 * M) / (y1 - y0))
OX = (W - (x1 - x0) * S) / 2


def proj(lon, lat):
    return (OX + (lon * K - x0) * S, M + (y1 - lat) * S)


def path(rings):
    out = []
    for ring in rings:
        r = simplify(ring, 0.004)
        pts = [(OX + (x - x0) * S, M + (y1 - y) * S) for x, y in r]
        out.append('M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + 'Z')
    return ''.join(out)


geo = {'w': W, 'h': H, 'land': path(feats['ISR']), 'pse': path(feats['PSX']),
       'proj': {'k': K, 'x0': x0, 'y1': y1, 's': S, 'ox': OX, 'm': M}}
os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)
json.dump(geo, open(os.path.join(ROOT, 'tools', 'out', 'geo.json'), 'w'), indent=1)
print('land', len(geo['land']), 'pse', len(geo['pse']), 'Jerusalem at', proj(35.235, 31.778), 'Gaza City at', proj(34.45, 31.52))
