const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--autoplay-policy=no-user-gesture-required', '--mute-audio'] });
  const p = await b.newPage(); await p.setViewport({ width: 1400, height: 900 });
  p.on('pageerror', e => console.log('PAGE ERROR', e.message));
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  const st = async l => console.log(l, await p.evaluate(() => [document.getElementById('count').textContent, document.getElementById('talk').textContent, document.getElementById('caption-text').textContent.slice(0, 45)].join(' | ')));
  const wait = ms => new Promise(r => setTimeout(r, ms));
  await p.click('#talk'); await wait(2000); await st('playing      ');
  await p.keyboard.press('ArrowRight'); await wait(1200); await st('after arrow  ');
  await p.keyboard.press('ArrowRight'); await wait(1200); await st('after arrow 2');
  await p.click('#talk'); await wait(2000); await st('resumed      ');
  await p.click('#talk'); await wait(500); await st('paused       ');
  await p.click('#talk'); await wait(1500); await st('resumed again');
  await p.click('#talk-stop'); await wait(500); await st('stopped      ');
  await b.close();
})();
