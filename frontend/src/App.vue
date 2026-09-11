<template>
  <div class="min-h-screen min-h-[100dvh] bg-theme-bg text-theme-text flex font-sans transition-colors duration-200">
    
    <!-- Sidebar Navigation bên lề trái (ở đúng vị trí ô đỏ bạn khoanh) -->
    <Sidebar 
      :active-tab="currentTab" 
      @select-tab="handleSelectTab" 
    />

    <!-- Khung nội dung chính bên phải -->
    <div class="flex-1 flex flex-col min-w-0">
      
      <!-- Top Navbar Header -->
      <Navbar 
        :market-data="marketData" 
        :countdown="countdown"
        :refresh-interval="refreshInterval"
      />

      <!-- Main Content Area: Rộng rãi, tối ưu khoảng đệm mobile & desktop -->
      <main class="flex-1 w-full max-w-[95%] xl:max-w-[92%] 2xl:max-w-[88%] mx-auto px-3 sm:px-6 py-4 sm:py-6 pb-24 md:pb-8 space-y-4 sm:space-y-6">
        
        <!-- API Offline Warning Alert (If Backend Not Running) -->
        <div 
          v-if="isApiOffline" 
          class="p-3.5 sm:p-4 rounded-2xl bg-rose-50 dark:bg-rose-500/10 border border-rose-200 dark:border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm"
        >
          <div class="flex items-center gap-2">
            <AlertCircle class="w-4 h-4 text-rose-500 shrink-0" />
            <span>
              Không thể kết nối đến máy chủ FastAPI tại <code class="font-mono bg-white dark:bg-slate-900 px-1.5 py-0.5 rounded border border-rose-200 dark:border-rose-800">http://127.0.0.1:8000</code>. Vui lòng đảm bảo <code class="font-mono text-cyan-600 dark:text-cyan-300 bg-white dark:bg-slate-900 px-1.5 py-0.5 rounded border border-rose-200 dark:border-rose-800">python api_server.py</code> đang chạy.
            </span>
          </div>
          <button 
            @click="loadData(false)" 
            class="px-3 py-1 rounded-xl bg-rose-500/10 dark:bg-rose-500/20 hover:bg-rose-500/20 text-rose-700 dark:text-white font-semibold transition border border-rose-300 dark:border-rose-500/40"
          >
            Thử lại
          </button>
        </div>

        <!-- ==================== TAB 1: THỊ TRƯỜNG VN30 (DASHBOARD) ==================== -->
        <template v-if="currentTab === 'dashboard'">
          <!-- Loading State (Chỉ hiện khi nạp trang lần đầu) -->
          <div v-if="isLoading && !marketData" class="py-20 text-center space-y-3">
            <div class="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p class="text-xs text-slate-500 dark:text-slate-400 font-mono">Đang nạp dữ liệu định lượng và mô hình AI...</p>
          </div>

          <template v-else>
            <!-- Market Overview (4 Cards) -->
            <MarketOverview 
              :market-data="marketData" 
              :top-stock="topStock" 
              :flow-summary="flowSummaryData"
              @open-report="openRecommendationReport"
              @open-flow-report="openFlowReport"
            />

            <!-- Leaderboard Table -->
            <Leaderboard 
              :stocks="stocks" 
              @select-stock="openStockModal" 
            />
          </template>
        </template>

        <!-- ==================== TAB 2: TIN TỨC THỊ TRƯỜNG ==================== -->
        <template v-else-if="currentTab === 'news'">
          <NewsFeed :key="newsRefreshKey" />
        </template>

        <!-- ==================== TAB 3: BÁO CÁO ĐÁNH GIÁ RỦI RO ==================== -->
        <template v-else-if="currentTab === 'risk'">
          <NewsRiskReport :key="riskRefreshKey" />
        </template>

      </main>

      <!-- Footer -->
      <footer class="border-t border-theme-border py-4 pb-24 md:pb-6 text-center text-xs text-theme-muted font-mono mt-4 transition-colors duration-200">
        <p>&copy; 2026 VN30 Quantitative & AI Intelligence Platform. All rights reserved.</p>
      </footer>
    </div>

    <!-- Modals (Đặt ngoài flex-1 để không bị ảnh hưởng ngữ cảnh hiển thị) -->
    <!-- Market Recommendation Report Modal (Báo cáo Phân bổ % & Lý do VN30) -->
    <MarketReportModal 
      :is-open="isReportModalOpen"
      :report-data="recommendationReportData"
      :is-loading="isLoadingReport"
      @close="isReportModalOpen = false"
      @select-stock="openStockModal"
    />

    <!-- Market Trading Flow Modal (Báo cáo Khối Ngoại & Trong Nước VN30 Hôm nay, 1 tuần, 1 tháng) -->
    <MarketFlowModal 
      :is-open="isFlowModalOpen"
      @close="isFlowModalOpen = false"
      @select-stock="openStockModal"
    />

    <!-- Stock Detail Modal with TradingView Charts (Hiển thị nổi lên trên các báo cáo) -->
    <StockModal 
      :is-open="isModalOpen" 
      :stock="selectedStock" 
      @close="closeStockModal" 
    />

    <!-- Mobile Bottom Navigation Bar (Thanh điều hướng cố định chân trang trên điện thoại) -->
    <nav 
      class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-t border-theme-border flex items-center justify-around px-3 pt-2 pb-safe shadow-[0_-4px_20px_rgba(0,0,0,0.08)] dark:shadow-[0_-4px_20px_rgba(0,0,0,0.45)] select-none"
      style="padding-bottom: max(0.5rem, calc(0.5rem + env(safe-area-inset-bottom, 0px))); -webkit-transform: translateZ(0); transform: translateZ(0);"
    >
      <!-- Tab 1: Thị Trường VN30 -->
      <button 
        @click="handleSelectTab('dashboard')"
        class="flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition relative"
        :class="currentTab === 'dashboard' ? 'text-cyan-500 font-bold' : 'text-theme-sub hover:text-theme-text'"
      >
        <LayoutDashboard class="w-5 h-5" />
        <span class="text-[11px] tracking-tight">Thị Trường</span>
        <span v-if="currentTab === 'dashboard'" class="w-1 h-1 rounded-full bg-cyan-500 absolute -bottom-0.5"></span>
      </button>

      <!-- Tab 2: Tin Tức Thị Trường -->
      <button 
        @click="handleSelectTab('news')"
        class="flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition relative"
        :class="currentTab === 'news' ? 'text-cyan-500 font-bold' : 'text-theme-sub hover:text-theme-text'"
      >
        <div class="relative">
          <Newspaper class="w-5 h-5" />
          <span class="w-2 h-2 rounded-full bg-rose-500 absolute -top-0.5 -right-0.5"></span>
        </div>
        <span class="text-[11px] tracking-tight">Tin Tức</span>
        <span v-if="currentTab === 'news'" class="w-1 h-1 rounded-full bg-cyan-500 absolute -bottom-0.5"></span>
      </button>

      <!-- Tab 3: Đánh Giá Rủi Ro -->
      <button 
        @click="handleSelectTab('risk')"
        class="flex flex-col items-center gap-1 py-1 px-3 rounded-xl transition relative"
        :class="currentTab === 'risk' ? 'text-cyan-500 font-bold' : 'text-theme-sub hover:text-theme-text'"
      >
        <ShieldAlert class="w-5 h-5" />
        <span class="text-[11px] tracking-tight">Rủi Ro AI</span>
        <span v-if="currentTab === 'risk'" class="w-1 h-1 rounded-full bg-cyan-500 absolute -bottom-0.5"></span>
      </button>
    </nav>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { AlertCircle, ShieldAlert, LayoutDashboard, Newspaper } from 'lucide-vue-next'
import Sidebar from './components/Sidebar.vue'
import Navbar from './components/Navbar.vue'
import MarketOverview from './components/MarketOverview.vue'
import Leaderboard from './components/Leaderboard.vue'
import StockModal from './components/StockModal.vue'
import MarketReportModal from './components/MarketReportModal.vue'
import MarketFlowModal from './components/MarketFlowModal.vue'
import NewsFeed from './components/NewsFeed.vue'
import NewsRiskReport from './components/NewsRiskReport.vue'
import { 
  fetchMarketOverview, 
  fetchVN30Leaderboard, 
  fetchMarketRecommendationReport, 
  fetchMarketTradingFlow,
  triggerMarketRefresh
} from './api'

// Quản lý Tab hiển thị: 'dashboard' | 'news' | 'risk'
const currentTab = ref('dashboard')

const marketData = ref(null)
const stocks = ref([])
const isLoading = ref(true)
const isApiOffline = ref(false)

const refreshInterval = ref(60)
const countdown = ref(60)
let timer = null

// Keys để ép buộc nạp mới các component Tab con khi làm mới (như Ctrl + Shift + R)
const newsRefreshKey = ref(0)
const riskRefreshKey = ref(0)
const isRefreshingManual = ref(false)

const isModalOpen = ref(false)
const selectedStock = ref(null)

// Quản lý Modal Báo cáo Khuyến nghị & Lý do VN30
const isReportModalOpen = ref(false)
const recommendationReportData = ref(null)
const isLoadingReport = ref(false)

// Quản lý Modal Giao dịch Khối Ngoại & Trong Nước
const isFlowModalOpen = ref(false)
const flowSummaryData = ref(null)

const topStock = computed(() => {
  if (stocks.value && stocks.value.length > 0) {
    return stocks.value[0]
  }
  return null
})

// Đóng toàn bộ các modal đang hiển thị nổi trên màn hình
function closeAllModals() {
  isModalOpen.value = false
  selectedStock.value = null
  isReportModalOpen.value = false
  isFlowModalOpen.value = false
}

// Khi người dùng bấm chọn tab (Thị trường, Tin tức, Rủi ro AI)
function handleSelectTab(tab) {
  closeAllModals()
  currentTab.value = tab
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Bất cứ khi nào currentTab thay đổi, đảm bảo đóng sạch các modal
watch(currentTab, () => {
  closeAllModals()
})

async function loadData(isSilent = false) {
  if (!isSilent) {
    isLoading.value = true
  }
  isApiOffline.value = false

  try {
    const [mRes, sRes, fRes] = await Promise.all([
      fetchMarketOverview(),
      fetchVN30Leaderboard(),
      fetchMarketTradingFlow('today')
    ])

    if (!mRes && (!sRes || sRes.length === 0)) {
      isApiOffline.value = true
    } else {
      marketData.value = mRes
      stocks.value = sRes
      if (fRes?.summary) {
        flowSummaryData.value = fRes.summary
      }
      
      if (mRes?.auto_refresh?.interval_seconds) {
        refreshInterval.value = mRes.auto_refresh.interval_seconds
      }
    }
  } catch (err) {
    isApiOffline.value = true
  } finally {
    if (!isSilent) {
      isLoading.value = false
    }
  }
}

// Hàm xử lý nút bấm "Làm Mới Toàn Trang" (Tương đương phím tắt Ctrl + Shift + R)
async function handleManualRefresh() {
  if (isRefreshingManual.value) return
  isRefreshingManual.value = true
  try {
    // 1. Gửi lệnh kích hoạt server tính toán lại dữ liệu mới nhất
    await triggerMarketRefresh().catch(() => {})
  } catch (e) {}

  // 2. Nạp lại dữ liệu thị trường và kích hoạt nạp lại Tab Tin Tức / Rủi Ro AI
  await loadData(false)
  newsRefreshKey.value++
  riskRefreshKey.value++
  countdown.value = refreshInterval.value

  setTimeout(() => {
    isRefreshingManual.value = false
  }, 600)
}

// ==================== CƠ CHẾ PAUSE POLLING KHI TAB ẨN & REFRESH NGAY KHI QUAY LẠI ====================
let lastActiveTimestamp = Date.now()
let isPollingPaused = false

async function handleVisibilityOrFocus() {
  if (document.visibilityState === 'visible' || document.hasFocus?.()) {
    const now = Date.now()
    const elapsedSeconds = Math.round((now - lastActiveTimestamp) / 1000)

    // Khi người dùng quay lại tab sau >= 30 giây: load mới dữ liệu ngay
    if (isPollingPaused || elapsedSeconds >= 30) {
      console.log(`[Lifecycle] Quay lại web sau ${elapsedSeconds}s → Tự động nạp mới dữ liệu...`)
      isPollingPaused = false
      // Nạp ngầm không giật màn hình
      await loadData(true)
      newsRefreshKey.value++
      riskRefreshKey.value++
      // Khởi động lại timer từ đầu
      startAutoRefreshTimer()
    }
    lastActiveTimestamp = now
  } else {
    // Tab bị ẩn / người dùng chuyển app khác → tạm dừng polling để tiết kiệm rate-limit
    lastActiveTimestamp = Date.now()
    if (!isPollingPaused) {
      isPollingPaused = true
      if (timer) {
        clearInterval(timer)
        timer = null
        console.log('[Lifecycle] Tab ẩn → Đã tạm dừng polling (tiết kiệm rate-limit).')
      }
    }
  }
}

function startAutoRefreshTimer() {
  if (timer) clearInterval(timer)
  countdown.value = refreshInterval.value

  timer = setInterval(async () => {
    if (document.hidden) {
      // Nếu tab đang ẩn (user đã tab-out sau khi timer đã chạy) → dừng lại
      if (!isPollingPaused) {
        isPollingPaused = true
        clearInterval(timer)
        timer = null
        console.log('[Timer] Tab ẩn giữa chừng → Dừng polling.')
      }
      return
    }
    if (countdown.value > 1) {
      countdown.value--
    } else {
      countdown.value = refreshInterval.value
      // Tự động làm mới dữ liệu ngầm không giật màn hình
      await loadData(true)
    }
  }, 1000)
}


function openStockModal(stock) {
  if (!stock) return
  const ticker = typeof stock === 'string' ? stock : stock?.ticker
  const fullStock = stocks.value.find(s => s.ticker === ticker)
  selectedStock.value = fullStock ? { ...stock, ...fullStock } : stock
  isModalOpen.value = true
}

function closeStockModal() {
  isModalOpen.value = false
  selectedStock.value = null
}

async function openRecommendationReport() {
  isReportModalOpen.value = true
  if (!recommendationReportData.value) {
    isLoadingReport.value = true
  }
  try {
    const data = await fetchMarketRecommendationReport()
    if (data) {
      recommendationReportData.value = data
    }
  } catch (err) {
    console.error('Lỗi lấy báo cáo khuyến nghị:', err)
  } finally {
    isLoadingReport.value = false
  }
}

function openFlowReport() {
  isFlowModalOpen.value = true
}

onMounted(async () => {
  await loadData(false)
  startAutoRefreshTimer()

  // Đăng ký các sự kiện theo dõi vòng đời trang web trên điện thoại & máy tính:
  // - visibilitychange: Tắt/bật màn hình điện thoại hoặc ẩn/hiện tab
  // - focus: Người dùng click chuột lại vào cửa sổ web
  // - pageshow: Trình duyệt mở lại trang từ bộ nhớ cache của hệ điều hành
  document.addEventListener('visibilitychange', handleVisibilityOrFocus)
  window.addEventListener('focus', handleVisibilityOrFocus)
  window.addEventListener('pageshow', handleVisibilityOrFocus)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  document.removeEventListener('visibilitychange', handleVisibilityOrFocus)
  window.removeEventListener('focus', handleVisibilityOrFocus)
  window.removeEventListener('pageshow', handleVisibilityOrFocus)
})
</script>
