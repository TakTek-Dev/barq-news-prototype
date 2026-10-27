"""Self-hosted WOFF2 subsets of the three brand faces.

python -I tools/fonts.py   (from the project root; sources in research/font-src, gitignored)

Funnel Display (NORD ID, OFL) is the voice of the flash: headlines, the wordmark, figures.
Its joins are cut like a funnel, so heavy weights stay open and fast at small sizes.
Funnel Sans, the same family drawn for text, carries reading copy and the interface.
Spline Sans Mono (Eben Sorkin, OFL) is the clock: first-seen times, datelines and sources.
Its rounded terminals match the brand's soft radii.
"""
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Basic Latin, Latin-1, Latin Extended-A, transliteration letters, typographic punctuation, arrows, maths
UNICODES = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
    [0x1E0C, 0x1E0D, 0x1E24, 0x1E25, 0x1E62, 0x1E63, 0x1E6C, 0x1E6D, 0x02BE, 0x02BF, 0x02BC,
     0x2009, 0x200A, 0x2010, 0x2011, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
     0x2032, 0x2033, 0x2039, 0x203A, 0x20AC, 0x20AA, 0x2190, 0x2191, 0x2192, 0x2193, 0x2197,
     0x2212, 0x2248, 0x2264, 0x2265, 0x00D7, 0x00B0, 0x00B7]
)

JOBS = [
    ('FunnelDisplay[wght].ttf', 'funnel-display.woff2', {'wght': (300, 800)}),
    ('FunnelSans[wght].ttf', 'funnel-sans.woff2', {'wght': (300, 800)}),
    ('FunnelSans-Italic[wght].ttf', 'funnel-sans-italic.woff2', {'wght': (300, 800)}),
    ('SplineSansMono[wght].ttf', 'spline-mono.woff2', {'wght': (300, 700)}),
]


def options():
    o = subset.Options()
    o.flavor = 'woff2'
    o.layout_features = ['*']
    o.name_IDs = ['*']
    o.notdef_outline = True
    o.hinting = False
    o.desubroutinize = True
    return o


for src, out, limits in JOBS:
    font = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, src)), limits)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    font = TTFont(buf)
    sub = subset.Subsetter(options())
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    path = os.path.join(OUT, out)
    subset.save_font(font, path, options())
    print(out, os.path.getsize(path) // 1024, 'KB')

for src, lic in (('funnel-OFL.txt', 'OFL-Funnel.txt'), ('spline-OFL.txt', 'OFL-SplineSansMono.txt')):
    with open(os.path.join(SRC, src), encoding='utf-8') as f, open(os.path.join(OUT, lic), 'w', encoding='utf-8') as g:
        g.write(f.read())
