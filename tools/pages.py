"""Every page that is not home: stories, sections, the wire, about, alerts, search, credits, 404.

python -I tools/pages.py   -> story/*.html, <section>.html, live.html, about.html, alerts.html,
                              search.html, credits.html, 404.html, assets/data/search.json
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir
import json
from urllib.parse import quote
import os
import shell as sh
from shell import E, S, SEC, SECTIONS, esc, card, row, photo, meta, kicker, status, url, in_section, latest

ROOT = sh.ROOT


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    open(full, 'w', encoding='utf-8').write(html)


def page(path, title, desc, body, current=None, og=None):
    return sh.head(title, desc, path, og) + sh.top(current) + body + sh.foot()


# ---------------------------------------------------------------- story
def related(s, n=4):
    same = [x for x in in_section(s['section']) if x['id'] != s['id']]
    tags = set(t.lower() for t in s.get('tags', []))
    same.sort(key=lambda x: (-len(tags & set(t.lower() for t in x.get('tags', []))), -sh.when(x).timestamp()))
    return same[:n]


def story(s):
    sh.C.R = '../'
    sec = SEC[s['section']]
    t = sh.when(s)
    figs = ''.join(f'<div class="fig"><b>{esc(f["value"])}</b><span>{esc(f["label"])}</span><small>{esc(f["source"])}</small></div>' for f in s.get('figures', []))
    paras = ''.join(f'<p>{esc(p)}</p>' for p in s['body'])
    src = ''.join(f'<li><a href="{esc(x["url"])}" rel="noopener" target="_blank"><span><b>{esc(x["name"])}</b><small>{esc(x["date"])} · {esc(x["url"].split("/")[2])}</small></span>{sh.icon("i-out")}</a></li>' for x in s['sources'])
    ph = ''
    if s.get('photo'):
        ph = f'<figure class="story-ph">{photo(s["photo"], "", "(max-width: 1320px) 100vw, 1260px", eager=True)}{sh.credit(s["photo"])}</figure>'
    where = ''
    if s.get('ll'):
        where = (f'<div class="where">{sh.flash_map([], "map", labels=False, focus=s["ll"])}'
                 f'<div><b>{esc(s["place"])}</b><span>{esc(s["region"])} · first seen {esc(sh.stamp(s, True))}</span></div></div>')
    tags = ''.join(f'<a href="../search.html?q={quote(tg.lower())}">{esc(tg)}</a>' for tg in s.get('tags', []))
    rel = ''.join(row(x, False) for x in related(s))
    first = sh.hm(s) or '—'
    body = f'''<div class="prog" aria-hidden="true"></div>
<main id="main" class="story wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../home.html">Barq</a><span aria-hidden="true">/</span><a href="../{sec[0]}.html">{sec[1]}</a><span aria-hidden="true">/</span><span>{esc(s['place'])}</span></nav>
<header class="story-hd">
{kicker(s)}
<h1 class="h-xl">{esc(s['headline'])}</h1>
<p class="dek">{esc(s['dek'])}</p>
<div class="clock">
<div>First seen<b><time datetime="{s['first_seen']}">{first} · {sh.day(t, True)}</time></b></div>
<div>Status<b>{status(s)}</b></div>
<div>Sources<b>{len(s['sources'])} cited</b></div>
<div class="share"><button class="tool" type="button" data-copy aria-label="Copy link"><svg aria-hidden="true"><use href="#i-link"/></svg></button></div>
</div>
</header>
{ph}
<div class="story-grid">
<article>
{f'<div class="figs">{figs}</div>' if figs else ''}
<div class="body">{paras}</div>
<section class="sources" aria-labelledby="src-h"><h2 id="src-h">Where this comes from</h2><ol>{src}</ol>
<p class="note" style="margin-top:14px">Barq summarises the reporting above in its own words. Figures are given as the named source gives them.</p></section>
</article>
<aside class="aside">
{where}
{f'<div><p class="side-h">Tagged</p><div class="tags">{tags}</div></div>' if tags else ''}
<div><p class="side-h">More from {sec[1]}</p><ul class="rows">{rel}</ul></div>
</aside>
</div>
</main>'''
    og = sh.BASE_URL + f'assets/img/photo/{s["photo"]}.webp' if s.get('photo') else None
    write(f'story/{s["id"]}.html', page(f'story/{s["id"]}.html', s['headline'], s['dek'], body, s['section'], og))


# ---------------------------------------------------------------- section
def section(slug, label, stand):
    sh.C.R = ''
    xs = in_section(slug)
    dev = len([s for s in xs if s['status'] == 'developing'])
    lead, rest = xs[0], xs[1:]
    cards = rest[:3]
    rows_ = rest[3:]
    on_map = [s for s in xs if s.get('ll')]
    mapbox = ''
    if on_map:
        mapbox = f'<aside class="radar" style="position:static"><div class="radar-hd"><h2>{label} on the map</h2><p>{len(on_map)} places</p></div>{sh.flash_map(on_map)}{sh.age_key()}</aside>'
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Section</span><h1>{label}</h1><p>{esc(stand)}</p>
<div class="stats"><span><b>{len(xs)}</b>stories this edition</span><span><b>{dev}</b>still developing</span><span><b>{sh.stamp(xs[0])}</b>latest flash</span></div></div></header>
<section class="band wrap"><div class="lead-grid">
<a class="lead" href="{url(lead)}">{photo(lead.get('photo'), '', '(max-width: 1024px) 100vw, 58vw', eager=True)}<div class="txt">{kicker(lead)}<h2 class="h-l">{esc(lead['headline'])}</h2><p class="dek">{esc(lead['dek'])}</p>{meta(lead)}</div></a>
{mapbox}
</div></section>
{f'<section class="band wrap rv"><div class="g-three">{"".join(card(s, dek=True) for s in cards)}</div></section>' if cards else ''}
{f'<section class="band wrap rv"><div class="band-hd"><h2>Earlier<small>{len(rows_)} stories</small></h2></div><ul class="rows">{"".join(row(s) for s in rows_)}</ul></section>' if rows_ else ''}
</main>'''
    write(f'{slug}.html', page(f'{slug}.html', label, stand, body, slug))


# ---------------------------------------------------------------- the wire
def live():
    sh.C.R = ''
    xs = latest()
    days = {}
    for s in xs:
        days.setdefault(sh.when(s).date(), []).append(s)
    btns = '<button type="button" data-sec="all" aria-pressed="true">All</button>' + ''.join(
        f'<button type="button" data-sec="{k}" aria-pressed="false">{v}</button>' for k, v, _ in SECTIONS)
    blocks = []
    for d, items in days.items():
        lis = ''.join(
            f'<li data-sec="{s["section"]}" class="{"dev" if s["status"] == "developing" else ""}" style="--c:var(--age-{sh.age_band(s)})">'
            f'<time datetime="{s["first_seen"]}">{sh.hm(s) or "—"}</time><span class="dot" aria-hidden="true"></span>'
            f'<a class="txt" href="{url(s)}"><span class="sec">{SEC[s["section"]][1]} · {esc(s["place"])}</span><span class="h-xs">{esc(s["headline"])}</span>'
            f'<span class="meta">{status(s)}<span>{len(s["sources"])} {"source" if len(s["sources"]) == 1 else "sources"}</span></span></a>'
            + (f'<a href="{url(s)}" tabindex="-1" aria-hidden="true">{photo(s["photo"], "", "120px")}</a>' if s.get('photo') else '') + '</li>' for s in items)
        dd = sh.long_day(sh.dt.datetime.combine(d, sh.dt.time()))
        blocks.append(f'<section class="day"><h2>{d.strftime("%A")}<small>{d.day} {d.strftime("%B")} · {len(items)} {"flash" if len(items) == 1 else "flashes"}</small></h2><ol class="feed" aria-label="{dd}">{lis}</ol></section>')
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Every flash, in order</span><h1>The wire</h1>
<p>Each story at the minute it was first seen, newest first. A filled dot is still developing; a ring is confirmed.</p></div></header>
<section class="wrap" style="padding-top:28px"><div class="strike-box">{sh.strike_line(S)}</div></section>
<div class="wrap"><div class="filters" role="group" aria-label="Filter by section">{btns}</div><p class="note" id="filter-count" aria-live="polite">{len(xs)} flashes</p>
{''.join(blocks)}</div>
</main>'''
    write('live.html', page('live.html', 'The wire', 'Every Barq flash in order, newest first.', body, 'live'))


# ---------------------------------------------------------------- about and standards
def about():
    sh.C.R = ''
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}About</span><h1>First the flash,<br>then the facts.</h1>
<p>Barq means lightning. Light arrives before the thunder; news arrives before the detail. Barq says which is which.</p></div></header>
<div class="wrap" style="padding-block:24px 40px"><div class="prose">
<h2>What Barq is</h2>
<p>Barq News reports Palestine in English as it happens: Gaza, the West Bank, Jerusalem, the prisoners, the politics and the world's response, and the ordinary life that goes on around them.</p>
<p>Speed matters in breaking news, and so does saying how sure we are. Every story on Barq carries three things in the same place: the minute it was first seen, its status, and the sources it rests on.</p>
<h2 id="standards">The three states</h2>
<div class="legend">
<div><span class="st developing">Developing</span><p>The first reports are in and the story is still moving. Figures may change; when they do, the change is shown, not hidden.</p></div>
<div><span class="st confirmed">Confirmed</span><p>The main facts are reported by named sources and are not in dispute. The story may still grow.</p></div>
<div><span class="mono" style="font-weight:600">First seen 09:42</span><p>The earliest time the story appeared in the reporting we cite, in Jerusalem time. It is a timestamp, not a claim that we were first.</p></div>
</div>
<h2>How we report</h2>
<p>Each story says where it comes from, with a link to every source. Casualty figures are given as the source gives them, with its name: the Gaza Health Ministry, the Palestinian Red Crescent, the United Nations, the Israeli army. We do not publish photographs of the dead or of children in distress.</p>
<p>The flash map places each story where it happened. Dots fade with age, the way a lightning map fades a strike: violet in the first day, paler over the week, grey after it.</p>
<h2 id="corrections">Corrections</h2>
<p>When a fact changes, the story says what changed and when. Nothing is quietly rewritten.</p>
<h2>This prototype</h2>
<p>This is a design prototype made by TakTek. Its stories are short summaries in our own words of real reporting from the outlets each one cites, for the edition of {sh.long_day(sh.NOW)}. Alerts and search work only inside the prototype. No staff, partners or readership figures are claimed. Photographs come from Wikimedia Commons; see <a href="credits.html">photo credits</a>.</p>
</div></div>
</main>'''
    write('about.html', page('about.html', 'About and standards', 'What Barq News is and how it reports.', body))


def alerts():
    sh.C.R = ''
    boxes = ''.join(f'<label><input type="checkbox" name="sec" value="{k}" {"checked" if k in ("gaza", "west-bank") else ""}> {v}</label>' for k, v, _ in SECTIONS)
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Alerts</span><h1>Get the flash first.</h1>
<p>One message when a story breaks and one when it is confirmed. Pick your sections; the rest stays quiet.</p></div></header>
<div class="wrap" style="padding-block:40px">
<div class="g-split">
<div class="chan" style="align-content:start">
<div class="alerts-band" style="grid-template-columns:1fr;padding:24px">
<a id="wa" href="#alerts-form"><span class="ci">{sh.icon('i-chat')}</span><span><b>WhatsApp channel</b><small>Flashes as they land · about 6 a day</small></span>{sh.icon('i-right')}</a>
<a id="tg" href="#alerts-form"><span class="ci">{sh.icon('i-send')}</span><span><b>Telegram</b><small>Flashes and confirmations</small></span>{sh.icon('i-right')}</a>
<a id="mail" href="#alerts-form"><span class="ci">{sh.icon('i-mail')}</span><span><b>The morning flash</b><small>Email at 07:00 Jerusalem</small></span>{sh.icon('i-right')}</a>
<a href="#alerts-form"><span class="ci">{sh.icon('i-feed')}</span><span><b>RSS</b><small>Every story, for your reader</small></span>{sh.icon('i-right')}</a>
</div></div>
<div>
<form class="form" id="alerts-form" novalidate>
<label>Email<input type="email" name="email" autocomplete="email" placeholder="you@example.org" required></label>
<fieldset class="checks"><legend>Sections</legend>{boxes}</fieldset>
<fieldset class="checks"><legend>When</legend><label><input type="radio" name="when" value="flash" checked> Every flash</label><label><input type="radio" name="when" value="morning"> Morning only</label></fieldset>
<button class="btn ion" type="submit" style="height:48px;justify-self:start">{sh.bolt_svg()}Start the alerts</button>
<p class="note">Prototype: nothing is sent or stored.</p>
</form>
<p class="done" role="status">Done. In the real site, a confirmation would be on its way now.</p>
</div></div></div>
</main>'''
    write('alerts.html', page('alerts.html', 'Alerts', 'Barq News alerts by WhatsApp, Telegram and email.', body))


def search():
    sh.C.R = ''
    idx = []
    for s in latest():
        idx.append({'u': f'story/{s["id"]}.html', 'h': s['headline'], 'd': s['dek'], 's': SEC[s['section']][1],
                    'w': sh.stamp(s, True) + ' · ' + s['place'],
                    'p': f'assets/img/photo/{s["photo"]}.webp?v={sh.V}' if s.get('photo') else '',
                    'k': ' '.join([s['headline'], s['dek'], s['place'], s['region'], SEC[s['section']][1], ' '.join(s.get('tags', [])), ' '.join(s['body'])]).lower()})
    os.makedirs(os.path.join(ROOT, 'assets', 'data'), exist_ok=True)
    json.dump(idx, open(os.path.join(ROOT, 'assets', 'data', 'search.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    sug = ''.join(f'<a href="search.html?q={q}">{q}</a>' for q in ('Rafah', 'Jenin', 'olive', 'Al-Aqsa', 'detention', 'ceasefire', 'UN'))
    body = f'''<main id="main" class="wrap" style="padding-block:40px 24px">
<h1 class="h-l" style="margin-bottom:20px">Search the edition</h1>
<label class="field">{sh.icon('i-search')}<span class="vh">Search</span><input id="q" type="search" placeholder="A place, a name, a word" autocomplete="off" autofocus data-base=""></label>
<p class="note" id="q-count" aria-live="polite" style="margin-top:12px">{len(idx)} stories in this edition</p>
<div class="tags" style="margin-top:12px">{sug}</div>
<div class="results"></div>
</main>'''
    write('search.html', page('search.html', 'Search', 'Search Barq News.', body))


def credits():
    sh.C.R = ''
    used = {}
    for s in S:
        if s.get('photo'):
            used.setdefault(s['photo'], []).append(s)
    rows_ = ''.join(
        f'<li class="row" style="grid-template-columns:132px minmax(0,1fr)">{photo(k, "", "132px")}<div class="txt"><span class="h-xs">{esc(E["photos"][k]["caption"])}</span>'
        f'<span class="meta"><span>{esc(E["photos"][k]["author"])}</span><span>{esc(E["photos"][k]["license"])}</span><a href="{esc(E["photos"][k]["page_url"])}" rel="noopener" style="text-decoration:underline">Commons file</a></span></div></li>'
        for k in sorted(used))
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Credits</span><h1>Photo credits</h1>
<p>{len(used)} photographs from Wikimedia Commons, each shown in its own colour and captioned with its real place and date.</p></div></header>
<div class="wrap" style="padding-block:24px"><ul class="rows">{rows_}</ul>
<p class="note" style="margin-top:24px">Type: Funnel Display and Funnel Sans by NORD ID, Spline Sans Mono by Eben Sorkin, all under the SIL Open Font License. Map: Natural Earth (public domain).</p></div>
</main>'''
    write('credits.html', page('credits.html', 'Photo credits', 'Where the photographs come from.', body))


def lost():
    sh.C.R = '/barq-news-prototype/'
    body = f'''<main id="main" class="wrap lost"><div>{sh.wordmark()}
<h1>No flash here.</h1><p>The page may have moved, or the link was mistyped.</p>
<p style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:24px"><a class="btn" href="{sh.C.R}home.html">Back to the news</a><a class="btn" style="background:var(--mist);color:var(--ink)" href="{sh.C.R}live.html">Open the wire</a></p></div></main>'''
    write('404.html', page('404.html', 'Not found', 'This page is not on Barq News.', body))


if __name__ == '__main__':
    for s in S:
        story(s)
    for slug, label, stand in SECTIONS:
        section(slug, label, stand)
    live()
    about()
    alerts()
    search()
    credits()
    lost()
    print(len(S), 'stories +', len(SECTIONS), 'sections + 7 pages')
