const CACHE_NAME = 'aquality-v1';
const ASSETS = [
  './dashboard.html',
  './manifest.json',
  './icono.png'
];

// Instalar y guardar archivos básicos
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)));
});

// Responder desde la memoria si no hay red
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(res => res || fetch(e.request)));
});