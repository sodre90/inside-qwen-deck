const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new' });
  const p = await b.newPage(); await p.setViewport({ width: 1300, height: 900, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.log('PAGE ERROR', e.message));
  await p.goto('file://' + process.argv[2], { waitUntil: 'networkidle0' });
  const el = await p.evaluateHandle(() => { const s = document.getElementById('s12'); s.querySelector('.journey > div:nth-child(3)').classList.add('spot'); return s.querySelector('.journey'); });
  await el.screenshot({ path: process.argv[3] });
  await b.close();
})();
