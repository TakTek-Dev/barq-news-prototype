"""index.html: the Barq identity book, plus the downloadable kit.

python -I tools/book.py   -> index.html, assets/barq-identity.zip
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir
import os
import zipfile
import shell as sh
from shell import E, S, esc, MARKS

ROOT = sh.ROOT
sh.C.R = ''
m = MARKS


def construction():
    """The q drawn twice: the font's stem as a ghost, the bolt that replaces it, with the bolt's seven points."""
    q = m['letters'][-1]
    pts = ''.join(f'<circle cx="{x}" cy="{y}" r="9" class="pt"/><text x="{x + 16}" y="{-y + 5}" class="pl" transform="scale(1 -1)">{i + 1}</text>' for i, (x, y) in enumerate(m['bolt_pts']))
    return (f'<svg class="cons" viewBox="-60 -900 900 1320" aria-label="Construction of the q: the bolt replaces the descender">'
            f'<g transform="scale(1 -1)">'
            f'<line x1="-60" x2="840" y1="0" y2="0" class="gl"/><line x1="-60" x2="840" y1="600" y2="600" class="gl"/><line x1="-60" x2="840" y1="-240" y2="-240" class="gl d"/>'
            f'<rect x="486" y="-240" width="184" height="260" class="ghost"/>'
            f'<path d="{q["d"]}" class="qf" fill-rule="evenodd"/>{pts}</g>'
            f'<text x="-50" y="-8" class="gt">baseline</text><text x="-50" y="-608" class="gt">x-height 600</text><text x="-50" y="232" class="gt">font descender −240</text></svg>')


def swatch(name, hexv, use, dark=False):
    return f'<div class="sw" style="--c:{hexv}"><i{" class=dk" if dark else ""}></i><b>{name}</b><span class="mono">{hexv}</span><small>{use}</small></div>'


def main():
    lead = sh.BY[E['lead']]
    zipf = os.path.join(ROOT, 'assets', 'barq-identity.zip')
    with zipfile.ZipFile(zipf, 'w', zipfile.ZIP_DEFLATED) as z:
        for n in sorted(os.listdir(os.path.join(ROOT, 'assets', 'brand'))):
            z.write(os.path.join(ROOT, 'assets', 'brand', n), 'barq/' + n)
        for n in sorted(os.listdir(os.path.join(ROOT, 'assets', 'fonts'))):
            z.write(os.path.join(ROOT, 'assets', 'fonts', n), 'barq/fonts/' + n)
    kb = os.path.getsize(zipf) // 1024
    extra = '''<style>
.book section{padding-block:72px;border-top:1px solid var(--rule)}
.book .num{font:600 12px/1 var(--f-mono);color:var(--ion);letter-spacing:.08em}
.book h2{font:800 clamp(2rem,4vw,3.25rem)/1 var(--f-display);letter-spacing:-.03em;margin:12px 0 18px}
.book .lede{font-size:1.25rem;line-height:1.5;color:var(--graphite);max-width:60ch;margin:0}
.cover{background:var(--storm);color:#fff;padding-block:clamp(56px,10vw,140px) 56px!important;border:0!important;position:relative;overflow:hidden}
.cover .wm{width:min(820px,88vw);color:#fff}
.cover .wm .q{color:var(--plasma)}
.cover p{font:500 13px/1.5 var(--f-mono);color:#8E92A8;letter-spacing:.06em;text-transform:uppercase;margin:36px 0 0}
.cover h1{font:700 clamp(1.5rem,3vw,2.25rem)/1.2 var(--f-display);color:#fff;margin:18px 0 0;max-width:30ch}
.g2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:40px;align-items:center;margin-top:32px}
.cons{width:100%;max-width:520px}
.cons .gl{stroke:var(--rule);stroke-width:3}.cons .gl.d{stroke-dasharray:14 10}
.cons .ghost{fill:none;stroke:var(--slate);stroke-width:4;stroke-dasharray:16 12;opacity:.6}
.cons .qf{fill:var(--ink)}.cons .pt{fill:var(--ion)}.cons .pl{font:700 34px var(--f-mono);fill:var(--ion)}.cons .gt{font:500 26px var(--f-mono);fill:var(--slate)}
.tiles{display:flex;gap:20px;flex-wrap:wrap;align-items:end}
.tiles img{border-radius:22%}
.lock{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:28px}
.lock div{border-radius:var(--r-3);padding:40px 28px;display:grid;place-items:center;min-height:200px}
.lock img{max-height:84px}
.sws{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:14px;margin-top:28px}
.sw{display:grid;gap:4px}.sw i{height:96px;border-radius:var(--r-3);background:var(--c);border:1px solid var(--rule)}
.sw b{font:700 16px/1.2 var(--f-display);margin-top:6px}.sw small{color:var(--slate);font-size:13.5px;line-height:1.4}
.ramp{display:flex;gap:6px;margin-top:20px}.ramp span{flex:1;height:44px;border-radius:10px;background:var(--c);display:grid;place-items:end start;padding:8px;font:600 11px var(--f-mono);color:#fff}
.ramp span:nth-child(n+3){color:var(--ink)}
.faces{display:grid;gap:22px;margin-top:32px}
.face{display:grid;grid-template-columns:220px minmax(0,1fr);gap:28px;padding-top:22px;border-top:1px solid var(--rule)}
.face .s{font-size:clamp(2.5rem,6vw,5rem);line-height:1;letter-spacing:-.03em}
.dont{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-top:24px}
.dont div{background:var(--mist);border-radius:var(--r-3);padding:22px;display:grid;gap:12px;font-size:14px;color:var(--graphite)}
.dont svg{height:46px;width:auto;color:var(--ink)}
.shots{display:grid;grid-template-columns:2fr 1fr;gap:18px;margin-top:28px}
.shots a{display:block;border-radius:var(--r-3);overflow:hidden;border:1px solid var(--rule)}
@media (max-width:820px){.g2,.lock,.shots,.face{grid-template-columns:1fr}.dont{grid-template-columns:1fr 1fr}}
</style>'''
    wm_cover = sh.wordmark('wm')
    states = ''.join([
        f'<div><span class="st developing">Developing</span><p>Still moving. A violet dot, breathing like a strike on a lightning map.</p></div>',
        f'<div><span class="st confirmed">Confirmed</span><p>Named sources agree. The dot becomes a ring: the light has passed, the fact stays.</p></div>',
        f'<div><span class="mono" style="font-weight:600">First seen 09:42</span><p>The clock, set in Spline Sans Mono, always in Jerusalem time.</p></div>'])
    body = f'''<main id="main" class="book">
<section class="cover"><div class="wrap">{wm_cover}
<p>Barq News · identity book · {sh.day(sh.NOW, True)}</p>
<h1>Breaking news from Palestine. First the flash, then the facts.</h1>
<div style="display:flex;gap:10px;margin-top:32px;flex-wrap:wrap"><a class="btn ion" href="home.html">Open the site</a><a class="btn" style="background:#24273B" href="assets/barq-identity.zip" download>Download the kit · {kb} KB</a></div></div></section>

<section><div class="wrap"><span class="num">01 · IDEA</span><h2>Light arrives before thunder.</h2>
<p class="lede">Barq is Arabic for lightning. In a storm you see the flash, then you count, then you hear it. Breaking news works the same way: first a flash, then the facts. The identity is built on that gap. Every story shows when it was first seen and whether it is still developing; every mark is the flash, and the facts are set calmly around it.</p></div></section>

<section><div class="wrap"><span class="num">02 · THE MARK</span><h2>The q strikes.</h2>
<p class="lede">The name ends in q, the one letter with a tail. The tail is struck as a bolt, the width of the stem it replaces, so the word carries its own flash without a lightning icon beside it. Drawn from Funnel Display 800; every straight corner rounded at 22 of 1200 units, the tip at 12, so the cut stays soft.</p>
<div class="g2">{construction()}<div class="tiles"><img src="assets/brand/barq-tile-ion.svg" width="180" height="180" alt="Barq app tile, white q on ion violet"><img src="assets/brand/barq-tile-storm.svg" width="120" height="120" alt="Barq app tile on storm"><img src="favicon.svg" width="48" height="48" alt="Barq favicon"><img src="favicon.svg" width="24" height="24" alt=""><img src="favicon.svg" width="16" height="16" alt=""></div></div>
<div class="lock"><div style="background:var(--paper);border:1px solid var(--rule)"><img src="assets/brand/barq-wordmark-ink.svg" alt="Barq wordmark in ink"></div><div style="background:var(--storm)"><img src="assets/brand/barq-wordmark-white.svg" alt="Barq wordmark in white on storm"></div><div style="background:var(--glow)"><img src="assets/brand/barq-wordmark-ion.svg" alt="Barq wordmark in ion"></div></div>
<div class="dont">
<div>{sh.wordmark()}Keep the bolt the colour of the word. Two colours split the name.</div>
<div><span style="display:block;transform:skewX(-14deg)">{sh.wordmark()}</span>Never slant it for speed. The bolt already moves.</div>
<div><span style="display:block;filter:drop-shadow(0 0 8px #5B3DF5)">{sh.wordmark()}</span>No glow. The flash is in the shape, not an effect.</div>
<div><span style="display:block;letter-spacing:0">{sh.wordmark()}</span>Clear space: the height of the bowl on every side.</div>
</div></div></section>

<section><div class="wrap"><span class="num">03 · COLOUR</span><h2>Ion, storm and cloud.</h2>
<p class="lede">One accent only. Ion is the violet a real strike leaves on the retina; it marks the flash, the developing state and nothing else. Storm carries the wire and the map; white and cool cloud greys carry the reading. No red for urgency, no beige for warmth.</p>
<div class="sws">{swatch("Ion", "#5B3DF5", "Flash, developing, links on hover. 6.1:1 on white.")}{swatch("Storm", "#0C0D16", "Wire, map, footer, ink.")}{swatch("Plasma", "#A99BFF", "Ion on storm. 8.1:1.")}{swatch("Glow", "#EEEAFF", "Selected and highlighted surfaces.")}{swatch("Cloud", "#F4F5F9", "Panels and figures.")}{swatch("Slate", "#636880", "Metadata. 4.9:1 on white.")}</div>
<p class="lede" style="margin-top:36px;font-size:1.0625rem">Age ramp, as lightning maps fade a strike:</p>
<div class="ramp"><span style="--c:#5B3DF5">&lt; 24 h</span><span style="--c:#8C78FA">1–3 days</span><span style="--c:#BDB2FC">3–7 days</span><span style="--c:#D4D7E3">older</span></div></div></section>

<section><div class="wrap"><span class="num">04 · TYPE</span><h2>The flash, the text, the clock.</h2>
<div class="faces">
<div class="face"><div><b>Funnel Display</b><p class="note">NORD ID · OFL · 300–800<br>Headlines, figures, the wordmark</p></div><div class="s" style="font-family:var(--f-display);font-weight:800">Aid trucks wait at Kerem Shalom</div></div>
<div class="face"><div><b>Funnel Sans</b><p class="note">NORD ID · OFL · 300–800, italic<br>Reading text and interface</p></div><div style="font-size:1.25rem;line-height:1.6;max-width:58ch">{esc(lead["body"][0])}</div></div>
<div class="face"><div><b>Spline Sans Mono</b><p class="note">Eben Sorkin · OFL · 300–700<br>Times, datelines, sources</p></div><div class="mono" style="font-size:1.375rem">FIRST SEEN {sh.hm(lead) or "09:42"} · {sh.day(sh.when(lead), True).upper()} · {len(lead["sources"])} {"SOURCE" if len(lead["sources"]) == 1 else "SOURCES"}</div></div>
</div></div></section>

<section><div class="wrap"><span class="num">05 · GRAMMAR</span><h2>Three states, one clock.</h2>
<div class="legend" style="max-width:820px">{states}</div></div></section>

<section><div class="wrap"><span class="num">06 · SIGNATURES</span><h2>The flash map and the strike line.</h2>
<p class="lede">Two pictures only Barq has. The flash map puts every story where it happened and fades it with age. The strike line lays a week of flashes in seven lanes, so a reader sees at a glance where the news is falling.</p>
<div class="strike-box" style="margin-top:32px">{sh.strike_line(S)}</div>
<div class="g2" style="align-items:start"><div class="radar" style="position:static;max-width:440px"><div class="radar-hd"><h2 style="font-size:20px;margin:0">Flash map</h2><p>live on the home page</p></div>{sh.flash_map([s for s in S if s.get("ll")])}{sh.age_key()}</div>
<p class="lede" style="font-size:1.0625rem">Every dot is a link to its story. The newest strike pulses while it is still developing; a dot older than a week turns grey and stays, so the map keeps the memory of where the news fell.</p></div></div></section>

<section><div class="wrap"><span class="num">07 · MOTION</span><h2>Strike, flash, settle.</h2>
<p class="lede">The loader runs once a session, 1.7 seconds, and skips on a click or Escape: the bolt strikes down into place, the screen flashes twice like real lightning, the letters rise and the bolt cools from plasma to white. On the page, the map's dots land in the order they happened; the wire runs and pauses on hover; developing dots breathe. With reduced motion, all of it is still.</p>
<p style="margin-top:22px"><a class="btn" href="home.html?loader">Replay the loader</a></p></div></section>

<section><div class="wrap"><span class="num">08 · THE SITE</span><h2>{len(S)} stories, 7 sections, one wire.</h2>
<p class="lede">Home, a page for every story, seven sections, the wire, alerts, search, about and standards, credits and a 404.</p>
<div class="tags" style="margin-top:20px">{''.join(f'<a href="{p}">{lab}</a>' for p, lab in [("home.html", "Home"), ("live.html", "The wire"), ("gaza.html", "Gaza"), ("west-bank.html", "West Bank"), ("jerusalem.html", "Jerusalem"), (sh.url(lead), "A story"), ("alerts.html", "Alerts"), ("search.html", "Search"), ("about.html", "About"), ("404.html", "404")])}</div></div></section>
</main>'''
    page = sh.head('Identity book', 'The Barq News identity: the q that strikes, ion violet, Funnel and Spline Sans Mono.', 'index.html', extra=extra) + sh.top() + body + sh.foot()
    page = page.replace('class="wm"', 'class="wm"')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(page)
    print('index.html', len(page) // 1024, 'KB · zip', kb, 'KB')


if __name__ == '__main__':
    main()
