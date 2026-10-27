"""The Barq marks, drawn from Funnel Display 800 outlines.

python -I tools/brand.py   -> assets/brand/*.svg, favicon.svg, tools/out/marks.json

The q of «barq» keeps its bowl and loses its stem below the baseline: the descender is
struck as a bolt, the same width as the stem, so the name ends in the flash it is named for.
Every straight corner of the four letters is rounded (r 22 of 1200 units, tip r 12), so
the heavy cut of the face reads soft at the size of a favicon and the size of a hoarding.
"""
import json
import math
import os
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src', 'FunnelDisplay[wght].ttf')
OUT = os.path.join(ROOT, 'assets', 'brand')
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(ROOT, 'tools', 'out'), exist_ok=True)

INK, ION, WHITE = '#0C0D16', '#5B3DF5', '#FFFFFF'
R, R_TIP = 22, 12
TRACK = -26                          # wordmark tracking, font units
# the bolt, clockwise from where the right edge of the q stem (486..670) meets the baseline
BOLT = [(670, 20), (596, -92), (762, -92), (466, -360), (552, -158), (408, -158), (486, 20)]
TIP = BOLT[3]

font = instancer.instantiateVariableFont(TTFont(SRC), {'wght': 800})
gs, cmap = font.getGlyphSet(), font.getBestCmap()


def f(v):
    return ('%.1f' % v).rstrip('0').rstrip('.')


def contours(ch):
    """Glyph -> contours of nodes {p, op, ctrl}; op 'L' for straight segments into p."""
    pen = RecordingPen()
    gs[cmap[ord(ch)]].draw(pen)
    out, cur = [], None
    for op, pts in pen.value:
        if op == 'moveTo':
            cur = [{'p': pts[0], 'op': 'L', 'ctrl': []}]
        elif op == 'lineTo':
            cur.append({'p': pts[0], 'op': 'L', 'ctrl': []})
        elif op in ('qCurveTo', 'curveTo'):
            cur.append({'p': pts[-1], 'op': 'Q' if op == 'qCurveTo' else 'C', 'ctrl': list(pts[:-1])})
        elif op in ('closePath', 'endPath'):
            if len(cur) > 1 and cur[-1]['p'] == cur[0]['p']:
                last = cur.pop()
                cur[0] = last           # the closing segment arrives at the start point
            out.append(cur)
    return out


def rounded(nodes, radius=lambda p: R):
    """Closed contour -> SVG path, every line-line corner rounded with a quadratic."""
    n = len(nodes)

    def straight(i):
        return nodes[i]['op'] == 'L' and nodes[(i + 1) % n]['op'] == 'L'

    def cut(i):
        p, a, b = nodes[i]['p'], nodes[i - 1]['p'], nodes[(i + 1) % n]['p']
        la, lb = math.dist(p, a), math.dist(p, b)
        r = min(radius(p), la / 2.2, lb / 2.2)
        return ((p[0] + (a[0] - p[0]) * r / la, p[1] + (a[1] - p[1]) * r / la), p,
                (p[0] + (b[0] - p[0]) * r / lb, p[1] + (b[1] - p[1]) * r / lb))

    start = cut(0)[2] if straight(0) else nodes[0]['p']
    d = ['M' + f(start[0]) + ' ' + f(start[1])]
    for k in range(1, n + 1):
        i = k % n
        nd = nodes[i]
        if nd['op'] == 'Q':
            c = nd['ctrl']
            for j, cp in enumerate(c):
                e = nd['p'] if j == len(c) - 1 else ((cp[0] + c[j + 1][0]) / 2, (cp[1] + c[j + 1][1]) / 2)
                d.append(f'Q{f(cp[0])} {f(cp[1])} {f(e[0])} {f(e[1])}')
        elif nd['op'] == 'C':
            (a, b), e = nd['ctrl'], nd['p']
            d.append(f'C{f(a[0])} {f(a[1])} {f(b[0])} {f(b[1])} {f(e[0])} {f(e[1])}')
        else:
            t = cut(i)[0] if straight(i) else nd['p']
            d.append(f'L{f(t[0])} {f(t[1])}')
        if straight(i):
            _, p, pb = cut(i)
            d.append(f'Q{f(p[0])} {f(p[1])} {f(pb[0])} {f(pb[1])}')
    return ''.join(d) + 'Z'


def q_with_bolt():
    """The q outline with the stem below y=20 replaced by the bolt."""
    outer, counter = contours('q')
    k = next(i for i, nd in enumerate(outer) if nd['p'] == (486, -240))
    walk = outer[k + 1:] + outer[:k]                    # (486,77) ... (670,420)
    walk = [nd for nd in walk if nd['p'][1] != -240]
    ring = walk + [{'p': p, 'op': 'L', 'ctrl': []} for p in BOLT]
    ring[0] = {**ring[0], 'op': 'L'}                    # (486,20) -> (486,77) is straight
    return [rounded(ring, lambda p: R_TIP if p == TIP else R), rounded(counter)]


letters, x = [], 0
for ch in 'barq':
    paths = q_with_bolt() if ch == 'q' else [rounded(c) for c in contours(ch)]
    letters.append({'ch': ch, 'x': x, 'd': ' '.join(paths)})
    x += gs[cmap[ord(ch)]].width + TRACK
WIDTH = x - TRACK
TOP, BOT, PAD = 860, -380, 40


def svg_wordmark(fill):
    g = ''.join(f'<path transform="translate({L["x"] + PAD} 0)" d="{L["d"]}"/>' for L in letters)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-TOP} {WIDTH + PAD * 2} {TOP - BOT}" role="img" aria-label="Barq">'
            f'<g transform="scale(1 -1)" fill="{fill}" fill-rule="evenodd">{g}</g></svg>')


Q_BOX = (28, -360, 762, 612)


def svg_tile(bg, fg, size=1200, rx=300, s=0.8):
    """App tile: the bolt-q alone, centred on its bounding box, nudged up so the bowl sits optically centred."""
    cx, cy = (Q_BOX[0] + Q_BOX[2]) / 2, (Q_BOX[1] + Q_BOX[3]) / 2
    tx, ty = size / 2 - cx * s, size / 2 + cy * s
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"><rect width="{size}" height="{size}" rx="{rx}" fill="{bg}"/>'
            f'<g transform="translate({f(tx)} {f(ty)}) scale({s} {-s})"><path d="{letters[-1]["d"]}" fill="{fg}" fill-rule="evenodd"/></g></svg>')


files = {
    'barq-wordmark-ink.svg': svg_wordmark(INK),
    'barq-wordmark-white.svg': svg_wordmark(WHITE),
    'barq-wordmark-ion.svg': svg_wordmark(ION),
    'barq-tile-ion.svg': svg_tile(ION, WHITE),
    'barq-tile-storm.svg': svg_tile(INK, WHITE),
    'barq-tile-white.svg': svg_tile(WHITE, ION),
}
for name, s in files.items():
    open(os.path.join(OUT, name), 'w', encoding='utf-8').write(s)
open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(svg_tile(ION, WHITE, rx=330, s=0.94))

bolt = rounded([{'p': p, 'op': 'L', 'ctrl': []} for p in BOLT], lambda p: R_TIP if p == TIP else R)
marks = {'width': WIDTH, 'top': TOP, 'bottom': BOT, 'pad': PAD, 'q_box': Q_BOX,
         'letters': letters, 'bolt': bolt, 'bolt_pts': BOLT}
json.dump(marks, open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), 'w', encoding='utf-8'), indent=1)
print('wordmark width', WIDTH, '| files', len(files) + 1)
