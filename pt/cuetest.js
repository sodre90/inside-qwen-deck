const puppeteer = require('puppeteer-core');
const [file, startSlide = '0', seconds = '40', rate = '1'] = process.argv.slice(2);
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1400, height: 900 });
  p.on('console', m => { if (m.type() === 'error') console.log('CONSOLE ERROR', m.text()); });
  p.on('pageerror', e => console.log('PAGE ERROR', e.message));
  await p.evaluateOnNewDocument(r => { const orig = HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play = function () { this.playbackRate = r; return orig.call(this); }; }, +rate);
  await p.goto('file://' + file, { waitUntil: 'load' });
  if (+startSlide) { for (let i = 0; i < +startSlide; i++) await p.keyboard.press('ArrowRight'); await new Promise(r => setTimeout(r, 800)); }
  await p.click('#talk');
  let last = '';
  for (let t = 0; t < +seconds * 2; t++) {
    await new Promise(r => setTimeout(r, 500));
    const s = await p.evaluate(() => {
      const tip = document.getElementById('tipbox');
      const why = window.__why || ''; const work = [...document.querySelectorAll('.work.stepping')].map(w => w.querySelectorAll('.calc > span.shown').length / 2).join(',');
      return [document.getElementById('count').textContent, document.getElementById('talk').textContent,
        tip && !tip.hidden ? 'tip:' + tip.querySelector('.tt').textContent : '', 'steps[' + work + ']',
        document.querySelector('svg.gd.running') ? 'gd-running' : '', document.getElementById('att-play').textContent === 'Stop' ? 'att-playing' : '',
        'T=' + document.getElementById('temp').value, (document.querySelector('.spot')?.querySelector('b')?.textContent ?? ''), document.getElementById('moe-play').textContent === 'Stop' ? 'moe-playing' : '', 'y=' + Math.round(scrollY),
        (document.getElementById('caption').hidden ? '(no caption)' : document.getElementById('caption-text').textContent.slice(0, 50))].filter(Boolean).join(' | ');
    });
    if (s !== last) { console.log((t / 2).toFixed(1) + 's', s); last = s; }
  }
  await b.close();
})();
