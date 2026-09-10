<template>
  <nav class="border-b border-theme-border bg-theme-card/90 backdrop-blur-md sticky top-0 z-40 transition-colors duration-200">
    <!-- Widescreen Container: Tối ưu co giãn trên điện thoại và màn hình rộng -->
    <div class="w-full max-w-[95%] xl:max-w-[88%] 2xl:max-w-[82%] mx-auto px-3 sm:px-6 h-14 sm:h-16 flex items-center justify-between">
      
      <!-- Logo & Title -->
      <div class="flex items-center space-x-2 sm:space-x-3 min-w-0">
        <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 shrink-0">
          <TrendingUp class="w-4 h-4 sm:w-6 sm:h-6 text-slate-950 stroke-[2.5]" />
        </div>
        <div class="min-w-0 truncate">
          <div class="flex items-center gap-1.5 sm:gap-2">
            <h1 class="text-sm sm:text-base font-bold tracking-tight text-theme-text truncate">
              VN30 QUANT & AI
            </h1>
            <span class="hidden sm:inline-block text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30">
              FINANCE PRO
            </span>
          </div>
          <p class="text-[10px] sm:text-[11px] text-theme-text-muted hidden sm:block truncate">
            Nền tảng Phân tích Định lượng & Machine Learning Dự báo T+3
          </p>
        </div>
      </div>

      <!-- Right Controls: Session Status + Auto-Refresh Status + Theme Toggle + VN-INDEX Pill + API Docs -->
      <div class="flex items-center gap-1.5 sm:gap-2.5 shrink-0">
        
        <!-- Market Trading Session Pill (Phiên 9h-15h vs Đã đóng phiên) -->
        <div 
          v-if="marketData?.market_schedule"
          class="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl text-[11px] sm:text-xs font-semibold shadow-sm transition"
          :class="marketData.market_schedule.is_trading 
            ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400' 
            : 'bg-theme-subtle border border-theme-border text-theme-sub'"
          :title="`${marketData.market_schedule.session_name}: ${marketData.market_schedule.detail}\n• Cổ phiếu: Quét trong giờ (09:00 - 15:00)\n• Tin tức & Rủi ro: Cập nhật 24/7 Real-time`"
        >
          <span 
            class="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full shrink-0"
            :class="marketData.market_schedule.is_trading ? 'bg-emerald-500 animate-ping' : 'bg-slate-400'"
          ></span>
          <span class="hidden md:inline">{{ marketData.market_schedule.session_name }}</span>
          <span class="md:hidden">{{ marketData.market_schedule.is_trading ? 'Mở' : 'Đóng' }}</span>
        </div>

        <!-- Live Auto-Refresh Status Pill -->
        <div 
          class="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-600 dark:text-cyan-400 text-[11px] sm:text-xs font-mono font-medium shadow-sm"
          :title="`Tự động làm mới dữ liệu mỗi ${refreshInterval}s (Cổ phiếu 9h-15h | Tin tức 24/7)`"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></span>
          <span class="hidden sm:inline">Làm mới:</span>
          <span class="font-bold">{{ countdown }}s</span>
        </div>

        <!-- Dark / Light Theme Toggle Button -->
        <button 
          @click="toggleTheme" 
          class="flex items-center gap-1 sm:gap-1.5 p-1.5 sm:px-3 sm:py-1.5 rounded-xl bg-theme-subtle hover:bg-theme-card-hover text-theme-text border border-theme-border text-xs font-semibold transition shadow-sm"
          :title="isDark ? 'Chuyển sang chế độ Sáng' : 'Chuyển sang chế độ Tối'"
        >
          <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
          <Moon v-else class="w-4 h-4 text-indigo-500" />
          <span class="hidden md:inline">{{ isDark ? 'Sáng' : 'Tối' }}</span>
        </button>

        <!-- VN-INDEX Pill (Ẩn trên điện thoại để tránh chật chội, đã có card riêng ở trang chủ) -->
        <div v-if="marketData" class="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-theme-subtle border border-theme-border text-xs shadow-inner">
          <span class="text-theme-muted font-semibold">VN-INDEX:</span>
          <span class="font-mono font-bold text-theme-text">
            {{ formatNumber(marketData.vnindex_close) }}
          </span>
          <span 
            class="font-mono font-bold flex items-center"
            :class="marketData.vnindex_change_pct >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400'"
          >
            {{ marketData.vnindex_change_pct >= 0 ? '+' : '' }}{{ marketData.vnindex_change_pct?.toFixed(2) }}%
          </span>
        </div>

        <!-- API Docs link (Relative link /docs) -->
        <a 
          href="/docs" 
          target="_blank" 
          class="hidden lg:flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30 text-xs font-mono font-semibold hover:bg-cyan-500/20 transition"
        >
          <span>Swagger</span>
          <ExternalLink class="w-3 h-3" />
        </a>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { TrendingUp, ExternalLink, Sun, Moon } from 'lucide-vue-next'

defineProps({
  marketData: {
    type: Object,
    default: null
  },
  countdown: {
    type: Number,
    default: 60
  },
  refreshInterval: {
    type: Number,
    default: 60
  }
})

const isDark = ref(true)

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'light') {
    isDark.value = false
    document.documentElement.classList.remove('dark')
    document.documentElement.classList.add('light')
  } else {
    isDark.value = true
    document.documentElement.classList.add('dark')
    document.documentElement.classList.remove('light')
  }
})

function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    document.documentElement.classList.remove('light')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    document.documentElement.classList.add('light')
    localStorage.setItem('theme', 'light')
  }
}

function formatNumber(val) {
  if (!val) return '--'
  return Number(val).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
