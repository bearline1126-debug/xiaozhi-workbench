/* v84：彻底修"部署了用户看不到"问题
   1. install 立即 skipWaiting + 不预缓存任何资源
   2. activate 强制清掉所有旧 cache（包括自己当前的 HTML 缓存）
   3. fetch HTML 永远走网络，**永不缓存 HTML**（避免下次又命中旧版） */
const CACHE = 'xiaozhi-workbench-v84';
const ASSETS = ['./manifest.json', './icon.png', './icon-192.png', './assets/welcome-default.jpg'];
const BUILD = '2026-08-20-v84';

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
  /* 不预缓存 HTML（避免下次又命中旧 HTML）
     只预缓存静态资源（图标、壁纸），并且用 BUG 处理：旧 install 用 cache.addAll 会阻塞 SW 升级，
     改成 cache.add（单个失败不阻塞） */
  event.waitUntil(
    caches.open(CACHE).then(cache => Promise.all(ASSETS.map(a => cache.add(a).catch(() => null))))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  /* 强制清掉所有旧 cache（包括当前 scope 里所有非 v84 的 cache） */
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
    background_color: DEFAULT_MANIFEST.background_color, theme_color: DEFAULT_MANIFEST.theme_color,
    categories: DEFAULT_MANIFEST.categories,
    icons: DEFAULT_MANIFEST.icons
  };
  return new Response(JSON.stringify(manifest), {
    headers: {'Content-Type': 'application/manifest+json', 'Cache-Control': 'no-cache'}
  });
}

self.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate') {
    /* navigation 请求永远走网络，不缓存 */
    event.respondWith(
      fetch(event.request, { cache: 'no-store' }).catch(() => caches.match('./index.html'))
    );
    return;
  }
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  /* manifest.json：动态注入用户自定义的 App 名称 */
  if (url.pathname.endsWith('manifest.json')) {
    event.respondWith(buildManifest(url));
    return;
  }

  /* HTML：永远走网络，不缓存到 cache（解决"部署了用户看到还是旧版"的核心问题） */
  if (url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' }).catch(() => caches.match('./index.html'))
    );
    return;
  }

  /* 其他静态资源：缓存优先 */
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