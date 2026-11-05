// headless check of step_viewer.html : loads, jumps to steps, counts visible meshes, screenshots. usage: node viewer_check.js viewer.html outdir
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
(async () => {
  const [,, html, out] = process.argv; fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] }); const pg = await b.newPage({ viewport: { width: 800, height: 520 } }); const errs = [];
  pg.on('pageerror', e => errs.push(String(e))); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await pg.goto('file://' + path.resolve(html)); await pg.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });
  const res = {};
  for (const k of [1, 40, 150, 354]) { await pg.evaluate(k => window.__show(k), k); await pg.waitForTimeout(1500); res['step' + k] = { visible: await pg.evaluate(() => window.__visible()), label: await pg.evaluate(() => document.getElementById('lab').textContent) }; await pg.screenshot({ path: path.join(out, 'viewer_step' + k + '.png'), timeout: 90000 }); }
  await pg.click('#prev'); res.after_prev = await pg.evaluate(() => document.getElementById('lab').textContent); res.errors = errs;
  fs.writeFileSync(path.join(out, 'viewer_check.json'), JSON.stringify(res, null, 1)); console.log(JSON.stringify(res)); await b.close();
})();
