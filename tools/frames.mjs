// Timed frames through Chrome DevTools Protocol (loader QA). MARKS=ms,ms,... env.
// node --experimental-websocket tools/shot.mjs <url> <out.png> [width] [height] [full|view|segments] [light|dark]
// The loader is marked as already heard so the capture shows the settled page; ?loader forces it.
import { spawn } from 'node:child_process';
import { mkdtempSync } from 'node:fs';
import { writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, out, w = '1440', h = '900', mode = 'full', scheme = 'light'] = process.argv.slice(2);
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9300 + Math.floor(Math.random() * 400);
const prof = mkdtempSync(join(tmpdir(), 'barq-shot-'));
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let ws, id = 0; const pending = new Map();
function send(method, params = {}) {
  return new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
}
try {
  let target;
  for (let k = 0; k < 50; k++) {
    try { const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); target = list.find((t) => t.type === 'page'); if (target) break; } catch {}
    await sleep(150);
  }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); } });
  await send('Page.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: +w, height: +h, deviceScaleFactor: 1, mobile: +w < 768 });
  await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: scheme }] });
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('barq-seen','1')}catch(e){}" });
  // frames mode: capture at the given ms marks after navigation (for the loader)
  const marks = (process.env.MARKS || '300,600,900,1300,2600').split(',').map(Number);
  await send('Page.navigate', { url });
  const t0 = Date.now();
  for (const [i, ms] of marks.entries()) {
    await sleep(Math.max(0, ms - (Date.now() - t0)));
    const shot = await send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(out.replace(/\.png$/, `-f${i}.png`), Buffer.from(shot.data, 'base64'));
  }
  console.log('frames', marks.length);
} finally {
  try { ws && ws.close(); } catch {}
  proc.kill();
}
