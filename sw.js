const CACHE = 'xiaozhi-workbench-v17';
const ASSETS = ['./', './index.html', './manifest.json', './icon.png', './icon-192.png', './assets/welcome-default.jpg'];
const BUILD = '2026-08-11-v17';

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
  );
  self.clients.claim();
});

/* 网络优先策略：HTML 始终尝试拉最新版；其他资源缓存优先 */
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  /* HTML 文件：网络优先，确保部署后立即生效 */
  if (url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(event.request).then(resp => {
        const copy = resp.clone();
        caches.open(CACHE).then(cache => cache.put(event.request, copy));
        return resp;
      }).catch(() => caches.match(event.request) || caches.match('./index.html')))
    );
    return;
  }
  /* 其他资源：缓存优先（图标、manifest、壁纸等） */
  event.respondWith(
    caches.match(event.request).then(hit => hit || fetch(event.request).then(resp => {
      const copy = resp.clone();
      caches.open(CACHE).then(cache => cache.put(event.request, copy));
      return resp;
    }).catch(() => caches.match('./index.html')))
  );
});
