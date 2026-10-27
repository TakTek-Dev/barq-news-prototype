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
        here = sh.places()[sh.place_name(s)]
        near = [x for x in S if x.get('ll') and x['region'] == s['region']]
        more = f'<a class="more" href="{sh.place_url(s)}">{"All " + str(len(here)) + " stories from" if len(here) > 1 else "About"} {esc(sh.place_name(s))} {sh.icon("i-right")}</a>'
        where = (f'<div class="where">{sh.flash_map([], "map", labels=False, focus=s["ll"], zoom=True, aspect=1, context=near, span=120)}'
                 f'<div><b>{esc(s["place"])}</b><span>{esc(s["region"])} · first seen {esc(sh.stamp(s, True))}</span>{more}</div></div>')
        if not s.get('photo'):
            # no honest photo: open the story on where it happened instead
            ph = (f'<figure class="story-map">{sh.flash_map([], "map", labels=True, focus=s["ll"], zoom=True, aspect=2.1, context=near, label="Map: " + s["place"], span=190)}'
                  f'<figcaption><b>{esc(s["place"])}</b> · {esc(s["region"])} · the violet dot is this story; grey dots are other flashes in the edition. No photograph of this place could be verified, so none is shown.</figcaption></figure>')
    tags = ''.join(f'<a href="../search.html?q={quote(tg.lower())}">{esc(tg)}</a>' for tg in s.get('tags', []))
    rel = ''.join(row(x, False) for x in related(s))
    first = sh.hm(s) or '—'
    body = f'''<div class="prog" aria-hidden="true"></div>
<main id="main" class="story wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="../home.html">Barq</a><span aria-hidden="true">/</span><a href="../{sec[0]}.html">{sec[1]}</a><span aria-hidden="true">/</span>{f'<a href="{sh.place_url(s)}">{esc(sh.place_name(s))}</a>' if s.get('ll') else f'<span>{esc(s["place"])}</span>'}</nav>
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
    lead = next((s for s in xs if s.get('photo')), xs[0])      # the section opens on a photo when it has one
    rest = [s for s in xs if s is not lead]
    cards = [s for s in rest if s.get('photo')][:3]                 # the card row carries photos; the rest are rows
    rows_ = [s for s in rest if s not in cards]
    on_map = [s for s in xs if s.get('ll')]
    mapbox = ''
    if on_map:
        mapbox = f'<aside class="radar" style="position:static"><div class="radar-hd"><h2>{label} on the map</h2><p>{len(on_map)} {'flash' if len(on_map) == 1 else 'flashes'}</p></div>{sh.flash_map(on_map, zoom=True, aspect=.82, context=[x for x in S if x.get('ll')])}{sh.age_key()}</aside>'
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
        blocks.append(f'<section class="day" id="d-{d.isoformat()}"><h2>{d.strftime("%A")}<small>{d.day} {d.strftime("%B")} · {len(items)} {"flash" if len(items) == 1 else "flashes"}</small></h2><ol class="feed" aria-label="{dd}">{lis}</ol></section>')
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
                    'p': f'assets/img/photo/{s["photo"]}-480.webp?v={sh.V}' if s.get('photo') else '',
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
        f'<span class="meta"><span>{esc(E["photos"][k]["author"])}</span><span>{esc(E["photos"][k]["license"])}</span><a class="cf" href="{esc(E["photos"][k]["page_url"])}" rel="noopener">Commons file</a></span></div></li>'
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



# ---------------------------------------------------------------- the flash map, full size
REGIONS = ['Gaza', 'West Bank', 'Jerusalem', 'Israel']


def map_page():
    sh.C.R = ''
    pl = sh.places()
    on_map = [s for s in S if s.get('ll')]
    groups = []
    for reg in REGIONS:
        names = [n for n, xs in pl.items() if xs[0]['region'] == reg]
        if not names:
            continue
        n_reg = sum(len(pl[n]) for n in names)
        items = []
        for n in sorted(names, key=lambda n: (-len(pl[n]), n)):
            sub = ''.join(
                f'<li data-age="{sh.age_band(x)}"><a href="{url(x)}" data-id="{x["id"]}" style="--c:var(--age-{sh.age_band(x)})"><i></i>'
                f'<span>{esc(x["headline"])}</span><time class="mono">{esc(sh.stamp(x))}</time></a></li>' for x in pl[n])
            items.append(f'<li data-age="{min(sh.age_band(x) for x in pl[n])}"><a class="pl" href="places/{sh.slug(n)}.html"><b>{esc(n)}</b>'
                         f'<span class="mono">{len(pl[n])}</span></a><ul>{sub}</ul></li>')
        groups.append(f'<section class="mgroup"><h2>{reg}<small>{n_reg} {"flash" if n_reg == 1 else "flashes"} · {len(names)} '
                      f'{"place" if len(names) == 1 else "places"}</small></h2><ul class="mplaces">{"".join(items)}</ul></section>')
    ages = [('all', 'All'), ('1', 'Last 24 h'), ('2', 'Last 3 days'), ('3', 'Last 7 days')]
    btns = ''.join(f'<button type="button" data-age="{k}" aria-pressed="{str(k == "all").lower()}">{v}</button>' for k, v in ages)
    world = [x for x in latest() if not x.get('ll')]
    wl = ''.join(f'<li><a href="{url(x)}"><span>{esc(x["headline"])}</span><time class="mono">{esc(x["place"])} · {esc(sh.stamp(x))}</time></a></li>' for x in world)
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Where the news fell</span><h1>Flash map</h1>
<p>Every story of the edition at the place it happened. A dot is violet in its first day and pales through the week, the way a lightning map fades a strike.</p>
<div class="stats"><span><b>{len(on_map)}</b>flashes on the map</span><span><b>{len(pl)}</b>places</span><span><b>{len([x for x in on_map if sh.age(x) < 24])}</b>in the last 24 hours</span></div></div></header>
<div class="wrap mapgrid">
<div class="mapstage radar">{sh.flash_map(on_map, zoom=True, aspect=.6)}{sh.age_key()}</div>
<div class="maplist">
<div class="filters" role="group" aria-label="Filter by age" data-agefilter>{btns}</div>
<p class="note" id="age-count" aria-live="polite">{len(on_map)} flashes</p>
{"".join(groups)}
<section class="mgroup"><h2>Off the map<small>{len(world)} stories from abroad or Israel-wide</small></h2><ul class="mworld">{wl}</ul></section>
</div></div>
</main>'''
    write('map.html', page('map.html', 'Flash map', 'Every Barq story at the place it happened, fading with age.', body, 'map'))


# ---------------------------------------------------------------- one page per place
def place_pages():
    sh.C.R = '../'
    pl = sh.places()
    allpts = [x for x in S if x.get('ll')]
    for name, xs in pl.items():
        reg = xs[0]['region']
        dev = len([x for x in xs if x['status'] == 'developing'])
        ph = next((x['photo'] for x in xs if x.get('photo')), None)
        secs = sorted({SEC[x['section']][1] for x in xs})
        mapf = (f'<div class="radar place-map">{sh.flash_map(xs, zoom=True, aspect=1.1, context=allpts, label="Map: " + name, span=110)}'
                f'{sh.age_key()}</div>')
        lead = f'<figure class="place-ph">{photo(ph, "r169", "(max-width: 1024px) 100vw, 60vw", eager=True)}{sh.credit(ph)}</figure>' if ph else ''
        near = sorted((n for n in pl if n != name and pl[n][0]['region'] == reg), key=lambda n: (-len(pl[n]), n))[:8]
        nearl = ''.join(f'<a href="{sh.slug(n)}.html">{esc(n)} · {len(pl[n])}</a>' for n in near)
        else_ = f'<div><p class="side-h">Elsewhere in {esc(reg)}</p><div class="tags">{nearl}</div></div>' if nearl else ''
        body = f'''<main id="main">
<header class="phead"><div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="../home.html">Barq</a><span aria-hidden="true">/</span><a href="../map.html">Flash map</a><span aria-hidden="true">/</span><span>{esc(reg)}</span></nav>
<span class="kicker">{sh.bolt_svg()}Place</span><h1>{esc(name)}</h1>
<div class="stats"><span><b>{len(xs)}</b>{"story" if len(xs) == 1 else "stories"} this edition</span><span><b>{dev}</b>still developing</span><span><b>{esc(sh.stamp(xs[0]))}</b>latest flash</span><span><b>{esc(", ".join(secs))}</b>{"section" if len(secs) == 1 else "sections"}</span></div></div></header>
<div class="wrap place-grid">
<div>{lead}<h2 class="side-h" style="margin-top:8px">{len(xs)} {"story" if len(xs) == 1 else "stories"} from {esc(name)}</h2><ul class="rows">{"".join(row(x) for x in xs)}</ul></div>
<aside class="aside">{mapf}{else_}</aside>
</div>
</main>'''
        write(f'places/{sh.slug(name)}.html', page(f'places/{sh.slug(name)}.html', name, f'Barq stories from {name}, {reg}.', body))
    return len(pl)


# ---------------------------------------------------------------- the outlets Barq cites
def sources_page():
    sh.C.R = ''
    by = {}
    for x in S:
        for src in x['sources']:
            by.setdefault(sh.outlet(src['name']), {})[x['id']] = x
    ranked = sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    top = len(ranked[0][1])
    total = sum(len(x['sources']) for x in S)
    lis = []
    for name, stories in ranked:
        xs = sorted(stories.values(), key=sh.when, reverse=True)
        sl = ''.join(f'<li><a href="{url(x)}"><span>{esc(x["headline"])}</span><time class="mono">{esc(sh.stamp(x))}</time></a></li>' for x in xs)
        lis.append(f'<li><details><summary><b>{esc(name)}</b><span class="bar" style="--w:{len(xs) / top * 100:.1f}%"><i></i></span>'
                   f'<span class="mono">{len(xs)} {"story" if len(xs) == 1 else "stories"}</span></summary><ul>{sl}</ul></details></li>')
    multi = len([x for x in S if len(x['sources']) > 1])
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Where the facts come from</span><h1>Our sources</h1>
<p>Barq cites; it does not copy. Every story links to the reporting it rests on. These are the outlets this edition cites, most-cited first. Open one to see the stories that lean on it.</p>
<div class="stats"><span><b>{len(ranked)}</b>outlets</span><span><b>{total}</b>citations</span><span><b>{multi}</b>stories with more than one source</span></div></div></header>
<div class="wrap" style="padding-block:32px 24px"><ol class="outlets">{"".join(lis)}</ol>
<p class="note" style="margin-top:20px">Agency copy is counted under the outlet that carried it, as each story cites it: AFP under France 24, Reuters under Al-Monitor.</p></div>
</main>'''
    write('sources.html', page('sources.html', 'Our sources', 'The outlets Barq News cites in this edition.', body))


# ---------------------------------------------------------------- the archive: the month as a calendar
def archive():
    import calendar
    sh.C.R = ''
    days = {}
    for x in S:
        days.setdefault(sh.when(x).date(), []).append(x)
    y, m = sh.NOW.year, sh.NOW.month
    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(y, m)
    cells = []
    for wk in weeks:
        for d in wk:
            xs = sorted(days.get(d, []), key=sh.when, reverse=True)
            out, fut = d.month != m, d > sh.NOW.date()
            cls = 'cday' + (' out' if out else '') + (' fut' if fut else '') + (' has' if xs else '') + (' today' if d == sh.NOW.date() else '')
            strokes = ''.join(f'<i style="--c:var(--age-{sh.age_band(x)})"></i>' for x in sorted(xs, key=sh.when))
            heads = ''.join(f'<li>{esc(x["headline"])}</li>' for x in xs[:2])
            inner = (f'<span class="dn">{d.day}</span><span class="ct mono">{len(xs) or ""}</span>'
                     f'<span class="st-row" aria-hidden="true">{strokes}</span><ul class="hd">{heads}</ul>')
            if xs and not out:
                label = f'{d.day} {d.strftime("%B")}: {len(xs)} {"flash" if len(xs) == 1 else "flashes"}'
                cells.append(f'<a class="{cls}" href="live.html#d-{d.isoformat()}" aria-label="{label}">{inner}</a>')
            else:
                cells.append(f'<div class="{cls}" aria-hidden="true">{inner}</div>')
    dow = ''.join(f'<span>{n}</span>' for n in ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'))
    in_month = {d: v for d, v in days.items() if d.month == m}
    earlier = sorted(d for d in days if d.month != m)
    busiest = max(in_month.items(), key=lambda kv: len(kv[1]))
    early = ''
    if earlier:
        e = earlier[0]
        xs = days[e]
        early = (f'<p class="note" style="margin-top:16px">Earlier: {len(xs)} {"story" if len(xs) == 1 else "stories"} from {e.day} {e.strftime("%B")} '
                 f'(<a href="{url(xs[0])}" style="text-decoration:underline">{esc(xs[0]["headline"])}</a>). Earlier months will join the archive as it grows.</p>')
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Archive</span><h1>{sh.NOW.strftime("%B %Y")}</h1>
<p>The edition by day. Each stroke is one story, coloured by its age. Open a day to read it on the wire.</p>
<div class="stats"><span><b>{sum(len(v) for v in in_month.values())}</b>stories this month</span><span><b>{len(in_month)}</b>days with flashes</span><span><b>{busiest[0].day} {busiest[0].strftime("%b")}</b>busiest day, {len(busiest[1])} flashes</span></div></div></header>
<div class="wrap" style="padding-block:32px 24px"><div class="cal" aria-label="{sh.NOW.strftime("%B %Y")}"><div class="dow" aria-hidden="true">{dow}</div><div class="cgrid">{"".join(cells)}</div></div>
{early}</div>
</main>'''
    write('archive.html', page('archive.html', 'Archive', 'Barq News by day.', body))


# ---------------------------------------------------------------- send a tip
def tips():
    sh.C.R = ''
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Send a tip</span><h1>Seen something?</h1>
<p>If it is happening where you are, tell us. A tip is a flash: it is checked before it becomes a story, and your name is never published unless you ask.</p></div></header>
<div class="wrap tipgrid">
<div class="prose" style="max-width:none">
<h2 style="margin-top:8px">What helps</h2>
<ol class="steps">
<li><b>Where, exactly.</b> The town, the street or the junction, and what is nearby.</li>
<li><b>When.</b> The time you saw it, and whether it is still going on.</li>
<li><b>What you saw yourself</b>, kept apart from what others told you.</li>
<li><b>Photos or video</b>, if taking them was safe. The original file is better than a screenshot.</li>
</ol>
<h2>Stay safe first</h2>
<ul class="safe">
<li>No photograph is worth your safety. Leave before you film.</li>
<li>A photo can carry the place and the phone it came from. Say if you want those details removed before anything is shown.</li>
<li>Avoid showing the faces of people who have not agreed, children above all.</li>
<li>Use a phone and an account you trust, and delete the chat if your phone may be searched.</li>
</ul>
<h2>What happens next</h2>
<p>An editor reads every tip. Once a second source confirms it, it goes on the wire as a flash, marked <span class="st developing">Developing</span> until the facts are settled.</p>
</div>
<div class="tipform">
<form class="form" id="tip-form" novalidate>
<label>What happened<textarea name="what" rows="5" required placeholder="What you saw, in your own words"></textarea></label>
<div class="two"><label>Where<input type="text" name="where" placeholder="Town, street, junction"></label><label>When<input type="text" name="when" placeholder="Today, 14:20"></label></div>
<label>How to reach you <span class="opt">optional</span><input type="text" name="contact" placeholder="Email, Signal or WhatsApp" autocomplete="off"></label>
<fieldset class="checks"><legend>Please</legend><label><input type="checkbox" name="anon" checked> Keep my name out of it</label><label><input type="checkbox" name="call"> Contact me to check</label></fieldset>
<button class="btn ion" type="submit" style="height:48px;justify-self:start">{sh.bolt_svg()}Send the tip</button>
<p class="note">Prototype: nothing is sent or stored. The live site would list its secure channels here.</p>
</form>
<p class="done" role="status">Thank you. On the real site, an editor would read this now.</p>
</div>
</div>
</main>'''
    write('tips.html', page('tips.html', 'Send a tip', 'Send Barq News a tip, safely.', body))


def privacy():
    sh.C.R = ''
    body = f'''<main id="main">
<header class="phead"><div class="wrap"><span class="kicker">{sh.bolt_svg()}Privacy</span><h1>What we keep</h1>
<p>As little as the site needs to work, and nothing that follows you elsewhere.</p></div></header>
<div class="wrap" style="padding-block:24px 40px"><div class="prose">
<h2>On this prototype</h2>
<p>Nothing you type is sent anywhere. The alert and tip forms stop in your browser, and search runs on a file of this edition's stories, in your browser too.</p>
<p>Two small notes stay in your browser only: your colour theme, if you choose one, and whether you have already seen the opening flash in this visit. Clear your browser data and both are gone.</p>
<h2>On the real site</h2>
<p>Alerts would need your email, WhatsApp or Telegram, and would use it for alerts alone. Tips would be read by editors and kept apart from anything published. There would be no advertising trackers.</p>
<p>The details would be agreed with Barq's editors before launch and set out here in full.</p>
</div></div>
</main>'''
    write('privacy.html', page('privacy.html', 'Privacy', 'What Barq News keeps, and what it does not.', body))

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
    map_page()
    n = place_pages()
    sources_page()
    archive()
    tips()
    privacy()
    print(len(S), 'stories +', len(SECTIONS), 'sections +', n, 'places + 12 pages')
