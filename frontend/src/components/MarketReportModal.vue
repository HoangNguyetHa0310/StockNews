<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-theme-backdrop backdrop-blur-md animate-fade-in overflow-y-auto"
    @click.self="$emit('close')"
  >
    <div 
      class="bg-theme-card border border-theme-border rounded-3xl w-full max-w-6xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden transition-colors duration-200 my-auto text-theme-text"
    >
      <!-- Modal Header -->
      <div class="px-6 py-5 border-b border-theme-border flex items-center justify-between bg-theme-subtle">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 shrink-0">
            <PieChart class="w-5 h-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                Báo Cáo Phân Bổ Khuyến Nghị & Lý Do Thị Trường VN30
              </h2>
              <span class="hidden sm:inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30">
                AI & QUANT INSIGHTS
              </span>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Phân bổ tỷ lệ % danh mục rổ VN30 và giải trình chi tiết lý do từng cổ phiếu nên Mua, Bán hay Nắm giữ.
            </p>
          </div>
        </div>

        <button 
          @click="$emit('close')" 
          class="p-2 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
          title="Đóng cửa sổ (Esc)"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div class="p-6 overflow-y-auto space-y-6 flex-1 text-theme-text">
        
        <!-- Loading State -->
        <div v-if="isLoading" class="py-20 text-center space-y-3">
          <div class="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p class="text-xs text-slate-500 dark:text-slate-400 font-mono">Đang tổng hợp báo cáo phân bổ và dữ liệu định lượng VN30...</p>
        </div>

        <template v-else>
          <!-- Section 1: 3 Thẻ Tỷ Lệ Phân Bổ Khuyến Nghị (Mua % - Chờ % - Bán %) -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            
            <!-- Card Mua -->
            <div 
              @click="activeFilter = 'BUY'"
              class="p-5 rounded-2xl border transition-all cursor-pointer shadow-sm relative overflow-hidden"
              :class="activeFilter === 'BUY' 
                ? 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-500 ring-2 ring-emerald-500/20' 
                : 'bg-theme-card border-theme-border hover:border-emerald-500/50'"
            >
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-xs font-bold font-mono uppercase tracking-wider text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
                    <TrendingUp class="w-4 h-4" /> NÊN MUA (TÍCH LŨY)
                  </span>
                  <div class="mt-2 flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400">
                      {{ reportData?.allocation?.buy?.percentage || 0 }}%
                    </span>
                    <span class="text-xs text-slate-500 dark:text-slate-400 font-mono">
                      ({{ reportData?.allocation?.buy?.count || 0 }} / {{ reportData?.total_stocks || 30 }} mã)
                    </span>
                  </div>
                </div>
                <div class="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 class="w-5 h-5" />
                </div>
              </div>
              <!-- Ticker pills -->
              <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-1">
                <span 
                  v-for="tick in (reportData?.allocation?.buy?.tickers || [])" 
                  :key="tick"
                  class="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-300"
                >
                  {{ tick }}
                </span>
                <span v-if="!reportData?.allocation?.buy?.tickers?.length" class="text-xs text-slate-400 italic">
                  Chưa có mã bùng nổ điểm mua
                </span>
              </div>
            </div>

            <!-- Card Chờ / Nắm Giữ -->
            <div 
              @click="activeFilter = 'HOLD'"
              class="p-5 rounded-2xl border transition-all cursor-pointer shadow-sm relative overflow-hidden"
              :class="activeFilter === 'HOLD' 
                ? 'bg-amber-50 dark:bg-amber-950/30 border-amber-500 ring-2 ring-amber-500/20' 
                : 'bg-theme-card border-theme-border hover:border-amber-500/50'"
            >
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-xs font-bold font-mono uppercase tracking-wider text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                    <Clock class="w-4 h-4" /> CHỜ / NẮM GIỮ (THEO DÕI)
                  </span>
                  <div class="mt-2 flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold font-mono text-amber-600 dark:text-amber-400">
                      {{ reportData?.allocation?.hold?.percentage || 0 }}%
                    </span>
                    <span class="text-xs text-slate-500 dark:text-slate-400 font-mono">
                      ({{ reportData?.allocation?.hold?.count || 0 }} / {{ reportData?.total_stocks || 30 }} mã)
                    </span>
                  </div>
                </div>
                <div class="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
                  <PauseCircle class="w-5 h-5" />
                </div>
              </div>
              <!-- Ticker pills (first 6) -->
              <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-1">
                <span 
                  v-for="tick in (reportData?.allocation?.hold?.tickers || []).slice(0, 7)" 
                  :key="tick"
                  class="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-amber-500/20 text-amber-700 dark:text-amber-300"
                >
                  {{ tick }}
                </span>
                <span v-if="(reportData?.allocation?.hold?.tickers?.length || 0) > 7" class="text-[11px] font-mono text-slate-400 self-center">
                  +{{ reportData.allocation.hold.tickers.length - 7 }} mã...
                </span>
              </div>
            </div>

            <!-- Card Bán -->
            <div 
              @click="activeFilter = 'SELL'"
              class="p-5 rounded-2xl border transition-all cursor-pointer shadow-sm relative overflow-hidden"
              :class="activeFilter === 'SELL' 
                ? 'bg-rose-50 dark:bg-rose-950/30 border-rose-500 ring-2 ring-rose-500/20' 
                : 'bg-theme-card border-theme-border hover:border-rose-500/50'"
            >
              <div class="flex justify-between items-start">
                <div>
                  <span class="text-xs font-bold font-mono uppercase tracking-wider text-rose-600 dark:text-rose-400 flex items-center gap-1.5">
                    <TrendingDown class="w-4 h-4" /> BÁN / HẠ TỶ TRỌNG
                  </span>
                  <div class="mt-2 flex items-baseline gap-2">
                    <span class="text-3xl font-extrabold font-mono text-rose-600 dark:text-rose-400">
                      {{ reportData?.allocation?.sell?.percentage || 0 }}%
                    </span>
                    <span class="text-xs text-slate-500 dark:text-slate-400 font-mono">
                      ({{ reportData?.allocation?.sell?.count || 0 }} / {{ reportData?.total_stocks || 30 }} mã)
                    </span>
                  </div>
                </div>
                <div class="p-2 rounded-xl bg-rose-500/10 text-rose-600 dark:text-rose-400">
                  <AlertTriangle class="w-5 h-5" />
                </div>
              </div>
              <!-- Ticker pills (first 6) -->
              <div class="mt-3 pt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-1">
                <span 
                  v-for="tick in (reportData?.allocation?.sell?.tickers || []).slice(0, 7)" 
                  :key="tick"
                  class="px-2 py-0.5 rounded-md text-[11px] font-mono font-bold bg-rose-500/20 text-rose-700 dark:text-rose-300"
                >
                  {{ tick }}
                </span>
                <span v-if="(reportData?.allocation?.sell?.tickers?.length || 0) > 7" class="text-[11px] font-mono text-slate-400 self-center">
                  +{{ reportData.allocation.sell.tickers.length - 7 }} mã...
                </span>
              </div>
            </div>

          </div>

          <!-- Section 2: Trạng Thái Thị Trường & Diễn Giải Chi Tiết -->
          <div class="p-5 rounded-2xl bg-theme-subtle border border-theme-border space-y-3">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div class="flex items-center gap-2">
                <Compass class="w-5 h-5 text-cyan-500" />
                <span class="text-xs uppercase font-bold text-slate-400 tracking-wider">Trạng Thái Thị Trường Hiện Tại:</span>
                <span class="text-sm font-bold text-slate-900 dark:text-white px-2.5 py-0.5 rounded-lg bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30">
                  {{ reportData?.market_sentiment }}
                </span>
              </div>
              <div class="text-xs font-mono text-slate-500 dark:text-slate-400">
                VN-INDEX: <strong class="text-slate-800 dark:text-slate-200">{{ formatNumber(reportData?.vnindex_close) }}</strong>
                <span :class="(reportData?.vnindex_change_pct || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'" class="ml-1 font-bold">
                  ({{ (reportData?.vnindex_change_pct || 0) >= 0 ? '+' : '' }}{{ reportData?.vnindex_change_pct?.toFixed(2) }}%)
                </span>
              </div>
            </div>

            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              {{ reportData?.regime_explanation }}
            </p>

            <!-- Distribution Progress Bar -->
            <div class="w-full bg-slate-200 dark:bg-slate-800 h-2.5 rounded-full overflow-hidden flex shadow-inner">
              <div 
                class="bg-emerald-500 h-full transition-all duration-500" 
                :style="{ width: (reportData?.allocation?.buy?.percentage || 0) + '%' }" 
                :title="`Nên Mua: ${reportData?.allocation?.buy?.percentage || 0}%`"
              ></div>
              <div 
                class="bg-amber-500 h-full transition-all duration-500" 
                :style="{ width: (reportData?.allocation?.hold?.percentage || 0) + '%' }" 
                :title="`Chờ / Giữ: ${reportData?.allocation?.hold?.percentage || 0}%`"
              ></div>
              <div 
                class="bg-rose-500 h-full transition-all duration-500" 
                :style="{ width: (reportData?.allocation?.sell?.percentage || 0) + '%' }" 
                :title="`Nên Bán: ${reportData?.allocation?.sell?.percentage || 0}%`"
              ></div>
            </div>
          </div>

          <!-- Section 3: Toolbar Lọc & Tìm Kiếm Cổ Phiếu -->
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 pt-2">
            <div class="flex flex-wrap items-center gap-2">
              <button 
                @click="activeFilter = 'ALL'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition"
                :class="activeFilter === 'ALL' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
              >
                Tất cả ({{ reportData?.all_stocks?.length || 0 }})
              </button>
              <button 
                @click="activeFilter = 'BUY'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
                :class="activeFilter === 'BUY' ? 'bg-emerald-500 text-slate-950 font-bold shadow-sm' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
              >
                🟢 Nên Mua ({{ reportData?.buy_stocks?.length || 0 }})
              </button>
              <button 
                @click="activeFilter = 'HOLD'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
                :class="activeFilter === 'HOLD' ? 'bg-amber-500 text-slate-950 font-bold shadow-sm' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
              >
                🟡 Chờ / Giữ ({{ reportData?.hold_stocks?.length || 0 }})
              </button>
              <button 
                @click="activeFilter = 'SELL'"
                class="px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
                :class="activeFilter === 'SELL' ? 'bg-rose-500 text-white font-bold shadow-sm' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'"
              >
                🔴 Cảnh Báo Bán ({{ reportData?.sell_stocks?.length || 0 }})
              </button>
            </div>

            <!-- Search input -->
            <div class="relative w-full md:w-72">
              <Search class="w-4 h-4 text-theme-muted absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                v-model="searchQuery"
                type="text" 
                placeholder="Tìm mã (VD: VCB, HPG, FPT)..."
                class="w-full pl-9 pr-4 py-2 bg-theme-subtle border border-theme-border rounded-xl text-xs text-theme-text placeholder-theme-muted focus:outline-none focus:border-cyan-500 font-mono shadow-inner"
              />
            </div>
          </div>

          <!-- Section 4: Danh Sách Chi Tiết Từng Cổ Phiếu VN30 (Cards with Detailed Reasoning) -->
          <div class="space-y-4 pt-1">
            <div 
              v-for="stock in filteredStocks" 
              :key="stock.ticker"
              class="p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm space-y-4 hover:border-cyan-500/40 transition group"
            >
              <!-- Stock Header Summary Row -->
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-theme-border">
                <div class="flex items-center gap-3">
                  <div class="w-11 h-11 rounded-xl bg-theme-subtle border border-theme-border flex items-center justify-center font-mono font-bold text-base text-theme-text group-hover:bg-cyan-500/10 group-hover:text-cyan-500 transition shrink-0">
                    {{ stock.ticker }}
                  </div>
                  <div>
                    <div class="flex items-center gap-2">
                      <h4 class="font-bold text-sm text-theme-text">{{ stock.company_name || stock.ticker }}</h4>
                      <span class="text-[10px] font-mono px-2 py-0.5 rounded-md bg-theme-subtle-2 text-theme-sub">
                        {{ stock.sector || 'Rổ VN30' }}
                      </span>
                    </div>
                    <p class="text-xs font-mono text-theme-sub mt-0.5">
                      Giá đóng cửa: <strong class="text-theme-text font-bold">{{ formatNumber(stock.close) }}</strong>
                      <span :class="(stock.change_pct || 0) >= 0 ? 'text-emerald-500' : 'text-rose-500'" class="ml-1 font-bold">
                        ({{ (stock.change_pct || 0) >= 0 ? '+' : '' }}{{ stock.change_pct?.toFixed(2) }}%)
                      </span>
                      &bull; Vol/MA20: <strong class="text-theme-text">{{ stock.vol_vs_ma20 }}x</strong>
                      &bull; RSI: <strong class="text-theme-text">{{ stock.rsi }}</strong>
                    </p>
                  </div>
                </div>

                <!-- Signal Badge & Scores -->
                <div class="flex items-center gap-2.5 flex-wrap">
                  <!-- Signal Badge -->
                  <span 
                    class="px-3 py-1 rounded-xl text-xs font-bold font-mono tracking-wide shadow-sm"
                    :class="getSignalBadgeClass(stock.signal)"
                  >
                    {{ stock.signal }}
                  </span>

                  <!-- Quant Score Pill -->
                  <div class="px-2.5 py-1 rounded-xl bg-theme-subtle border border-theme-border text-xs font-mono">
                    <span class="text-theme-muted">Quant: </span>
                    <strong class="text-cyan-500 dark:text-cyan-400">{{ stock.total_score }}đ</strong>
                  </div>

                  <!-- AI Prob Pill -->
                  <div class="px-2.5 py-1 rounded-xl bg-theme-subtle border border-theme-border text-xs font-mono">
                    <span class="text-theme-muted">AI T+3: </span>
                    <strong :class="stock.ml_prob_up >= 50 ? 'text-emerald-500' : 'text-theme-muted'">{{ stock.ml_prob_up }}%</strong>
                  </div>

                  <!-- Open Chart Button -->
                  <button 
                    @click="$emit('select-stock', stock)"
                    class="px-2.5 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30 text-xs font-medium transition flex items-center gap-1"
                    title="Xem biểu đồ kỹ thuật TradingView"
                  >
                    <span>Biểu đồ</span>
                    <ExternalLink class="w-3 h-3" />
                  </button>
                </div>
              </div>

              <!-- 3 Detailed Content Pillars (Lý do khuyến nghị, Tin tức tác động, Động lực giá) -->
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-3.5 text-xs">
                
                <!-- Pillar 1: Lý do vì sao Mua/Bán/Giữ -->
                <div class="p-3.5 rounded-xl bg-theme-subtle border border-theme-border space-y-1.5">
                  <div class="flex items-center gap-1.5 font-bold text-theme-text text-[11px] uppercase tracking-wider">
                    <Brain class="w-3.5 h-3.5 text-cyan-500" />
                    LÝ DO KHUYẾN NGHỊ KỸ THUẬT & AI
                  </div>
                  <p class="text-theme-text-sub leading-relaxed text-[11.5px]">
                    {{ stock.recommendation_reason || 'Đang cập nhật phân tích định lượng...' }}
                  </p>
                </div>

                <!-- Pillar 2: Tin tức & Vĩ mô tác động -->
                <div class="p-3.5 rounded-xl bg-theme-subtle border border-theme-border space-y-1.5">
                  <div class="flex items-center gap-1.5 font-bold text-theme-text text-[11px] uppercase tracking-wider">
                    <Newspaper class="w-3.5 h-3.5 text-emerald-500" />
                    TIN TỨC VĨ MÔ & NGÀNH TÁC ĐỘNG
                  </div>
                  <p class="text-theme-text-sub leading-relaxed text-[11.5px]">
                    {{ stock.news_impact || 'Chịu tác động bởi các chính sách điều hành tiền tệ và xu hướng nhóm ngành.' }}
                  </p>
                </div>

                <!-- Pillar 3: Vì sao tăng giá / Động lực & Mức giá chiến lược -->
                <div class="p-3.5 rounded-xl bg-theme-subtle border border-theme-border space-y-1.5 flex flex-col justify-between">
                  <div>
                    <div class="flex items-center gap-1.5 font-bold text-theme-text text-[11px] uppercase tracking-wider">
                      <Zap class="w-3.5 h-3.5 text-amber-500" />
                      VÌ SAO TĂNG GIÁ / ĐỘNG LỰC CỐT LÕI
                    </div>
                    <p class="text-theme-text-sub leading-relaxed text-[11.5px] mt-1">
                      {{ stock.why_price_changes || stock.growth_driver || 'Động lực từ dòng tiền phục hồi và định giá.' }}
                    </p>
                  </div>

                  <!-- Price targets pill bar -->
                  <div class="pt-2 border-t border-theme-border flex items-center justify-between text-[11px] font-mono">
                    <span class="text-theme-muted">Mục tiêu: <strong class="text-emerald-500">{{ formatNumber(stock.target_1) }}</strong></span>
                    <span class="text-theme-muted">Dừng lỗ: <strong class="text-rose-500">{{ formatNumber(stock.stoploss) }}</strong></span>
                    <span class="text-theme-muted">R/R: <strong class="text-cyan-500">{{ stock.risk_reward_ratio }}:1</strong></span>
                  </div>
                </div>

              </div>
            </div>

            <!-- Empty state if search has no match -->
            <div v-if="filteredStocks.length === 0" class="py-12 text-center text-theme-muted space-y-2">
              <AlertCircle class="w-8 h-8 mx-auto text-theme-muted" />
              <p class="text-xs">Không tìm thấy mã cổ phiếu nào phù hợp với từ khóa "{{ searchQuery }}".</p>
            </div>
          </div>

        </template>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 border-t border-theme-border bg-theme-subtle flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-theme-text-muted">
        <div class="flex items-center gap-2">
          <ShieldAlert class="w-4 h-4 text-amber-500" />
          <span>Báo cáo được tổng hợp tự động từ mô hình định lượng đa nhân tố và dữ liệu nến phiên gần nhất.</span>
        </div>
        <button 
          @click="$emit('close')"
          class="px-5 py-2 rounded-xl bg-theme-subtle-2 hover:bg-theme-border font-semibold text-theme-text transition"
        >
          Đóng Báo Cáo
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { 
  X, PieChart, TrendingUp, TrendingDown, Clock, 
  CheckCircle2, PauseCircle, AlertTriangle, Compass, 
  Search, ExternalLink, Brain, Newspaper, Zap, AlertCircle, ShieldAlert
} from 'lucide-vue-next'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  reportData: {
    type: Object,
    default: null
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close', 'select-stock'])

const activeFilter = ref('ALL') // 'ALL' | 'BUY' | 'HOLD' | 'SELL'
const searchQuery = ref('')

const filteredStocks = computed(() => {
  let list = props.reportData?.all_stocks || []

  // Filter by signal category
  if (activeFilter.value === 'BUY') {
    list = props.reportData?.buy_stocks || list.filter(s => s.signal?.includes('MUA'))
  } else if (activeFilter.value === 'HOLD') {
    list = props.reportData?.hold_stocks || list.filter(s => !s.signal?.includes('MUA') && !s.signal?.includes('BÁN'))
  } else if (activeFilter.value === 'SELL') {
    list = props.reportData?.sell_stocks || list.filter(s => s.signal?.includes('BÁN'))
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toUpperCase()
    list = list.filter(s => 
      s.ticker?.toUpperCase().includes(q) || 
      (s.company_name && s.company_name.toUpperCase().includes(q)) ||
      (s.sector && s.sector.toUpperCase().includes(q))
    )
  }

  return list
})

function getSignalBadgeClass(signal) {
  if (!signal) return 'bg-slate-100 text-slate-600'
  if (signal.includes('MUA MẠNH')) {
    return 'bg-emerald-500 text-slate-950 font-extrabold border border-emerald-400'
  } else if (signal.includes('MUA')) {
    return 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/40'
  } else if (signal.includes('BÁN MẠNH')) {
    return 'bg-rose-500 text-white font-extrabold border border-rose-400'
  } else if (signal.includes('BÁN')) {
    return 'bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/40'
  } else if (signal.includes('THEO DÕI')) {
    return 'bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
  } else {
    return 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30'
  }
}

function formatNumber(val) {
  if (val === null || val === undefined) return '--'
  return Number(val).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>
