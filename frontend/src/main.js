import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

createApp(App).mount('#app')

// Đăng ký Service Worker (PWA offline support + cache static assets)
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js', { scope: '/' })
      .then(reg => {
        console.log('[SW] Đăng ký thành công:', reg.scope)
        // Kiểm tra cập nhật SW mỗi khi trang load
        reg.update()
      })
      .catch(err => {
        console.warn('[SW] Đăng ký thất bại:', err)
      })
  })
}
