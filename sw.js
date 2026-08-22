/* 缓存策略（v84 + v91 两轮血泪史的最终形态，勿改回 cache-first）：
   1. install 立即 skipWaiting + 不预缓存 HTML，只预缓存 4 个静态资源（单个失败不阻塞）
   2. activate 强制清掉所有旧 cache
   3. fetch HTML：网络优先 + 缓存兜底（SWR）——网络成功回填缓存（部署立即生效），
      失败回退缓存副本（弱网/离线不白屏。v84 的"纯不缓存"曾导致网络不稳时白屏，v91 修复）
   4. 其他静态资源 cache-first */
const CACHE = 'xiaozhi-workbench-v96';
const ASSETS = ['./manifest.json', './icon.png', './icon-192.png', './assets/welcome-default.jpg'];
const BUILD = '2026-08-22-v96';

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
  /* 强制清掉所有旧 cache（只保留当前版本 CACHE） */
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
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  /* manifest.json：动态注入用户自定义的 App 名称 */
  if (url.pathname.endsWith('manifest.json')) {
    event.respondWith(buildManifest(url));
    return;
  }

  /* HTML（含 navigate）：SWR 策略 —— 网络优先拿最新（部署立即生效），同时缓存一份用于离线/网络失败兜底
     v91：修 v84 引入的回归 bug（HTML 永不缓存 → 网络不稳时 fetch 失败、缓存里又没有 → 白屏打不开） */
  if (event.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(event.request, { cache: 'no-store' })
        .then(resp => {
          if (resp && resp.ok) {
            const copy = resp.clone();
            caches.open(CACHE).then(c => c.put('./index.html', copy)).catch(() => {});
          }
          return resp;
        })
        .catch(() => caches.match('./index.html'))
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