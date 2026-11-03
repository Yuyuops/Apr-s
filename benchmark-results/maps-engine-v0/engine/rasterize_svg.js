// SVG -> PNG with Chromium (playwright of the engine-1 node_modules, read-only dependency). usage: node rasterize_svg.js in.svg out.png [size=512]
const path = require('path');
const nm = process.env.LEGO_NODE_MODULES || path.join(__dirname, '..', '..', '20_portable_engine', 'node_modules');
const { chromium } = require(path.join(nm, 'playwright'));
(async () => {
  const [inp, out, size] = [process.argv[2], process.argv[3], parseInt(process.argv[4] || '512')];
  const svg = require('fs').readFileSync(inp, 'utf8');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: size, height: size } });
  await p.setContent(`<html><body style="margin:0">${svg.replace(/width="\d+" height="\d+"/, `width="${size}" height="${size}"`)}</body></html>`);
  await p.screenshot({ path: out, clip: { x: 0, y: 0, width: size, height: size } }); await b.close();
})();
