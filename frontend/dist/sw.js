/**
 * Service Worker – VN30 Quant & AI Intelligence PWA
 * Chiến lược cache:
 * - Static assets (JS/CSS/images): Cache-First → tải ngay từ cache, nhanh hơn nhiều
 * - API endpoints (/api/*): Network-First → luôn lấy dữ liệu mới từ server, fallback cache nếu offline
 * - HTML/manifest: Network-First → đảm bảo luôn có giao diện mới nhất
 *
 * Giải quyết lỗi "Safari không thể mở trang vì máy chủ đã dừng phản hồi":
 * SW sẽ cache index.html và static assets → app vẫn load được khi server đang cold-start.
 */

const CACHE_NAME = 'vn30-ai-v1'
const STATIC_CACHE_NAME = 'vn30-static-v1'

// Danh sách tài nguyên tĩnh cần cache ngay khi SW cài đặt
const STATIC_ASSETS = [
  '/',
  '/manifest.webmanifest',
  '/apple-touch-icon.png',
  '/pwa-192x192.png',
  '/pwa-512x512.png',
]

// ==================== CÀI ĐẶT ====================
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE_NAME).then(cache => {
      // Pre-cache các tài nguyên quan trọng
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] Không thể pre-cache một số tài nguyên:', err)
      })
    }).then(() => {
      console.log('[SW] Cài đặt hoàn tất – pre-cache xong.')
      return self.skipWaiting()
    })
  )
})

// ==================== KÍCH HOẠT (dọn cache cũ) ====================
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys
          .filter(k => k !== CACHE_NAME && k !== STATIC_CACHE_NAME)
          .map(k => {
            console.log('[SW] Xóa cache cũ:', k)
            return caches.delete(k)
          })
      )
    }).then(() => {
      console.log('[SW] Kích hoạt hoàn tất – đang kiểm soát tất cả tab.')
      return self.clients.claim()
    })
  )
})

// ==================== CHIẾN LƯỢC FETCH ====================
self.addEventListener('fetch', event => {
  const { request } = event
  const url = new URL(request.url)

  // Bỏ qua các request không phải GET hoặc từ extension
  if (request.method !== 'GET') return
  if (!url.protocol.startsWith('http')) return

  // --- API Endpoints: Network-First (luôn lấy dữ liệu mới, cache là fallback offline) ---
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstWithFallback(request))
    return
  }

  // --- Static Assets (JS/CSS/images trong /assets/): Cache-First ---
  if (url.pathname.startsWith('/assets/') || url.pathname.match(/\.(js|css|png|jpg|svg|woff2?)$/)) {
    event.respondWith(cacheFirstWithNetwork(request))
    return
  }

  // --- HTML / SPA routes: Network-First với fallback index.html ---
  event.respondWith(networkFirstSPA(request))
})

/**
 * Network-First: thử lấy từ mạng, nếu offline → dùng cache.
 * Dùng cho API để luôn có dữ liệu mới nhất.
 */
async function networkFirstWithFallback(request) {
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      // Cache response để dùng offline
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch {
    const cached = await caches.match(request)
    if (cached) return cached
    // Trả về lỗi JSON thay vì lỗi trình duyệt
    return new Response(
      JSON.stringify({ status: 'offline', message: 'Không có kết nối mạng. Đang hiển thị dữ liệu đã cache.' }),
      { headers: { 'Content-Type': 'application/json' } }
    )
  }
}

/**
 * Cache-First: lấy từ cache ngay nếu có, nếu không → lấy từ mạng rồi cache lại.
 * Dùng cho static assets (tốc độ cao).
 */
async function cacheFirstWithNetwork(request) {
  const cached = await caches.match(request)
  if (cached) return cached

  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch {
    return new Response('Tài nguyên không có sẵn khi offline', { status: 503 })
  }
}

/**
 * Network-First cho SPA: thử mạng trước, nếu offline → trả về index.html từ cache.
 * Đảm bảo PWA vẫn load được khi server đang cold-start (vấn đề Render.com).
 */
async function networkFirstSPA(request) {
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE_NAME)
      cache.put(request, networkResponse.clone())
      return networkResponse
    }
  } catch {
    // Mạng thất bại → dùng cache
  }

  // Thử cache theo URL cụ thể
  const cached = await caches.match(request)
  if (cached) return cached

  // Fallback về index.html cho SPA routing
  const indexCached = await caches.match('/')
  if (indexCached) return indexCached

  return new Response(
    '<html><body><h2>Đang kết nối lại với máy chủ...</h2><p>Vui lòng kiểm tra kết nối mạng.</p></body></html>',
    { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
  )
}
