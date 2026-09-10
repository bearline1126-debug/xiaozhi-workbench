/* 缓存策略（v84 + v91 两轮血泪史的最终形态，勿改回纯 cache-first）：
   1. install 立即 skipWaiting + 不预缓存 HTML，只预缓存 4 个静态资源（单个失败不阻塞）
   2. activate 强制清掉所有旧 cache
   3. fetch HTML（v143 起）：SWR 快速刷新 —— 先用本地缓存立即渲染，同时后台拉最新；
      网络快(<1.2s)用它返回(部署立即生效)，网络慢则 1.2s 先用缓存顶上(不再白屏)、后台继续更新缓存；
      后台取到更新版本号 ≠ 旧缓存版本号 → 主动刷新窗口一次，配合 index.html 版本自愈清旧缓存。
      仍非 cache-first：后台持续校验版本，避免"部署了用户看不到新版"。
   4. 其他静态资源 cache-first */
const CACHE = 'xiaozhi-workbench-v143';
const ASSETS = ['./manifest.json', './icon.png', './icon-192.png', './assets/welcome-default.jpg', './dict.json'];
const BUILD = '2026-09-10-v143';

const DEFAULT_MANIFEST = {
  name: '拾光手账', short_name: '拾光',
  description: '本地生活记录与个人复盘',
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

  /* HTML（含 navigate）：SWR 快速刷新 + 网络后台更新（v143）
     之前是"网络优先 + 兜底"：每次刷新都阻塞等 GitHub Pages 下完整份 index.html（~4MB，中国访问 github.io 不稳定），
     网络一卡就长时间白屏转圈，甚至最终回退旧缓存 → 又慢、又"看不到新版"。
     现改为：先用本地缓存立即渲染；同时后台拉最新 HTML：
       · 网络快（<1.2s）→ 直接用新版，部署立即生效；
       · 网络慢/挂起 → 1.2s 内先用缓存顶上（刷新飞快不再白屏），后台继续拉取并回填缓存；
       · 后台取到最新版号 ≠ 缓存里的旧版号 → 主动刷新窗口一次，用户无需手动再刷就拿到新版。
   仍不是 cache-first（后台持续校验并更新版本号，配合 index.html 的版本自愈清旧缓存） */
  if (event.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname.endsWith('/')) {
    event.respondWith(
      caches.match('./index.html').then(cached => {
        const network = fetch(event.request, { cache: 'no-store' })
          .then(resp => {
            if (resp && resp.ok) {
              const copy = resp.clone();
              caches.open(CACHE).then(c => c.put('./index.html', copy)).catch(() => {});
              /* 后台自愈：取到的新版号 ≠ 之前缓存服务的旧版号 → 通知窗口刷新一次，让"新版"一次到位 */
              copy.clone().text().then(async t => {
                try {
                  const newV = /BUILD_VERSION = '([^']+)'/.exec(t);
                  if (!newV || !cached) return;
                  let oldV = null;
                  try { const oldT = await cached.clone().text(); const om = /BUILD_VERSION = '([^']+)'/.exec(oldT); oldV = om ? om[1] : null; } catch {}
                  if (oldV !== newV[1]) {
                    const cs = await self.clients.matchAll({ type: 'window' });
                    if (cs.length) cs.forEach(c => { try { c.navigate(c.url); } catch {} });
                  }
                } catch {}
              }).catch(() => {});
            }
            return resp;
          })
          .catch(() => cached);
        if (cached) {
          return Promise.race([network, new Promise(r => setTimeout(() => r(cached), 1200))]);
        }
        return network;
      })
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