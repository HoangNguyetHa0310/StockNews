<template>
  <div class="min-h-screen bg-theme-bg text-theme-text flex font-sans transition-colors duration-200">
    
    <!-- Sidebar Navigation bên lề trái (ở đúng vị trí ô đỏ bạn khoanh) -->
    <Sidebar 
      :active-tab="currentTab" 
      @select-tab="handleSelectTab" 
    />

    <!-- Khung nội dung chính bên phải -->
    <div class="flex-1 flex flex-col min-w-0 overflow-x-hidden">
      
      <!-- Top Navbar Header -->
      <Navbar 
        :market-data="marketData" 
        :countdown="countdown"
        :refresh-interval="refreshInterval"
      />

      <!-- Main Content Area: Rộng rãi, tối ưu khoảng đệm mobile & desktop -->
      <main class="flex-1 w-full max-w-[95%] xl:max-w-[92%] 2xl:max-w-[88%] mx-auto px-3 sm:px-6 py-4 sm:py-8 pb-24 md:pb-8 space-y-4 sm:space-y-8">
        
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
          <NewsFeed />
        </template>

        <!-- ==================== TAB 3: BÁO CÁO ĐÁNH GIÁ RỦI RO ==================== -->
        <template v-else-if="currentTab === 'risk'">
          <NewsRiskReport />
        </template>

      </main>

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

      <!-- Footer -->
      <footer class="border-t border-theme-border py-6 text-center text-xs text-theme-text-muted font-mono mt-8 mb-14 md:mb-0 transition-colors duration-200">
        <p>&copy; 2026 VN30 Quantitative & AI Intelligence Platform. All rights reserved.</p>
      </footer>

      <!-- Mobile Bottom Navigation Bar (Thanh điều hướng cố định dưới đáy màn hình điện thoại) -->
      <nav class="md:hidden fixed bottom-0 left-0 right-0 z-40 bg-theme-card/95 backdrop-blur-lg border-t border-theme-border flex items-center justify-around py-2 px-3 shadow-lg select-none">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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
  fetchMarketTradingFlow 
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

function handleSelectTab(tab) {
  currentTab.value = tab
}

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

function startAutoRefreshTimer() {
  if (timer) clearInterval(timer)
  countdown.value = refreshInterval.value

  timer = setInterval(async () => {
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
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>
