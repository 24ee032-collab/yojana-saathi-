// Caches the app shell so it opens fast and works with a weak connection.
const CACHE = 'yojana-v4';
const SHELL = ['/', '/finder.html', '/css/style.css', '/css/home.css', '/img/red-fort.jpg', '/js/i18n.js', '/js/icons.js', '/js/speech.js', '/js/home.js', '/js/app.js', '/icon-192.png'];
self.addEventListener('install', e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== CACHE).map(x => caches.delete(x)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  // API: always network. Pages and files: network first, cache as fallback.
  if (url.pathname.startsWith('/api')) return;
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; }).catch(() => caches.match(e.request)));
});
