const fs = require('fs');
const { chromium } = require('playwright');

const pages = [
  'index.html', 'about.html', 'products.html', '1121-basmati-rice-exporter.html',
  'blog.html', 'contact.html', 'quote-calculator.html', 'infrastructure.html'
];

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const results = [];
  for (const viewport of [{name:'mobile',width:390,height:844},{name:'desktop',width:1440,height:1000}]) {
    for (const route of pages) {
      const context = await browser.newContext({ viewport });
      const page = await context.newPage();
      const errors = [];
      page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
      page.on('pageerror', error => errors.push(error.message));
      await page.addInitScript(() => {
        localStorage.setItem('jft_cookie_choice', 'essential');
        window.__auditVitals = { lcp: 0, cls: 0, longTasks: 0 };
        new PerformanceObserver(list => {
          const entries = list.getEntries();
          if (entries.length) window.__auditVitals.lcp = entries[entries.length - 1].startTime;
        }).observe({ type: 'largest-contentful-paint', buffered: true });
        new PerformanceObserver(list => {
          list.getEntries().forEach(entry => { if (!entry.hadRecentInput) window.__auditVitals.cls += entry.value; });
        }).observe({ type: 'layout-shift', buffered: true });
        new PerformanceObserver(list => { window.__auditVitals.longTasks += list.getEntries().length; }).observe({ type: 'longtask', buffered: true });
      });
      const started = Date.now();
      await page.goto(`http://127.0.0.1:8765/${route}`, { waitUntil: 'networkidle', timeout: 45000 });
      await page.waitForTimeout(2500);
      const metrics = await page.evaluate(() => {
        const navigation = performance.getEntriesByType('navigation')[0];
        const paint = Object.fromEntries(performance.getEntriesByType('paint').map(item => [item.name, item.startTime]));
        const resources = performance.getEntriesByType('resource');
        return {
          ...window.__auditVitals,
          fcp: paint['first-contentful-paint'] || 0,
          domContentLoaded: navigation ? navigation.domContentLoadedEventEnd : 0,
          load: navigation ? navigation.loadEventEnd : 0,
          transferKb: Math.round(resources.reduce((sum, item) => sum + (item.transferSize || 0), 0) / 1024),
          resources: resources.length,
          domNodes: document.getElementsByTagName('*').length,
          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
        };
      });
      results.push({ viewport: viewport.name, route, elapsedMs: Date.now() - started, errors, ...metrics });
      await context.close();
    }
  }
  await browser.close();
  fs.writeFileSync('reports/browser-metrics.json', JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
})().catch(error => { console.error(error); process.exit(1); });
