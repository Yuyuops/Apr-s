// opens viewer.html headlessly, clicks a part and prints the identification panel ; usage: node viewer_check.js viewer.html shot.png
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'] }); const p = await b.newPage({ viewport: { width: 1200, height: 800 } }); const errs = []; p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + require('path').resolve(process.argv[2])); await p.waitForFunction('window.__ready===true', { timeout: 30000 }).catch(() => {}); await p.waitForTimeout(1500);
  await p.click('#top'); await p.waitForTimeout(600); await p.mouse.click(600, 400); await p.waitForTimeout(400); const info = await p.textContent('#info');
  await p.fill('#layer', '4').catch(() => {}); await p.dispatchEvent('#layer', 'input').catch(() => {}); await p.waitForTimeout(400); const lab = await p.textContent('#lab');
  await p.click('#persp'); await p.waitForTimeout(500); await p.screenshot({ path: process.argv[3] }); console.log(JSON.stringify({ erreurs_console: errs, clic_identifie: info.slice(0, 120), curseur_couches: lab })); await b.close(); })();
