const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new' });
  const p = await b.newPage(); await p.setViewport({ width: 1400, height: 900 });
  p.on('pageerror', e => console.log('PAGE ERROR', e.message));
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  const work = await p.evaluateHandle(() => [...document.querySelectorAll('.slide')].find(s => s.dataset.sec === 'I. Sampling').querySelector('.work'));
  for (let i = 0; i < 5; i++) {
    await p.evaluate(w => w.querySelectorAll('.stepctl button')[1].click(), work);
    await new Promise(r => setTimeout(r, 300));
    console.log(await p.evaluate(w => { const s = w.querySelectorAll('.calc > span.shown'); return (s.length / 2) + ' shown, lit rows: ' + [...w.querySelectorAll('tr.lit td:first-child')].map(td => td.textContent).join(',') + ' | ' + s[s.length - 1].textContent.slice(0, 70); }, work));
  }
  await b.close();
})();
