// Keyboard walk through Chrome DevTools Protocol: press Tab n times and report what holds focus and where it is.
// node --experimental-websocket tools/keys.mjs <url> [tabs=12] [width=1280]
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, n = '12', w = '1280'] = process.argv.slice(2);
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9500 + Math.floor(Math.random() * 150);
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'barq-keys-'))}`, '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
try {
  let t;
  for (let k = 0; k < 60 && !t; k++) { try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: 900, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('barq-seen','1')}catch(e){}" });
  await send('Page.navigate', { url });
  await sleep(1800);
  for (let i = 0; i < +n; i++) {
    await send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
    await sleep(260);
    const r = await send('Runtime.evaluate', { returnByValue: true, expression: `(() => { const e = document.activeElement; const b = e.getBoundingClientRect(); const cs = getComputedStyle(e);
      const name = (e.getAttribute('aria-label') || e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 40);
      return { tag: e.tagName.toLowerCase(), cls: (e.className && e.className.baseVal !== undefined ? e.className.baseVal : e.className || '').toString().slice(0, 24), name,
        inView: b.bottom > 0 && b.top < innerHeight && b.right > 0 && b.left < innerWidth, outline: cs.outlineStyle !== 'none' ? cs.outlineWidth + ' ' + cs.outlineColor : 'none', y: Math.round(b.top) }; })()` });
    console.log(String(i + 1).padStart(2), JSON.stringify(r.result.value));
  }
} finally { try { ws && ws.close(); } catch {} proc.kill(); }
