const CACHE = 'xiaozhi-workbench-v24';
const ASSETS = ['./', './index.html', './manifest.json', './icon.png', './icon-192.png', './assets/welcome-default.jpg'];
const BUILD = '2026-08-12-v24';

const DEFAULT_MANIFEST = {
  name: '小彘的工作台', short_name: '小彘',
  description: '小彘的本地个人复盘工作台',
  start_url: './index.html', scope: './', display: 'standalone', orientation: 'portrait',
  background_color: '#eef7ef', theme_color: '#dfead6',
  categories: ['productivity', 'lifestyle', 'utilities'],
  icons: [
    {src: 'icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any'},
    {src: 'icon.png', sizes: '512x512', type: 'image/png', purpose: 'any'}
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

/* 从 IndexedDB 读取用户自定义的 App 名称/图标 */
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

/* 将 data URL 转为 Blob（用于 SW 响应） */
function dataUrlToBlob(dataUrl){
  if(!dataUrl || !dataUrl.startsWith('data:')) return null;
  const [header, base64] = dataUrl.split(',');
  if(!base64) return null;
  const mime = header.match(/:(.*?);/)?.[1] || 'image/png';
  const bin = atob(base64);
  const bytes = new Uint8Array(bin.length);
  for(let i=0;i<bin.length;i++) bytes[i]=bin.charCodeAt(i);
  return new Blob([bytes], {type: mime});
}

/* 从 IDB 取出自定义图标，返回 Response（供 /custom-icon.png 拦截用） */
async function serveCustomIcon(){
  const custom = await readAppCustom();
  if(custom && custom.icon){
    const blob = dataUrlToBlob(custom.icon);
    if(blob) return new Response(blob, {
      headers: {'Content-Type': blob.type || 'image/png', 'Cache-Control': 'no-store'}
    });
  }
  /* 无自定义图标：回退到默认 512 图标 */
  return (await caches.match('./icon.png')) || new Response('', {status: 404});
}

/* 构建动态 manifest：名称可自定义；图标用 /custom-icon.png 路径（不用 data URL！） */
async function buildManifest(url){
  const custom = await readAppCustom();
  if(custom && (custom.name || custom.shortName)){
    const hasIcon = !!(custom && custom.icon);
    const manifest = {
      name: custom.name || DEFAULT_MANIFEST.name,
      short_name: custom.shortName || DEFAULT_MANIFEST.short_name,
      description: DEFAULT_MANIFEST.description,
      start_url: './index.html', scope: './', display: 'standalone', orientation: 'portrait',
      background_color: '#eef7ef', theme_color: '#dfead6',
      categories: DEFAULT_MANIFEST.categories,
      icons: hasIcon ? [
        {src: './custom-icon.png', sizes: '512x512', type: 'image/png', purpose: 'any'},
        {src: './icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any'}
      ] : DEFAULT_MANIFEST.icons
    };
    return new Response(JSON.stringify(manifest), {
      headers: {'Content-Type': 'application/manifest+json', 'Cache-Control': 'no-cache'}
    });
  }
  /* 无自定义：回退到静态 manifest（缓存或网络） */
  return (await caches.match(url.href)) || fetch(url.href);
}

/* 网络优先策略：HTML 始终尝试拉最新版；其他资源缓存优先 */
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);

  /* 自定义图标：从 IndexedDB 读取并返回图片（关键修复！不再用 data URL） */
  if (url.pathname.endsWith('custom-icon.png')) {
    event.respondWith(serveCustomIcon());
    return;
  }

  /* manifest.json：动态注入用户自定义的 App 名称/图标路径 */
  if (url.pathname.endsWith('manifest.json')) {
    event.respondWith(buildManifest(url));
    return;
  }

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
  /* 其他资源：缓存优先（图标、壁纸等） */
  event.respondWith(
    caches.match(event.request).then(hit => hit || fetch(event.request).then(resp => {
      const copy = resp.clone();
      caches.open(CACHE).then(cache => cache.put(event.request, copy));
      return resp;
    }).catch(() => caches.match('./index.html')))
  );
});
