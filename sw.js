const CACHE_NAME = 'jft-agro-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/script.js',
  '/images/jft logo.png',
  '/images/products/basmati_rice_hd.webp',
  '/images/products/spices_hd.webp',
  '/images/products/pulses_hd.webp',
  '/images/homepage/Flag-United-Arab-Emirates.webp',
  '/images/homepage/Flag-Benin.webp',
  '/images/homepage/Flag-Russia.webp',
  '/images/homepage/Flag-Vietnam.webp'
];

// Install Event
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

// Activate Event
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
});

// Fetch Event
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cacheRes) => {
      return cacheRes || fetch(e.request).then((fetchRes) => {
        return caches.open(CACHE_NAME).then((cache) => {
          // Cache new requests dynamically (optional, but good for blogs)
          if (e.request.url.includes('.html') || e.request.url.includes('.webp')) {
            cache.put(e.request.url, fetchRes.clone());
          }
          return fetchRes;
        });
      });
    }).catch(() => {
      if (e.request.url.includes('.html')) {
        return caches.match('/index.html');
      }
    })
  );
});
