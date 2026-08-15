const CACHE_NAME = 'jft-agro-v12';

/* Do not compete with the first page view by preloading the whole site.
   Static assets are cached on demand by the fetch handler below. */
const SHELL_ASSETS = [];

/* Install: cache shell assets. Skip missing assets gracefully. */
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return Promise.allSettled(
        SHELL_ASSETS.map(url =>
          cache.add(url).catch(err => console.warn('SW cache miss (non-fatal):', url, err))
        )
      );
    }).then(() => self.skipWaiting())
  );
});

/* Activate: remove old caches */
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

/* Fetch: Network-first for HTML (always fresh), Cache-first for assets */
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  /* Only handle same-origin requests */
  if (url.origin !== self.location.origin || e.request.method !== 'GET') return;

  /* Network-first for HTML pages — ensures fresh content */
  if (e.request.destination === 'document' || url.pathname.endsWith('.html')) {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(e.request, clone));
          }
          return res;
        })
        .catch(() => caches.match(e.request).then(r => r || caches.match('/404.html')))
    );
    return;
  }

  /* Cache-first for images and static assets */
  if (url.pathname.match(/\.(webp|png|jpg|jpeg|svg|ico|woff2|woff|css|js|json|pdf)$/)) {
    e.respondWith(
      caches.match(e.request).then((cached) => {
        if (cached) return cached;
        return fetch(e.request).then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(e.request, clone));
          }
          return res;
        });
      })
    );
  }
});
