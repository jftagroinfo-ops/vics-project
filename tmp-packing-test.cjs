const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const results = [];
  for (const viewport of [{ name: 'desktop', width: 1440, height: 1000 }, { name: 'mobile', width: 390, height: 844 }]) {
    const page = await browser.newPage({ viewport });
    const errors = [];
    page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(() => localStorage.setItem('jft_cookie_choice', 'essential'));
    await page.goto('http://127.0.0.1:8765/packing-calculator.html', { waitUntil: 'networkidle' });
    await page.waitForSelector('#pack-result-content.show');
    const initial = await page.locator('#result-bags').textContent();
    const layout = await page.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth, h1: document.querySelectorAll('h1').length, header: !!document.querySelector('.main-header'), footer: !!document.querySelector('footer') }));
    if (viewport.name === 'desktop') {
      await page.locator('[data-container="40ft"]').click();
      const forty = await page.locator('#result-bags').textContent();
      await page.locator('#cargo-cap').fill('40000');
      const cappedRef = await page.locator('#stat-route-cap').textContent();
      const warning = await page.locator('#packing-warning-text').textContent();
      await page.locator('#measured-bag').check();
      const measuredVisible = await page.locator('#measured-fields').evaluate(el => getComputedStyle(el).display !== 'none');
      await page.locator('#palletised').check();
      const palletVisible = await page.locator('#pallet-fields').evaluate(el => getComputedStyle(el).display !== 'none');
      results.push({ viewport: viewport.name, initial, forty, cappedRef, warning, measuredVisible, palletVisible, errors, layout });
    } else {
      results.push({ viewport: viewport.name, initial, errors, layout });
    }
    await page.screenshot({ path: `tmp-packing-${viewport.name}-full.png`, fullPage: true });
    await page.close();
  }
  console.log(JSON.stringify(results, null, 2));
  await browser.close();
})().catch(error => { console.error(error); process.exit(1); });
