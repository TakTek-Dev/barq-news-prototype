# Product

## Platform

web

## Stack

Static HTML/CSS/JS, no framework. Python helper scripts generate the marks, fonts, map, photos and pages (same pattern as TakTek's other news prototypes). Delivered on GitHub Pages under TakTek-Dev only when the user says «ارفع». Commits only on request.

Build order: `python -I tools/fonts.py` → `brand.py` → `geo.py` → `edition.py` → `photos.py` → `build.py` → `pages.py` → `book.py` → `og.py` (+ `node --experimental-websocket tools/shot.mjs http://localhost:8263/tools/out/og.html assets/og.png 1200 630 view`) → `links.py`. Bump `V` in tools/shell.py on any asset change. Never hand-edit the built HTML. Preview: «barq» on port 8263 in الارسال/.claude/launch.json. Loader QA: `MARKS=300,460,620,900 node --experimental-websocket tools/frames.mjs "http://localhost:8263/home.html?loader" out.png`. Page QA: `node --experimental-websocket tools/qa.mjs http://localhost:8263/ <visual-qa probe> out.json <pages…> -- 375,768,1024,1280,1440` then `python -I tools/qa_sum.py out.json`; keyboard walk: `tools/keys.mjs <url> [tabs] [width]`; published site: `python -I tools/live.py`.

## Users

English-speaking readers who follow Palestine as it breaks: diaspora Palestinians, journalists, researchers, solidarity audiences. They want to know fast, and to know how sure the news is.

## Product Purpose

Barq News (برق, lightning): breaking news from Palestine in English. No logo existed; identity from zero. Idea «First the flash, then the facts»: every story shows when it was first seen (Jerusalem time), its state (Developing / Confirmed) and its sources.

## Brand Commitments

- Mark: the q of «barq» drops a bolt in place of its descender (Funnel Display 800, corners rounded r22/1200, tip r12). No separate lightning icon, no glow, no slant.
- One accent: ion #5B3DF5 (plasma #A99BFF on storm). It marks the flash and the developing state only. No red, no beige.
- Faces: Funnel Display (flash), Funnel Sans (text), Spline Sans Mono (clock). Faces used by other TakTek prototypes are off-limits; IBM Plex banned.
- Signatures: the flash map (stories where they happened, fading by age like a lightning map) and the strike line (seven days, seven lanes).
- Every story names its sources; every photo is a real Commons photo of the place, captioned with place, date, author and licence; no photo stands for a story it does not show; no photographs of the dead or of children in distress.
- No staff, readership or partners may be invented. Alerts and search are prototypes.
