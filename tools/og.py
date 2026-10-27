"""tools/out/og.html: the 1200x630 sharing card (wordmark on storm, the lead photo).

python -I tools/og.py
node --experimental-websocket tools/shot.mjs http://localhost:8263/tools/out/og.html assets/og.png 1200 630 view
"""
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))  # python -I drops the script dir
import os
import shell as sh

sh.C.R = '../../'
lead = sh.BY[sh.E['lead']]
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>og</title>
<link rel="stylesheet" href="../../assets/css/barq.css?v={sh.V}">
<style>html,body{{margin:0;width:1200px;height:630px;overflow:hidden;background:#0C0D16}}
.og{{display:grid;grid-template-columns:600px 600px;height:630px}}
.l{{padding:56px;display:flex;flex-direction:column;color:#fff}}.l svg{{width:420px}}
.l p{{margin-top:auto;font:800 40px/1.06 var(--f-display);letter-spacing:-.025em;max-width:15ch}}
.l small{{margin-top:18px;font:500 15px/1.3 var(--f-mono);color:#A99BFF;letter-spacing:.06em;text-transform:uppercase}}
.r img{{width:100%;height:100%;object-fit:cover}}</style></head><body><div class="og"><div class="l">{sh.wordmark()}
<p>First the flash, then the facts.</p><small>Breaking news from Palestine</small></div>
<div class="r"><img src="../../assets/img/photo/{lead["photo"]}.webp" alt=""></div></div></body></html>'''
open(os.path.join(sh.ROOT, 'tools', 'out', 'og.html'), 'w', encoding='utf-8').write(html)
print('tools/out/og.html')
