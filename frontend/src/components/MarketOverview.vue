<template>
  <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Card 1: VN-INDEX -->
    <div class="p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm relative overflow-hidden backdrop-blur-sm transition-colors duration-200 flex flex-col justify-between">
      <div class="flex justify-between items-start gap-2">
        <div class="min-w-0 flex-1">
          <p class="text-xs font-semibold text-theme-sub uppercase tracking-wider truncate">Chỉ Số VN-INDEX</p>
          <h3 class="text-2xl font-bold font-mono text-theme-text mt-1">
            {{ formatNumber(marketData?.vnindex_close) }}
          </h3>
          <p 
            class="text-xs font-mono font-semibold mt-1 flex items-center gap-1"
            :class="(marketData?.vnindex_change_pct || 0) >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400'"
          >
            <span>{{ (marketData?.vnindex_change_pct || 0) >= 0 ? '+' : '' }}{{ marketData?.vnindex_change_pct?.toFixed(2) }}%</span>
          </p>
        </div>
        <div class="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 shrink-0">
          <BarChart2 class="w-5 h-5" />
        </div>
      </div>
      <div class="mt-4 pt-3 border-t border-theme-border flex items-center justify-between text-xs text-theme-sub font-mono">
        <span>Thanh khoản phiên:</span>
        <span class="text-theme-text font-semibold">{{ formatVolume(marketData?.vnindex_volume) }}</span>
      </div>
    </div>

    <!-- Card 2: Báo Cáo Khuyến Nghị Mua / Chờ / Bán (Clickable để mở báo cáo lý do VN30) -->
    <div 
      @click="$emit('open-report')"
      class="p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm relative overflow-hidden backdrop-blur-sm transition-all duration-200 cursor-pointer hover:border-cyan-500/70 hover:shadow-lg hover:shadow-cyan-500/5 group flex flex-col justify-between"
      title="Bấm để xem Báo cáo Khuyến nghị Mua / Chờ / Bán chi tiết rổ VN30"
    >
      <div>
        <!-- Clean Header Row: Title & Interactive Badge with Icon -->
        <div class="flex items-center justify-between gap-2 pb-1.5">
          <p class="text-xs font-semibold text-theme-sub uppercase tracking-wider truncate" title="Khuyến Nghị Mua / Chờ / Bán">
            Khuyến Nghị Mua / Chờ / Bán
          </p>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-bold whitespace-nowrap shrink-0 bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20 group-hover:bg-cyan-500 group-hover:text-slate-950 transition">
            <Compass class="w-3.5 h-3.5" />
            <span>Báo cáo ↗</span>
          </span>
        </div>

        <!-- Sentiment Statement -->
        <h3 class="text-base font-bold text-theme-text mt-1 leading-snug group-hover:text-cyan-500 dark:group-hover:text-cyan-400 transition">
          {{ marketData?.market_sentiment || 'Thận Trọng / Tích Lũy Chờ Xu Hướng Mới' }}
        </h3>

        <!-- Distribution Pill Values -->
        <p class="text-xs text-theme-muted mt-1.5 font-mono">
          <span class="text-emerald-500 font-semibold">{{ marketData?.pct_buy || 0 }}% Mua</span>
          <span class="mx-1.5 text-theme-border">|</span>
          <span class="text-amber-500 font-semibold">{{ marketData?.pct_hold || 0 }}% Chờ</span>
          <span class="mx-1.5 text-theme-border">|</span>
          <span class="text-rose-500 font-semibold">{{ marketData?.pct_sell || 0 }}% Bán</span>
        </p>
      </div>

      <div class="mt-4 pt-3 border-t border-theme-border flex items-center justify-between text-xs text-theme-sub font-mono">
        <span>Tỷ lệ MUA rổ VN30:</span>
        <span class="font-bold text-emerald-500 dark:text-emerald-400">{{ marketData?.pct_buy || 0 }}% ({{ marketData?.buy_count || 0 }}/{{ totalStocks }} mã)</span>
      </div>
    </div>

    <!-- Card 3: Giao Dịch Khối Ngoại & Trong Nước (Clickable để mở Báo cáo Dòng Tiền VN30) -->
    <div 
      @click="$emit('open-flow-report')"
      class="p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm relative overflow-hidden backdrop-blur-sm transition-all duration-200 cursor-pointer hover:border-cyan-500/70 hover:shadow-lg hover:shadow-cyan-500/5 group flex flex-col justify-between"
      title="Bấm để xem danh sách 30 mã VN30, khối lượng Mua/Bán của Khối Ngoại & Trong Nước"
    >
      <div>
        <!-- Clean Header Row: Title & Interactive Badge with Icon -->
        <div class="flex items-center justify-between gap-2 pb-1.5">
          <p class="text-xs font-semibold text-theme-sub uppercase tracking-wider truncate" title="Khối Ngoại & Trong Nước">
            Khối Ngoại & Trong Nước
          </p>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg text-[10px] font-bold whitespace-nowrap shrink-0 bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20 group-hover:bg-blue-500 group-hover:text-slate-950 transition">
            <ArrowLeftRight class="w-3.5 h-3.5" />
            <span>Chi tiết ↗</span>
          </span>
        </div>
        
        <!-- Giá trị Mua/Bán Ròng Khối Ngoại & Trong Nước -->
        <div class="mt-1 flex items-baseline justify-between">
          <div>
            <p class="text-[10px] uppercase tracking-wider font-semibold text-theme-muted">Khối Ngoại</p>
            <h3 
              class="text-xl sm:text-2xl font-bold font-mono mt-0.5"
              :class="foreignNet >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400'"
            >
              {{ foreignNet >= 0 ? '+' : '' }}{{ formatNumber(foreignNet) }}M
            </h3>
          </div>
          <div class="text-right">
            <p class="text-[10px] uppercase tracking-wider font-semibold text-theme-muted">Trong Nước</p>
            <h3 
              class="text-xl sm:text-2xl font-bold font-mono mt-0.5"
              :class="domesticNet >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400'"
            >
              {{ domesticNet >= 0 ? '+' : '' }}{{ formatNumber(domesticNet) }}M
            </h3>
          </div>
        </div>

        <!-- Tóm tắt chi tiết Mua/Bán -->
        <div class="text-[11px] text-theme-sub font-mono mt-1.5 flex items-center justify-between border-t border-theme-border/50 pt-1.5">
          <span>Mua {{ formatNumber(foreignBuy) }}M / Bán {{ formatNumber(foreignSell) }}M</span>
          <span>Mua {{ formatNumber(domesticBuy) }}M / Bán {{ formatNumber(domesticSell) }}M</span>
        </div>
      </div>

      <div class="mt-4 pt-3 border-t border-theme-border flex items-center justify-between text-xs text-theme-sub font-mono">
        <span>Dòng tiền VN30:</span>
        <span class="font-bold text-cyan-600 dark:text-cyan-400 group-hover:underline">Báo cáo 30 mã &rarr;</span>
      </div>
    </div>

    <!-- Card 4: Top AI Pick -->
    <div class="p-5 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-emerald-500/5 bg-theme-card border border-cyan-500/30 shadow-sm relative overflow-hidden backdrop-blur-sm transition-colors duration-200 flex flex-col justify-between">
      <div class="flex justify-between items-start gap-2">
        <div class="min-w-0 flex-1">
          <p class="text-xs font-semibold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider flex items-center gap-1 truncate">
            <Zap class="w-3.5 h-3.5 shrink-0" /> Dẫn Đầu AI & Quant
          </p>
          <h3 class="text-2xl font-bold font-mono text-theme-text mt-1">
            {{ topStock?.ticker || '--' }}
          </h3>
          <p class="text-xs text-theme-sub font-mono mt-0.5 truncate">
            Giá: {{ formatNumber(topStock?.close) }} ({{ (topStock?.change_pct || 0) >= 0 ? '+' : '' }}{{ topStock?.change_pct?.toFixed(2) }}%)
          </p>
        </div>
        <div class="px-2.5 py-1 rounded-lg bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-mono font-bold text-xs border border-emerald-500/40 shrink-0">
          {{ topStock?.total_score || 0 }} ĐIỂM
        </div>
      </div>
      <div class="mt-4 pt-3 border-t border-cyan-500/20 flex items-center justify-between text-xs text-theme-sub font-mono">
        <span>Xác suất tăng T+3:</span>
        <span class="font-bold text-cyan-600 dark:text-cyan-300">{{ topStock?.ml_prob_up || 0 }}%</span>
      </div>
    </div>

    <!-- Market Trading Session Banner (Hiển thị trạng thái phiên sạch sẽ, gọn gàng) -->
    <div 
      v-if="marketData?.market_schedule"
      class="col-span-1 sm:col-span-2 lg:col-span-4 px-4 py-3 rounded-2xl bg-theme-card border border-theme-border shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs transition-colors duration-200"
    >
      <div class="flex items-center gap-2 min-w-0">
        <span 
          class="w-2.5 h-2.5 rounded-full shrink-0"
          :class="marketData.market_schedule.is_trading ? 'bg-emerald-500 animate-ping' : 'bg-amber-500'"
        ></span>
        <span class="font-bold text-theme-text whitespace-nowrap">
          {{ marketData.market_schedule.session_name }}:
        </span>
        <span class="text-theme-sub truncate">
          {{ marketData.market_schedule.detail }}
        </span>
      </div>
      <div class="flex items-center gap-2 text-[11px] font-mono text-cyan-600 dark:text-cyan-400 shrink-0">
        <span class="w-1.5 h-1.5 rounded-full bg-cyan-500"></span>
        <span>Tin tức & Rủi ro: <strong>24/7 Realtime</strong></span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { BarChart2, Compass, PieChart, Zap, ArrowLeftRight } from 'lucide-vue-next'

defineEmits(['open-report', 'open-flow-report'])

const props = defineProps({
  marketData: {
    type: Object,
    default: null
  },
  topStock: {
    type: Object,
    default: null
  },
  flowSummary: {
    type: Object,
    default: null
  }
})

const totalStocks = computed(() => props.marketData?.total_stocks_analyzed || 30)
const buyWidth = computed(() => ((props.marketData?.buy_count || 0) / totalStocks.value) * 100)
const holdWidth = computed(() => ((props.marketData?.hold_count || 0) / totalStocks.value) * 100)
const sellWidth = computed(() => ((props.marketData?.sell_count || 0) / totalStocks.value) * 100)

const foreignBuy = computed(() => {
  if (props.flowSummary?.foreign?.buy_million !== undefined) {
    return props.flowSummary.foreign.buy_million
  }
  return 14.50
})

const foreignSell = computed(() => {
  if (props.flowSummary?.foreign?.sell_million !== undefined) {
    return props.flowSummary.foreign.sell_million
  }
  return 12.76
})

const domesticBuy = computed(() => {
  if (props.flowSummary?.domestic?.buy_million !== undefined) {
    return props.flowSummary.domestic.buy_million
  }
  return 235.00
})

const domesticSell = computed(() => {
  if (props.flowSummary?.domestic?.sell_million !== undefined) {
    return props.flowSummary.domestic.sell_million
  }
  return 236.75
})

const foreignNet = computed(() => foreignBuy.value - foreignSell.value)
const domesticNet = computed(() => domesticBuy.value - domesticSell.value)

function formatNumber(val) {
  if (val === undefined || val === null || isNaN(val)) return '--'
  return Number(val).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatVolume(val) {
  if (!val) return '--'
  return Number(val).toLocaleString('vi-VN')
}
</script>
