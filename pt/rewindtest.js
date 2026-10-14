const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'] });
  const p = await b.newPage(); await p.setViewport({ width: 1400, height: 900 });
  p.on('pageerror', e => console.log('PAGE ERROR', e.message));
  await p.evaluateOnNewDocument(() => { const o = HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play = function () { this.playbackRate = 4; window.__a = this; return o.call(this); }; });
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const st = async l => console.log(l, await p.evaluate(() => {
    const w = document.querySelectorAll('.slide')[3].querySelector('.work');
    return [document.getElementById('count').textContent, 'steps ' + w.querySelectorAll('.calc > span.shown').length / 2, 't=' + (window.__a ? window.__a.currentTime.toFixed(1) : '-'), document.getElementById('caption-text').textContent.slice(0, 40)].join(' | ');
  }));
  for (let i = 0; i < 3; i++) await p.keyboard.press('ArrowRight');
  await wait(800);
  await p.click('#talk');
  for (let k = 0; k < 200; k++) { await wait(100); if (await p.evaluate(() => document.getElementById('caption-text').textContent.startsWith('To ask'))) break; }
  await wait(250); await st('at "To ask"   ');
  await p.click('#talk-back'); await wait(300); await st('after -5s     ');
  await p.click('#talk'); await wait(200); await st('paused        ');
  await p.click('#talk-back'); await wait(300); await st('-5s paused    ');
  await p.click('#talk'); await wait(200); await st('resumed       ');
  for (let k = 0; k < 300; k++) { await wait(100); if (await p.evaluate(() => document.getElementById('count').textContent.startsWith('5'))) break; }
  await st('next slide    ');
  await b.close();
})();
