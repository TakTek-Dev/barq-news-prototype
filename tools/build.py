"""Home page: the lead, the flash map, the strike line, the sections.

python -I tools/build.py   -> home.html
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir
import os
import shell as sh
from shell import E, S, esc, card, row, photo, meta, kicker, status, url, in_section, latest, SEC

ROOT = sh.ROOT
sh.C.R = ''


def lead_block(used):
    s = sh.BY[E['lead']]
    used.add(s['id'])
    subs = [sh.BY[i] for i in E.get('lead_subs', [])] or latest(3, used)
    for x in subs:
        used.add(x['id'])
    sub = ''.join(f'<a href="{url(x)}">{kicker(x)}<h2 class="h-xs">{esc(x["headline"])}</h2>{meta(x, st=False)}</a>' for x in subs)
    return f'''<article class="lead">
<a href="{url(s)}" aria-hidden="true" tabindex="-1">{photo(s.get('photo'), '', '(max-width: 1024px) 100vw, 58vw', eager=True)}</a>
<div class="txt">{kicker(s)}
<a href="{url(s)}"><h1 class="h-xl">{esc(s['headline'])}</h1></a>
<p class="dek">{esc(s['dek'])}</p>
{meta(s)}</div>
<div class="lead-sub">{sub}</div>
</article>'''


def radar():
    on_map = [s for s in S if s.get('ll')]
    newest = latest(6)
    lst = ''.join(f'<li><a href="{url(s)}" data-id="{s["id"]}" style="--c:var(--age-{sh.age_band(s)})"><span class="t"><i></i>{esc(sh.stamp(s))} · {esc(s["place"])}</span><span class="h">{esc(s["headline"])}</span></a></li>' for s in newest)
    return f'''<aside class="radar" aria-labelledby="radar-h">
<div class="radar-hd"><h2 id="radar-h"><a href="map.html" class="hl">Flash map</a></h2><p>{len(on_map)} places · fading with age</p></div>
<div class="radar-body">{sh.flash_map(on_map)}<ol class="flist">{lst}</ol></div>
{sh.age_key()}
<div style="display:flex;gap:20px;flex-wrap:wrap"><a class="more" href="map.html">Open the map {sh.icon('i-right')}</a><a class="more" href="live.html">Every flash on the wire {sh.icon('i-right')}</a></div>
</aside>'''


def strike():
    n = len([s for s in S if sh.age(s) < 168])
    return f'''<section class="strike wrap rv" aria-labelledby="strike-h">
<div class="strike-box">
<div class="strike-hd"><h2 id="strike-h">The strike line</h2><p>{n} flashes in seven days, one lane per section, newest on the right</p></div>
{sh.strike_line(S)}
</div>
</section>'''


def band_head(sec, label=None):
    n = len(in_section(sec))
    return (f'<div class="band-hd"><h2>{label or SEC[sec][1]}<small>{n} stories</small></h2>'
            f'<a class="all" href="{sec}.html">All {SEC[sec][1]} {sh.icon("i-right")}</a></div>')


def pick(sec, used, n):
    xs = [s for s in in_section(sec) if s['id'] not in used]
    with_ph = [s for s in xs if s.get('photo')]
    out = (with_ph + [s for s in xs if not s.get('photo')])[:n] if n <= len(with_ph) else xs[:n]
    out = sorted(out, key=sh.when, reverse=True)
    for s in out:
        used.add(s['id'])
    return out


def gaza(used):
    xs = pick('gaza', used, 5)
    big, rest = xs[0], xs[1:]
    bigc = (f'<a class="big" href="{url(big)}">{photo(big.get("photo"), "r1610", "(max-width: 1024px) 100vw, 50vw")}'
            f'{kicker(big)}<h3 class="h-l">{esc(big["headline"])}</h3><p class="dek">{esc(big["dek"])}</p>{meta(big)}</a>')
    return f'<section class="band wrap rv">{band_head("gaza")}<div class="g-feature">{bigc}{"".join(card(s) for s in rest)}</div></section>'


def west_bank(used):
    xs = pick('west-bank', used, 6)
    big, rest = xs[0], xs[1:]
    bigc = (f'<a class="card" href="{url(big)}">{photo(big.get("photo"), "r43", "(max-width: 1024px) 100vw, 40vw")}'
            f'{kicker(big)}<h3 class="h-m">{esc(big["headline"])}</h3><p class="dek">{esc(big["dek"])}</p>{meta(big)}</a>')
    return f'<section class="band wrap rv">{band_head("west-bank")}<div class="wb">{bigc}<ul class="rows">{"".join(row(s) for s in rest)}</ul></div></section>'


def pair(a, b, used):
    cols = []
    for sec in (a, b):
        xs = pick(sec, used, 4)
        xs.sort(key=lambda s: not s.get('photo'))        # the card that leads the column carries a photo
        xs = xs[:1] + sorted(xs[1:], key=sh.when, reverse=True)
        cols.append(f'<div>{band_head(sec)}{card(xs[0], "h-m", True, "r169", "(max-width: 720px) 100vw, 45vw")}<ul class="rows" style="margin-top:12px">{"".join(row(s, False) for s in xs[1:])}</ul></div>')
    return f'<section class="band wrap rv"><div class="g-split">{"".join(cols)}</div></section>'


def threads():
    items = ''.join(f'<li>{esc(w)}</li>' for w in E['week'])
    return f'''<section class="band threads rv" aria-labelledby="th-h"><div class="wrap">
<div class="band-hd"><h2 id="th-h">The week in threads<small>what the flashes add up to</small></h2><a class="all" href="live.html">Read the wire {sh.icon("i-right")}</a></div>
<ol>{items}</ol></div></section>'''


def life(used):
    xs = pick('life', used, 4)
    return f'<section class="band wrap rv">{band_head("life")}<div class="g-four">{"".join(card(s) for s in xs)}</div></section>'


def alerts_band():
    big = sh.bolt_svg('bigq')
    return f'''<section class="wrap rv" style="padding-block:24px 8px" aria-labelledby="al-h">
<div class="alerts-band">{big}
<div><span class="kicker" style="color:var(--plasma)">{sh.bolt_svg()}Alerts</span><h2 id="al-h" style="margin-top:14px">Get the flash first.</h2>
<p>One message when something breaks, a second when it is confirmed. Choose the sections you follow; nothing else arrives.</p></div>
<div class="chan">
<a href="alerts.html#wa"><span class="ci">{sh.icon('i-chat')}</span><span><b>WhatsApp channel</b><small>Flashes as they land</small></span>{sh.icon('i-right')}</a>
<a href="alerts.html#tg"><span class="ci">{sh.icon('i-send')}</span><span><b>Telegram</b><small>Flashes and confirmations</small></span>{sh.icon('i-right')}</a>
<a href="alerts.html#mail"><span class="ci">{sh.icon('i-mail')}</span><span><b>The morning flash</b><small>Email, 07:00 Jerusalem</small></span>{sh.icon('i-right')}</a>
</div></div></section>'''


def main():
    used = set()
    lead = lead_block(used)
    body = (f'<main id="main"><section class="top wrap"><div class="lead-grid">{lead}{radar()}</div></section>'
            f'{strike()}{gaza(used)}{west_bank(used)}{pair("jerusalem", "prisoners", used)}{threads()}'
            f'{pair("politics", "world", used)}{life(used)}{alerts_band()}</main>')
    page = (sh.head(sh.SITE, 'Breaking news from Palestine in English. First the flash, then the facts.', 'home.html')
            + sh.top() + sh.dateline() + body + sh.foot())
    open(os.path.join(ROOT, 'home.html'), 'w', encoding='utf-8').write(page)
    print('home.html', len(page) // 1024, 'KB')


if __name__ == '__main__':
    main()
