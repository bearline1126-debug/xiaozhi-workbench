const CACHE = 'xiaozhi-workbench-v36';
const ASSETS = ['./', './index.html', './manifest.json', './icon.png', './icon-192.png', './assets/welcome-default.jpg'];
const BUILD = '2026-08-13-v36';

const DEFAULT_MANIFEST = {
  name: '小彘的工作台', short_name: '小彘',
  description: '小彘的本地个人复盘工作台',
  id: '/xiaozhi-workbench/',
  start_url: './index.html', scope: './', display: 'standalone', display_override: ['standalone','minimal-ui'], orientation: 'portrait',
  background_color: '#eef7ef', theme_color: '#dfead6',
  categories: ['productivity', 'lifestyle', 'utilities'],
  icons: [
    {src: 'icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any maskable'},
    {src: 'icon.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable'}
  ]
};

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

/* 从 IndexedDB 读取用户自定义的 App 名称（图标已下线，不再读取 icon） */
function readAppCustom(){
  return new Promise(resolve => {
    try {
      const q = indexedDB.open('bysdash-media', 1);
      q.onsuccess = () => {
        const db = q.result;
        if(!db.objectStoreNames.contains('files')){ resolve(null); return; }
        const tx = db.transaction('files', 'readonly');
        const r = tx.objectStore('files').get('app_custom');
        r.onsuccess = () => resolve(r.result ? (r.result.data || null) : null);
        r.onerror = () => resolve(null);
      };
      q.onerror = () => resolve(null);
    } catch(e){ resolve(null); }
  });
}

/* 构建动态 manifest：注入用户自定义的 App 名称，图标固定使用默认（自定义图标已下线） */
async function buildManifest(url){
  const custom = await readAppCustom();
  const manifest = {
    name: (custom && custom.name) || DEFAULT_MANIFEST.name,
    short_name: (custom && custom.shortName) || DEFAULT_MANIFEST.short_name,
    description: DEFAULT_MANIFEST.description,
    id: DEFAULT_MANIFEST.id,
    start_url: './index.html', scope: './', display: 'standalone',
    display_override: DEFAULT_MANIFEST.display_override,
    orientation: 'portrait',
    background_color: '#eef7ef', theme_color: '#dfead6',
    categories: DEFAULT_MANIFEST.categories,
    icons: DEFAULT_MANIFEST.icons
  };
  return new Response(JSON.stringify(manifest), {
    headers: {'Content-Type': 'application/manifest+json', 'Cache-Control': 'no-cache'}
  });
}

/* 网络优先策略：HTML 始终尝试拉最新版；其他资源缓存优先 */
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  /* manifest.json：动态注入用户自定义的 App 名称 */
  if (url.pathname.endsWith('manifest.json')) {
    event.respondWith(buildManifest(url));
    return;
  }

  /* HTML 文件：网络优先，确保部署后立即生效 */
  if (url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(event.request)
        .then(resp => {
          const copy = resp.clone();
          caches.open(CACHE).then(cache => cache.put(event.request, copy));
          return resp;
        })
        .catch(() => caches.match(event.request) || caches.match('./index.html'))
    );
    return;
  }

  /* 其他资源：缓存优先（图标、壁纸等） */
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request)
        .then(resp => {
          const copy = resp.clone();
          caches.open(CACHE).then(cache => cache.put(event.request, copy));
          return resp;
        })
        .catch(() => caches.match('./index.html'));
    })
  );
});