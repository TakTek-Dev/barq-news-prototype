"""Compose the edition the site is built from.

python -I tools/edition.py   -> tools/edition.json, tools/photos.json

Reads research/news.json (the sourced stories), research/photos.json (Commons candidates),
tools/photo_map.json (story id -> photo slug, chosen by hand: only a photo of the place or
the thing the story is about) and tools/places.json (place -> lat, lon for the flash map).
"""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda *p: json.load(open(os.path.join(ROOT, *p), encoding='utf-8'))
news, cands = J('research', 'news.json'), {p['slug']: p for p in J('research', 'photos.json')['photos']}
pmap, places, cfg = J('tools', 'photo_map.json'), J('tools', 'places.json'), J('tools', 'edition_cfg.json')

WINTER = dt.datetime(2026, 10, 24, 23, 0, tzinfo=dt.timezone.utc)   # Israel and Palestine leave summer time 25 Oct 2026


def jerusalem(iso):
    """Any ISO time -> the same instant in Jerusalem local time (+03:00 summer, +02:00 from 25 Oct)."""
    t = dt.datetime.fromisoformat(iso.replace('Z', '+00:00'))
    off = 2 if t >= WINTER else 3
    return t.astimezone(dt.timezone(dt.timedelta(hours=off))).isoformat(timespec='minutes')


stories, used = [], {}
seen_ll = {}
for it in news['items']:
    s = dict(it)
    fs = s['first_seen']
    if len(fs) == 10:                                   # date only: noon, flagged as no time
        fs = fs + 'T12:00+03:00'
        s['time_known'] = False
    s['first_seen'] = jerusalem(fs)
    slug = pmap.get(s['id'])
    if slug:
        assert slug in cands, ('unknown photo', slug)
        s['photo'] = slug
        used[slug] = cands[slug]
    ll = places.get(s['place']) or places.get(s['place'].split(',')[0].strip())
    if ll:
        k = seen_ll.get(tuple(ll), 0)                   # stories in the same place fan out round it
        seen_ll[tuple(ll)] = k + 1
        if k:
            import math
            a = k * 2.4
            ll = [round(ll[0] + 0.016 * math.sin(a) * (1 + k * .25), 4), round(ll[1] + 0.019 * math.cos(a) * (1 + k * .25), 4)]
        s['ll'] = ll
    elif s['region'] != 'World':
        print('  no place for', s['id'], '|', s['place'])
    stories.append(s)

photos = {}
for slug, p in used.items():
    when = p['date'][:4] if len(p['date']) >= 4 else p['date']
    photos[slug] = {'file': p['file'], 'page_url': p['page_url'], 'author': p['author'], 'license': p['license'],
                    'date': p['date'], 'alt': p['subject'].rstrip('.'),
                    'caption': f"{p['subject'].rstrip('.')}. {p['place']}, {when}."}

now = cfg['now']
ticker = []
for t in news.get('ticker', []):
    s = next((x for x in stories if x['id'] == (t.get('id') or t.get('item'))), None)
    if not s:
        continue
    d = dt.datetime.fromisoformat(s['first_seen'])
    ticker.append({'id': s['id'], 'time': d.strftime('%H:%M') if s.get('time_known') else f"{d.day} {d.strftime('%b')}", 'text': t.get('text') or t.get('alert')})

ed = {'now': now, 'lead': cfg['lead'], 'lead_subs': cfg.get('lead_subs', []), 'ticker': ticker,
      'week': news.get('week', []), 'notes': news.get('notes', ''), 'photos': photos, 'stories': stories}
json.dump(ed, open(os.path.join(ROOT, 'tools', 'edition.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(photos, open(os.path.join(ROOT, 'tools', 'photos.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(stories), 'stories,', sum(1 for s in stories if s.get('photo')), 'with photos,', sum(1 for s in stories if s.get('ll')), 'on the map,', len(ticker), 'on the wire')
