/* Barq News — page behaviour. No framework; every block checks for its own markup. */
(() => {
  const d = document, root = d.documentElement;
  const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, el = d) => el.querySelector(s), $$ = (s, el = d) => [...el.querySelectorAll(s)];
  root.classList.add('js');

  // theme: saved choice wins over the system
  const themeBtns = $$('[data-theme-set]');
  const setTheme = (t) => {
    if (t === 'auto') delete root.dataset.theme; else root.dataset.theme = t;
    try { t === 'auto' ? localStorage.removeItem('barq-theme') : localStorage.setItem('barq-theme', t); } catch (e) {}
    themeBtns.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.themeSet === t)));
  };
  let saved = 'auto';
  try { saved = localStorage.getItem('barq-theme') || 'auto'; } catch (e) {}
  themeBtns.forEach((b) => { b.setAttribute('aria-pressed', String(b.dataset.themeSet === saved)); b.addEventListener('click', () => setTheme(b.dataset.themeSet)); });

  // loader: once a session, ?loader forces it
  const boot = $('.boot');
  if (boot) {
    let seen = false;
    try { seen = sessionStorage.getItem('barq-seen') === '1'; } catch (e) {}
    if ((seen && !/[?&]loader/.test(location.search)) || calm) boot.remove();
    else {
      root.classList.add('booting');
      const end = () => {
        if (boot.classList.contains('out')) return;
        boot.classList.add('out');
        root.classList.remove('booting');
        try { sessionStorage.setItem('barq-seen', '1'); } catch (e) {}
        setTimeout(() => { boot.remove(); d.dispatchEvent(new Event('barq:ready')); }, 620);
      };
      requestAnimationFrame(() => boot.classList.add('go'));
      const t = setTimeout(end, 1750);
      boot.addEventListener('click', () => { clearTimeout(t); end(); });
      d.addEventListener('keydown', (e) => { if (e.key === 'Escape') { clearTimeout(t); end(); } }, { once: true });
    }
  }
  // page to page: cover the old page with the storm, then go; the next page lifts it (see the head script)
  const internal = (a, e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return null;
    if ((a.target && a.target !== '_self') || a.hasAttribute('download')) return null;
    const u = new URL(a.href, location.href);
    if (u.origin !== location.origin || !/^https?:$/.test(u.protocol)) return null;
    if (u.pathname === location.pathname && u.search === location.search) return null;   // same page, an anchor
    return u;
  };
  if (!calm) {
    d.addEventListener('click', (e) => {
      const a = e.target.closest('a[href]');
      const u = a && internal(a, e);
      if (!u) return;
      e.preventDefault();
      try { sessionStorage.setItem('barq-nav', '1'); } catch (er) {}
      root.classList.add('nav-out');
      setTimeout(() => { location.href = u.href; }, 300);
    });
    // warm the next page while the pointer is on its link
    const warmed = new Set();
    d.addEventListener('pointerover', (e) => {
      const a = e.target.closest('a[href]');
      if (!a || warmed.has(a.href) || !internal(a, { button: 0 })) return;
      warmed.add(a.href);
      const l = d.createElement('link'); l.rel = 'prefetch'; l.href = a.href; d.head.appendChild(l);
    });
  }
  // back/forward from the cache: never come back to a covered page
  addEventListener('pageshow', (e) => { if (e.persisted) root.classList.remove('nav-out', 'nav-in'); });
  setTimeout(() => root.classList.remove('nav-in'), 700);

  const ready = (fn) => (d.querySelector('.boot') ? d.addEventListener('barq:ready', fn, { once: true }) : fn());

  // wire: pause, clock in Jerusalem, a flicker each time the run loops
  const wire = $('.wire');
  if (wire) {
    const btn = $('.wire-btn', wire), run = $('.wire-run', wire), label = $('.wire-label', wire);
    btn && btn.addEventListener('click', () => {
      const p = wire.toggleAttribute('data-paused');
      btn.setAttribute('aria-pressed', String(p));
      btn.setAttribute('aria-label', p ? 'Play the wire' : 'Pause the wire');
      $('use', btn).setAttribute('href', p ? '#i-play' : '#i-pause');
    });
    if (calm && btn) btn.hidden = true;
    run && run.addEventListener('animationiteration', () => { label.classList.remove('lit'); void label.offsetWidth; label.classList.add('lit'); });
    const clock = $('.wire-clock b', wire);
    if (clock) {
      const fmt = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Jerusalem', hour: '2-digit', minute: '2-digit' });
      const tick = () => { clock.textContent = fmt.format(new Date()); };
      tick(); setInterval(tick, 15000);
    }
  }

  // masthead
  const mast = $('.mast');
  if (mast) {
    const on = () => mast.classList.toggle('scrolled', scrollY > 8);
    on(); addEventListener('scroll', on, { passive: true });
    const mb = $('.menu-btn'), nav = $('.nav');
    mb && mb.addEventListener('click', () => {
      const o = nav.classList.toggle('open');
      mb.setAttribute('aria-expanded', String(o));
      $('use', mb).setAttribute('href', o ? '#i-close' : '#i-menu');
    });
    d.addEventListener('keydown', (e) => {
      if (e.key !== 'Escape' || !nav.classList.contains('open')) return;
      nav.classList.remove('open'); mb.setAttribute('aria-expanded', 'false'); $('use', mb).setAttribute('href', '#i-menu'); mb.focus();
    });
  }

  // photos fade in once decoded
  $$('.ph img').forEach((im) => {
    if (im.complete) return;
    im.classList.add('ld');
    im.addEventListener('load', () => im.classList.remove('ld'), { once: true });
    im.addEventListener('error', () => im.classList.remove('ld'), { once: true });
  });

  // reveal on scroll
  const rv = $$('.rv');
  if (rv.length && 'IntersectionObserver' in window && !calm) {
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
    rv.forEach((el) => io.observe(el));
  } else rv.forEach((el) => el.classList.add('in'));

  // flash map: strikes land oldest first, list and dots light each other
  const radar = $('.radar');
  if (radar) {
    const fls = $$('.map .fl', radar), links = $$('.flist a', radar);
    const light = (id, on) => {
      fls.forEach((f) => f.classList.toggle('hot', on && f.dataset.id === id));
      links.forEach((a) => a.classList.toggle('on', on && a.dataset.id === id));
    };
    links.forEach((a) => {
      a.addEventListener('mouseenter', () => light(a.dataset.id, true));
      a.addEventListener('mouseleave', () => light(a.dataset.id, false));
      a.addEventListener('focus', () => light(a.dataset.id, true));
      a.addEventListener('blur', () => light(a.dataset.id, false));
    });
    fls.forEach((f) => {
      f.addEventListener('mouseenter', () => light(f.dataset.id, true));
      f.addEventListener('mouseleave', () => light(f.dataset.id, false));
    });
    if (!calm) {
      const order = fls.slice().sort((a, b) => a.dataset.t - b.dataset.t);
      order.forEach((f) => { f.style.opacity = '0'; });
      ready(() => order.forEach((f, i) => setTimeout(() => {
        f.style.opacity = '';
        f.classList.add('strike');
        setTimeout(() => f.classList.remove('strike'), 950);
      }, 200 + i * 70)));
    }
  }

  // strike line: tooltip and draw-in
  $$('.sline').forEach((box) => {
    const tip = $('.tip', box);
    $$('a', box).forEach((a) => {
      const show = () => {
        tip.innerHTML = `<time>${a.dataset.when}</time>${a.dataset.h}`;
        const r = $('.plot', box).getBoundingClientRect(), b = $('.bar', a).getBoundingClientRect();
        const x = Math.min(Math.max(b.left - r.left - 20, 0), r.width - 280);
        tip.style.left = Math.max(0, x) + 'px';
        tip.style.bottom = (r.bottom - b.top + 8) + 'px';
        tip.classList.add('on');
      };
      a.addEventListener('mouseenter', show); a.addEventListener('focus', show);
      a.addEventListener('mouseleave', () => tip.classList.remove('on')); a.addEventListener('blur', () => tip.classList.remove('on'));
    });
    if (!calm && 'IntersectionObserver' in window) {
      const bars = $$('.bar', box);
      bars.forEach((b) => { b.style.transformBox = 'fill-box'; b.style.transformOrigin = '50% 100%'; b.style.opacity = '0'; });
      const io = new IntersectionObserver((es) => { if (es[0].isIntersecting) { bars.forEach((b, i) => { b.style.animationDelay = (i * 22) + 'ms'; b.style.opacity = ''; b.classList.add('drawn'); }); io.disconnect(); } }, { threshold: .4 });
      io.observe(box);
    }
  });

  // story: reading progress
  const prog = $('.prog'), body = $('.body');
  if (prog && body) {
    const on = () => {
      const r = body.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (innerHeight * .4 - r.top) / r.height));
      prog.style.transform = `scaleX(${p})`;
    };
    on(); addEventListener('scroll', on, { passive: true });
  }

  // copy link
  $$('[data-copy]').forEach((b) => b.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(location.href.split('?')[0]); b.setAttribute('aria-label', 'Link copied'); b.dataset.ok = ''; setTimeout(() => { b.setAttribute('aria-label', 'Copy link'); delete b.dataset.ok; }, 1600); } catch (e) {}
  }));

  // wire page filters
  const filters = $('.filters');
  if (filters) {
    const items = $$('.feed li'), days = $$('.day');
    filters.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      $$('button', filters).forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      const s = b.dataset.sec;
      items.forEach((li) => { li.hidden = s !== 'all' && li.dataset.sec !== s; });
      days.forEach((dy) => { dy.hidden = !$$('.feed li', dy).some((li) => !li.hidden); });
      const n = items.filter((li) => !li.hidden).length;
      const live = $('#filter-count'); if (live) live.textContent = `${n} ${n === 1 ? 'flash' : 'flashes'}`;
    });
  }

  // search over the edition index
  const sbox = $('#q');
  if (sbox) {
    const out = $('.results'), count = $('#q-count'), base = sbox.dataset.base || '';
    let idx = [];
    fetch(base + 'assets/data/search.json').then((r) => r.json()).then((j) => { idx = j; go(); });
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const mark = (s, ws) => { let h = esc(s); ws.forEach((w) => { if (w.length > 1) h = h.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>'); }); return h; };
    const go = () => {
      const q = sbox.value.trim().toLowerCase();
      const ws = q.split(/\s+/).filter(Boolean);
      history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) : location.pathname);
      if (!ws.length) { out.innerHTML = ''; count.textContent = `${idx.length} stories in this edition`; return; }
      const hits = idx.filter((it) => ws.every((w) => it.k.includes(w)));
      count.textContent = `${hits.length} ${hits.length === 1 ? 'story' : 'stories'} for “${sbox.value.trim()}”`;
      out.innerHTML = '<ul class="rows">' + hits.map((it) => `<li><a class="row" href="${base}${it.u}">${it.p ? `<div class="ph"><img src="${base}${it.p}" alt="" loading="lazy" width="400" height="300"></div>` : '<div class="ph plate"><svg viewBox="0 0 10 10" aria-hidden="true"><path d="M6.2.6 2 5.6h2.9L3.6 9.4 8 4.2H5.1z" fill="currentColor"/></svg></div>'}<div class="txt"><span class="kicker">${esc(it.s)}</span><h2 class="h-s">${mark(it.h, ws)}</h2><p class="dek">${mark(it.d, ws)}</p><span class="meta"><time>${esc(it.w)}</time></span></div></a></li>`).join('') + '</ul>';
    };
    const q0 = new URLSearchParams(location.search).get('q'); if (q0) sbox.value = q0;
    sbox.addEventListener('input', go);
  }

  // alerts and tip forms (prototype: nothing is sent)
  $$('#alerts-form, #tip-form').forEach((f) => f.addEventListener('submit', (e) => {
    e.preventDefault();
    const need = $('[required]', f);
    if (need && !need.value.trim()) { need.setAttribute('aria-invalid', 'true'); need.focus(); return; }
    const done = $('.done', f.parentNode);
    done.classList.add('on'); done.setAttribute('tabindex', '-1'); done.focus();
    $('button[type=submit]', f).disabled = true;
  }));

  // flash map page: filter dots and list by age; a row lights its dot and a dot its row
  const ageF = $('[data-agefilter]');
  if (ageF) {
    const dots = $$('.mapstage .fl'), rows = $$('.maplist li[data-age]'), out = $('#age-count');
    ageF.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      $$('button', ageF).forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
      const max = b.dataset.age === 'all' ? 9 : +b.dataset.age;
      dots.forEach((f) => { f.style.display = +f.dataset.age <= max ? '' : 'none'; });
      rows.forEach((li) => { li.hidden = +li.dataset.age > max; });
      $$('.mgroup').forEach((g) => { const any = $$('li[data-age]', g); if (any.length) g.hidden = any.every((li) => li.hidden); });
      const n = dots.filter((f) => f.style.display !== 'none').length;
      out.textContent = `${n} ${n === 1 ? 'flash' : 'flashes'}`;
    });
    $$('.maplist a[data-id]').forEach((a) => {
      const on = (v) => dots.forEach((f) => f.classList.toggle('hot', v && f.dataset.id === a.dataset.id));
      a.addEventListener('mouseenter', () => on(true)); a.addEventListener('mouseleave', () => on(false));
      a.addEventListener('focus', () => on(true)); a.addEventListener('blur', () => on(false));
    });
    dots.forEach((f) => {
      const a = $(`.maplist a[data-id="${f.dataset.id}"]`);
      f.addEventListener('mouseenter', () => a && a.classList.add('on'));
      f.addEventListener('mouseleave', () => a && a.classList.remove('on'));
    });
  }
})();
