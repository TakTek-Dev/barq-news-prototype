"""The page shell every built page shares: head, wire, masthead, footer, loader, small parts.

Imported by build.py (home) and pages.py (everything else). C.R is the path back to the
site root: '' at the root, '../' in folders, the absolute site path on the 404 page.
"""
import datetime as dt
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '1'                                         # bump on any asset change (Chrome caches hard)
SITE = 'Barq News'
BASE_URL = 'https://taktek-dev.github.io/barq-news-prototype/'
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))
GEO = json.load(open(os.path.join(ROOT, 'tools', 'out', 'geo.json'), encoding='utf-8'))
DIM_P = os.path.join(ROOT, 'tools', 'out', 'photos.json')
DIM = json.load(open(DIM_P, encoding='utf-8')) if os.path.exists(DIM_P) else {}
esc = html.escape
NOW = dt.datetime.fromisoformat(E['now'])
S = E['stories']
BY = {s['id']: s for s in S}


class Ctx:
    R = ''


C = Ctx()

SECTIONS = [  # slug, label, standfirst
    ('gaza', 'Gaza', 'The ceasefire and what it holds back: strikes, aid at the crossings, hospitals and the slow count of the dead.'),
    ('west-bank', 'West Bank', 'Raids on the camps, settler attacks in the hills, demolitions and the olive harvest under guard.'),
    ('jerusalem', 'Jerusalem', 'Al-Aqsa, the Old City and the neighbourhoods around it: Silwan, Sheikh Jarrah, the permits and the bulldozers.'),
    ('prisoners', 'Prisoners', 'Detention without charge, deaths in custody, releases and the families who wait at the gate.'),
    ('politics', 'Politics', 'Ramallah, Gaza and the decisions taken in the Knesset that land on Palestinian lives.'),
    ('world', 'World', 'The courts, the councils and the capitals: what the world decides about Palestine, and what it does.'),
    ('life', 'Life', 'Work, harvest, schools, health, culture and sport. The news is not only of the dead.'),
]
SEC = {s[0]: s for s in SECTIONS}


def when(s):
    return dt.datetime.fromisoformat(s['first_seen'])


def hm(s):
    return when(s).strftime('%H:%M') if s.get('time_known') else ''


def day(t, year=False):
    return f"{t.day} {t.strftime('%b')}" + (f" {t.year}" if year else '')


def long_day(t):
    return f"{t.strftime('%A')} {t.day} {t.strftime('%B')} {t.year}"


def stamp(s, year=False):
    t = when(s)
    return (hm(s) + ' · ' if s.get('time_known') else '') + day(t, year)


def age(s):
    """Hours since the flash, at edition time."""
    return (NOW - when(s)).total_seconds() / 3600


def age_band(s):
    h = age(s)
    return 1 if h < 24 else 2 if h < 72 else 3 if h < 168 else 4


def url(s):
    return f"{C.R}story/{s['id']}.html"


# ---------------------------------------------------------------- icons and marks
def bolt_svg(cls='bolt'):
    """The bolt alone, as the q drops it (used as the flash icon)."""
    x0, x1 = 408, 762
    y0, y1 = -360, 20
    return (f'<svg class="{cls}" viewBox="{x0} {-y1} {x1 - x0} {y1 - y0}" aria-hidden="true">'
            f'<path transform="scale(1 -1)" d="{MARKS["bolt"]}" fill="currentColor"/></svg>')


def wordmark(cls='', label=True):
    m = MARKS
    g = ''.join(f'<path transform="translate({L["x"] + m["pad"]} 0)" d="{L["d"]}"/>' for L in m['letters'])
    lab = ' role="img" aria-label="Barq"' if label else ' aria-hidden="true"'
    return (f'<svg{lab} class="{cls}" viewBox="0 {-m["top"]} {m["width"] + m["pad"] * 2} {m["top"] - m["bottom"]}">'
            f'<g transform="scale(1 -1)" fill="currentColor" fill-rule="evenodd">{g}</g></svg>')


def boot_svg():
    """Loader: the bolt strikes first (plasma, top to bottom), then b a r and the q bowl rise in turn,
    and the bolt cools to white. The q is clipped at its baseline so its tail is only the struck bolt."""
    m = MARKS
    parts = []
    for i, L in enumerate(m['letters']):
        clip = ' clip-path="url(#boot-q)"' if L['ch'] == 'q' else ''
        parts.append(f'<g transform="translate({L["x"] + m["pad"]} 0)"><path class="bar" style="--i:{i}" d="{L["d"]}"{clip}/></g>')
    q = m['letters'][-1]
    bolt = f'<g transform="translate({q["x"] + m["pad"]} 0)"><path class="bolt" d="{m["bolt"]}"/></g>'
    return (f'<svg viewBox="0 {-m["top"]} {m["width"] + m["pad"] * 2} {m["top"] - m["bottom"]}" aria-hidden="true">'
            f'<defs><clipPath id="boot-q"><rect x="-50" y="16" width="900" height="900"/></clipPath></defs>'
            f'<g transform="scale(1 -1)" fill-rule="evenodd">{"".join(parts)}{bolt}</g></svg>')


SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="i-right" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-search" viewBox="0 0 20 20"><circle cx="8.75" cy="8.75" r="5.75" fill="none" stroke="currentColor" stroke-width="1.9"/><path d="m13.2 13.2 4.3 4.3" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></symbol>
<symbol id="i-out" viewBox="0 0 16 16"><path d="M6 3.5H3.5v9h9V10M9 3h4v4M13 3 7.5 8.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-pause" viewBox="0 0 12 12"><rect x="2.5" y="2" width="2.4" height="8" rx="1" fill="currentColor"/><rect x="7.1" y="2" width="2.4" height="8" rx="1" fill="currentColor"/></symbol>
<symbol id="i-play" viewBox="0 0 12 12"><path d="M3.5 2.2v7.6a.6.6 0 0 0 .9.5l6-3.8a.6.6 0 0 0 0-1L4.4 1.7a.6.6 0 0 0-.9.5z" fill="currentColor"/></symbol>
<symbol id="i-menu" viewBox="0 0 20 20"><path d="M3.5 6.5h13M3.5 13.5h13" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></symbol>
<symbol id="i-close" viewBox="0 0 20 20"><path d="m5 5 10 10M15 5 5 15" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></symbol>
<symbol id="i-link" viewBox="0 0 20 20"><path d="M8.5 11.5a3.2 3.2 0 0 0 4.6.2l2.6-2.6a3.3 3.3 0 0 0-4.6-4.6l-1 1M11.5 8.5a3.2 3.2 0 0 0-4.6-.2L4.3 10.9a3.3 3.3 0 0 0 4.6 4.6l1-1" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-mail" viewBox="0 0 20 20"><rect x="2.5" y="4.5" width="15" height="11" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="m3.5 6 6.5 5 6.5-5" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-chat" viewBox="0 0 20 20"><path d="M10 3.2c-3.9 0-7 2.7-7 6.1 0 1.6.7 3.1 1.9 4.2l-.6 3 3.1-1.4c.8.3 1.7.4 2.6.4 3.9 0 7-2.7 7-6.2S13.9 3.2 10 3.2z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></symbol>
<symbol id="i-send" viewBox="0 0 20 20"><path d="M17 3 8.6 11.4M17 3l-5.2 14-3.2-5.6L3 8.2 17 3z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/></symbol>
<symbol id="i-feed" viewBox="0 0 20 20"><path d="M4.5 9a6.5 6.5 0 0 1 6.5 6.5M4.5 4a11.5 11.5 0 0 1 11.5 11.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><circle cx="5.2" cy="14.8" r="1.6" fill="currentColor"/></symbol>
</defs></svg>'''


def icon(name, cls='ic'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


# ---------------------------------------------------------------- photos
def photo(slug, cls='', sizes='(max-width: 720px) 100vw, 50vw', eager=False, alt=None):
    if not slug or slug not in E['photos']:
        return f'<div class="ph plate {cls}">{bolt_svg("")}</div>'
    p = E['photos'][slug]
    dim = DIM.get(slug, {'w': 1000, 'h': 667})
    a = esc(p['alt'] if alt is None else alt)
    lz = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<div class="ph {cls}"><img src="{C.R}assets/img/photo/{slug}.webp?v={V}" alt="{a}" '
            f'width="{dim["w"]}" height="{dim["h"]}" {lz} sizes="{sizes}"></div>')


def credit(slug):
    p = E['photos'][slug]
    return f'<figcaption>{esc(p["caption"])} <b>Photo:</b> {esc(p["author"])} / Wikimedia Commons, {esc(p["license"])}</figcaption>'


# ---------------------------------------------------------------- small parts
def status(s):
    return f'<span class="st {s["status"]}">{"Developing" if s["status"] == "developing" else "Confirmed"}</span>'


def meta(s, place=True, st=True):
    bits = [f'<time datetime="{s["first_seen"]}">{stamp(s)}</time>']
    if place:
        bits.append(f'<span>{esc(s["place"])}</span>')
    if st:
        bits.append(status(s))
    return '<span class="meta">' + ''.join(bits) + '</span>'


def kicker(s, link=False):
    lab = SEC[s['section']][1]
    return f'<span class="kicker">{bolt_svg()}{lab}</span>'


def card(s, h='h-s', dek=False, ph='r32', sizes='(max-width: 720px) 100vw, 25vw'):
    return (f'<a class="card" href="{url(s)}">{photo(s.get("photo"), ph, sizes)}'
            f'{kicker(s)}<h3 class="{h}">{esc(s["headline"])}</h3>'
            + (f'<p class="dek">{esc(s["dek"])}</p>' if dek else '') + f'{meta(s)}</a>')


def row(s, dek=True):
    return (f'<li><a class="row" href="{url(s)}">{photo(s.get("photo"), "", "132px")}'
            f'<div class="txt"><h3 class="h-xs">{esc(s["headline"])}</h3>'
            + (f'<p class="dek" style="font-size:15px">{esc(s["dek"])}</p>' if dek else '') + f'{meta(s)}</div></a></li>')


def in_section(sec):
    return sorted([s for s in S if s['section'] == sec], key=when, reverse=True)


def latest(n=None, exclude=()):
    xs = [s for s in sorted(S, key=when, reverse=True) if s['id'] not in exclude]
    return xs[:n] if n else xs


# ---------------------------------------------------------------- the flash map
def project(lat, lon):
    p = GEO['proj']
    return (p['ox'] + (lon * p['k'] - p['x0']) * p['s'], p['m'] + (p['y1'] - lat) * p['s'])


def flash_map(items, cls='map', labels=True, focus=None, r=7):
    dots = []
    for s in sorted(items, key=when):
        if not s.get('ll'):
            continue
        x, y = project(*s['ll'])
        band = age_band(s)
        now = ' now' if s['status'] == 'developing' and band == 1 else ''
        dots.append(f'<a href="{url(s)}" class="fl{now}" data-id="{s["id"]}" data-t="{int(when(s).timestamp())}" style="--c:var(--age-{band})" aria-label="{esc(s["place"])}: {esc(s["headline"])}">'
                    f'<circle class="ring" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/><circle class="core" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/></a>')
    if focus:
        x, y = project(*focus)
        dots.append(f'<g class="fl now" style="--c:var(--plasma)"><circle class="ring" cx="{x:.1f}" cy="{y:.1f}" r="16"/><circle class="core" cx="{x:.1f}" cy="{y:.1f}" r="16"/></g>')
    lab = ''
    if labels:
        for name, ll, dx in (('GAZA', (31.47, 34.36), -78), ('WEST BANK', (32.3, 35.4), 14), ('JERUSALEM', (31.78, 35.23), 34), ('HAIFA', (32.8, 34.99), -76), ('NAQAB', (30.75, 34.8), -24)):
            x, y = project(*ll)
            lab += f'<text class="lbl" x="{x + dx:.0f}" y="{y + 4:.0f}">{name}</text>'
    return (f'<svg class="{cls}" viewBox="0 0 {GEO["w"]} {GEO["h"]}" role="group" aria-label="Map of Palestine with the places of recent flashes">'
            f'<path class="land" d="{GEO["land"]}"/><path class="pse" d="{GEO["pse"]}"/>{lab}{"".join(dots)}</svg>')


# ---------------------------------------------------------------- the strike line
def strike_line(items, days=7):
    """Seven days, one lane per section; each flash a short stroke coloured by its age.
    Labels are HTML (the SVG stretches to the box), positioned in percent of the span."""
    W, H = 1000, 84
    start = NOW - dt.timedelta(days=days)
    lanes = [s[0] for s in SECTIONS]
    lh = H / len(lanes)
    span = (NOW - start).total_seconds()
    pct = lambda t: (t - start).total_seconds() / span * 100
    ticks, grid = [], []
    t = (start + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0)
    while t < NOW:
        p = pct(t)
        grid.append(f'<line x1="{p * 10:.1f}" x2="{p * 10:.1f}" y1="0" y2="{H}"/>')
        ticks.append(f'<span style="left:{p:.2f}%">{t.strftime("%a %d")}</span>')
        t += dt.timedelta(days=1)
    bars = []
    for s in sorted(items, key=when):
        ts = when(s)
        if ts < start:
            continue
        x = pct(ts) * 10
        y = lanes.index(s['section']) * lh
        bars.append(f'<a href="{url(s)}" data-h="{esc(s["headline"])}" data-when="{esc(SEC[s["section"]][1])} · {esc(stamp(s))}" aria-label="{esc(s["headline"])}">'
                    f'<line class="bar" style="--c:var(--age-{age_band(s)})" x1="{x:.1f}" x2="{x:.1f}" y1="{y + 2:.1f}" y2="{y + lh - 2:.1f}"/></a>')
    labels = ''.join(f'<span>{SEC[l][1]}</span>' for l in lanes)
    return (f'<div class="sline"><div class="lanes" aria-hidden="true">{labels}</div><div class="plot">'
            f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" role="group" aria-label="Flashes of the last {days} days by section">'
            f'<g class="grid">{"".join(grid)}</g>{"".join(bars)}</svg><div class="ticks" aria-hidden="true">{"".join(ticks)}<span class="nowt" style="left:100%">Now</span></div>'
            f'<div class="tip" role="presentation"></div></div></div>')


def age_key():
    return ('<div class="age-key"><span><i style="--c:var(--age-1)"></i>Under 24 h</span><span><i style="--c:var(--age-2)"></i>1–3 days</span>'
            '<span><i style="--c:var(--age-3)"></i>3–7 days</span><span><i style="--c:var(--age-4)"></i>Older</span></div>')


# ---------------------------------------------------------------- shell
NAV = [('gaza', 'Gaza'), ('west-bank', 'West Bank'), ('jerusalem', 'Jerusalem'), ('prisoners', 'Prisoners'),
       ('politics', 'Politics'), ('world', 'World'), ('life', 'Life'), ('live', 'The wire')]


def head(title, desc, path, og=None, extra=''):
    t = f'{title} · {SITE}' if title != SITE else f'{SITE} · First the flash, then the facts'
    canon = BASE_URL + path
    img = og or (BASE_URL + 'assets/og.png')
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(t)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0C0D16">
<meta property="og:type" content="website"><meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}"><meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{C.R}favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="{C.R}assets/fonts/funnel-display.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{C.R}assets/fonts/funnel-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{C.R}assets/css/barq.css?v={V}">
<script>try{{var t=localStorage.getItem('barq-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
{extra}</head>'''


def wire():
    items = E['ticker']
    one = ''.join(f'<a href="{url(BY[t["id"]])}"><time>{esc(t["time"])}</time>{esc(t["text"])}</a>' for t in items)
    return f'''<div class="wire" role="region" aria-label="Latest flashes">
<div class="wrap">
<span class="wire-label">{bolt_svg()}FLASH</span>
<div class="wire-track"><div class="wire-run" style="--wire-s:{len(items) * 11}s">{one}<span aria-hidden="true" style="display:contents">{one.replace('<a ', '<a tabindex="-1" ')}</span></div></div>
<button class="wire-btn" type="button" aria-pressed="false" aria-label="Pause the wire"><svg aria-hidden="true"><use href="#i-pause"/></svg></button>
<span class="wire-clock">Jerusalem <b>--:--</b></span>
</div>
</div>'''


def top(current=None, boot=False):
    nav = ''.join(f'<a href="{C.R}{slug}.html"{" aria-current=\"page\"" if slug == current else ""}>{lab}</a>' for slug, lab in NAV)
    loader = (f'<div class="boot" aria-hidden="true">{boot_svg()}<div class="flash"></div><div class="cap">First the flash, then the facts</div></div>' if boot else '')
    return f'''<body>
{loader}<a class="skip" href="#main">Skip to the news</a>
{SPRITE}
{wire()}
<header class="mast">
<div class="wrap">
<a class="logo" href="{C.R}home.html" aria-label="Barq News, home">{wordmark(label=False)}<span class="news">News</span></a>
<nav class="nav" aria-label="Sections">{nav}</nav>
<div class="mast-tools">
<a class="tool" href="{C.R}search.html" aria-label="Search">{icon('i-search')}</a>
<a class="btn" href="{C.R}alerts.html">{bolt_svg()}<span>Get alerts</span></a>
<button class="tool menu-btn" type="button" aria-expanded="false" aria-label="Sections menu"><svg aria-hidden="true"><use href="#i-menu"/></svg></button>
</div>
</div>
</header>'''


def dateline():
    n = len([s for s in S if age(s) < 24])
    return (f'<div class="dateline"><div class="wrap"><span><b>{long_day(NOW)}</b> · Edition of {NOW.strftime("%H:%M")} Jerusalem</span>'
            f'<span>{len(S)} stories · {n} flashes in the last 24 hours</span></div></div>')


def foot():
    secs = ''.join(f'<li><a href="{C.R}{s[0]}.html">{s[1]}</a></li>' for s in SECTIONS)
    return f'''<footer class="foot">
<div class="wrap">
<div class="foot-grid">
<div><a class="logo" href="{C.R}home.html" aria-label="Barq News, home">{wordmark(label=False)}</a>
<p>Breaking news from Palestine, in English. First the flash, then the facts: every story says when it was first seen, whether it is still developing, and where it comes from.</p></div>
<div><h3>Sections</h3><ul>{secs}</ul></div>
<div><h3>Barq</h3><ul><li><a href="{C.R}live.html">The wire</a></li><li><a href="{C.R}alerts.html">Alerts</a></li><li><a href="{C.R}search.html">Search</a></li><li><a href="{C.R}about.html">About and standards</a></li></ul></div>
<div><h3>This prototype</h3><ul><li><a href="{C.R}index.html">Identity book</a></li><li><a href="{C.R}credits.html">Photo credits</a></li><li><a href="{C.R}about.html#corrections">Corrections</a></li></ul></div>
</div>
<div class="foot-base"><span>Design prototype by TakTek · stories summarised from the outlets each one cites · edition of {day(NOW, True)}</span>
<span class="theme-sw" role="group" aria-label="Colour theme"><button type="button" data-theme-set="light">Light</button><button type="button" data-theme-set="auto">Auto</button><button type="button" data-theme-set="dark">Dark</button></span></div>
</div>
</footer>
<script src="{C.R}assets/js/barq.js?v={V}" defer></script>
</body>
</html>'''
