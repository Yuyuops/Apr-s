// HTML -> PDF with Chromium (playwright from engine-1 node_modules). usage: node html2pdf.js in.html out.pdf
const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage(); await p.goto('file://' + require('path').resolve(process.argv[2])); await p.waitForTimeout(500);
  await p.pdf({ path: process.argv[3], format: 'A4', landscape: true, printBackground: true, margin: { top: '10mm', bottom: '10mm', left: '10mm', right: '10mm' } }); await b.close(); })();
