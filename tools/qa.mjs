// Run the visual-QA probe on many pages and widths through Chrome DevTools Protocol.
// node --experimental-websocket tools/qa.mjs <base-url> <probe.js> <out.json> page1 page2 ... [-- 375,768,1024,1280,1440]
// The loader is marked as seen; each page is scrolled once so lazy images load before the probe runs.
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const args = process.argv.slice(2);
const [base, probePath, out] = args;
const sep = args.indexOf('--');
const pages = args.slice(3, sep < 0 ? undefined : sep);
const widths = (sep < 0 ? '375,768,1024,1280,1440' : args[sep + 1]).split(',').map(Number);
const src = readFileSync(probePath, 'utf8').replace(/^await \(document\.fonts[^\n]*\n/m, '');
const expr = `(async () => { await (document.fonts ? document.fonts.ready : 0); return (
${src.trim().replace(/;?\s*$/, '')}
); })()`;

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const port = 9700 + Math.floor(Math.random() * 200);
const prof = mkdtempSync(join(tmpdir(), 'barq-qa-'));
const proc = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map();
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const results = [];
try {
  let target;
  for (let k = 0; k < 60 && !target; k++) { try { target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((r) => ws.addEventListener('open', r));
  const errors = [];
  ws.addEventListener('message', (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text);
    if (m.method === 'Log.entryAdded' && m.params.entry.level === 'error') errors.push(m.params.entry.text + ' ' + (m.params.entry.url || ''));
  });
  await send('Page.enable'); await send('Runtime.enable'); await send('Log.enable');
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('barq-seen','1')}catch(e){}" });
  for (const w of widths) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: w < 768 ? 812 : 900, deviceScaleFactor: 1, mobile: w < 768 });
    for (const p of pages) {
      errors.length = 0;
      await send('Page.navigate', { url: base + p });
      await sleep(1400);
      const H = (await send('Runtime.evaluate', { expression: 'document.documentElement.scrollHeight', returnByValue: true })).result.value;
      for (let y = 0; y < H; y += 700) { await send('Runtime.evaluate', { expression: `scrollTo(0,${y})` }); await sleep(60); }
      await send('Runtime.evaluate', { expression: 'scrollTo(0,0)' }); await sleep(300);
      const r = await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true });
      results.push({ page: p, w, errors: [...errors], probe: r.result.value || r.exceptionDetails?.text });
    }
  }
} finally { try { ws && ws.close(); } catch {} proc.kill(); }
writeFileSync(out, JSON.stringify(results, null, 1));
console.log('probed', results.length, 'page-widths ->', out);
