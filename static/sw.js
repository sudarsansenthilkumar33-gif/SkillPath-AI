// SkillPath AI — Progressive Web App Service Worker
// Enables offline resilience, instant mobile loading, and PWA standalone experience.

const CACHE_NAME = 'skillpath-ai-v1.0.0';

// Core static assets to precache on install
const PRECACHE_URLS = [
  '/',
  '/login',
  '/manifest.json',
  '/static/style.css',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

// External assets to opportunistically cache
const EXTERNAL_URLS = [
  'https://cdn.tailwindcss.com',
  'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install Event: precache core app shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      // Precache local app assets
      for (const url of PRECACHE_URLS) {
        try {
          await cache.add(url);
        } catch (err) {
          console.warn('[SW] Precache skipped for:', url, err);
        }
      }
      // Attempt caching external CDNs
      for (const extUrl of EXTERNAL_URLS) {
        try {
          const req = new Request(extUrl, { mode: 'cors' });
          const res = await fetch(req);
          if (res && res.status === 200) {
            await cache.put(req, res);
          }
        } catch (e) {
          // CDN fetch during install can be optional
        }
      }
    }).then(() => self.skipWaiting())
  );
});

// Activate Event: purge stale caches and claim clients immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => {
          console.log('[SW] Purging outdated cache:', key);
          return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event: Intelligent Cache & Network Strategy
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);

  // Skip non-GET requests and browser extensions
  if (request.method !== 'GET' || !url.protocol.startsWith('http')) {
    return;
  }

  // 1. Static Assets (CSS, Icons, Fonts, Manifest): Cache-first with background revalidation
  if (
    url.pathname.startsWith('/static/') ||
    url.pathname === '/manifest.json' ||
    url.hostname.includes('fonts.googleapis.com') ||
    url.hostname.includes('fonts.gstatic.com') ||
    url.hostname.includes('cdn.jsdelivr.net') ||
    url.hostname.includes('cdn.tailwindcss.com')
  ) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          // Update cache in background
          fetch(request).then((networkResponse) => {
            if (networkResponse && networkResponse.status === 200) {
              caches.open(CACHE_NAME).then((cache) => cache.put(request, networkResponse));
            }
          }).catch(() => {});
          return cachedResponse;
        }

        return fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // 2. HTML Navigation & API Requests: Network-first with cache fallback
  event.respondWith(
    fetch(request)
      .then((networkResponse) => {
        // Cache successful page navigations
        if (request.mode === 'navigate' && networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
        }
        return networkResponse;
      })
      .catch(async () => {
        // Fallback to cache if offline
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
          return cachedResponse;
        }

        // Offline navigation fallback
        if (request.mode === 'navigate') {
          const loginCached = await caches.match('/login');
          if (loginCached) return loginCached;

          return new Response(
            `<!DOCTYPE html>
            <html lang="en">
            <head>
              <meta charset="utf-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>SkillPath AI — Offline</title>
              <style>
                body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; text-align: center; padding: 1.5rem; }
                .box { background: #1e293b; padding: 2.5rem; border-radius: 1rem; border: 1px solid #334155; max-width: 420px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }
                h1 { font-size: 1.5rem; margin-bottom: 0.75rem; color: #38bdf8; }
                p { color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 1.5rem; }
                button { background: #2563eb; color: #fff; border: none; padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
                button:hover { background: #1d4ed8; }
              </style>
            </head>
            <body>
              <div class="box">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
                <h1>SkillPath AI is Offline</h1>
                <p>You appear to be disconnected from the internet. Reconnect to resume live multi-agent career intelligence.</p>
                <button onclick="window.location.reload()">Retry Connection</button>
              </div>
            </body>
            </html>`,
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          );
        }
      })
  );
});
