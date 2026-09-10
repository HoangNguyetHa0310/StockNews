<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 z-[70] flex items-center justify-center p-4 bg-theme-backdrop backdrop-blur-md animate-fade-in"
    @click.self="$emit('close')"
  >
    <div class="relative w-full max-w-5xl max-h-[92vh] bg-theme-card border border-theme-border text-theme-text rounded-3xl shadow-2xl overflow-hidden flex flex-col transition-colors duration-200">
      
      <!-- Modal Header -->
      <div class="p-6 border-b border-theme-border flex items-center justify-between bg-theme-subtle">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-600 dark:text-cyan-400 font-bold font-mono text-xl">
            {{ stock?.ticker }}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-xl font-bold text-slate-900 dark:text-white font-mono">{{ stock?.ticker }}</h3>
              <span v-html="getSignalBadge(stock?.signal)"></span>
            </div>
            <p class="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">
              Giá: <span class="text-slate-900 dark:text-white font-bold">{{ formatPrice(stock?.close) }}</span>
              <span :class="stock?.change_pct >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400'" class="ml-1 font-semibold">
                ({{ stock?.change_pct >= 0 ? '+' : '' }}{{ stock?.change_pct?.toFixed(2) }}%)
              </span>
              &bull; RSI: {{ stock?.rsi }} &bull; Vol/MA20: {{ stock?.vol_vs_ma20 }}x
            </p>
          </div>
        </div>

        <button 
          @click="$emit('close')" 
          class="w-9 h-9 rounded-xl bg-theme-subtle hover:bg-theme-subtle-2 text-theme-muted hover:text-theme-text flex items-center justify-center transition border border-theme-border shadow-sm"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Modal Body (Scrollable) -->
      <div class="p-6 overflow-y-auto space-y-6 flex-1 text-theme-text">

        <!-- 4 Score Cards -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="p-3.5 rounded-2xl bg-theme-subtle border border-theme-border">
            <span class="text-[11px] text-theme-sub font-medium">Xu Hướng (Trend)</span>
            <div class="text-lg font-bold font-mono text-theme-text mt-0.5">{{ stock?.trend_score }} / 100</div>
            <div class="w-full bg-theme-subtle-2 h-1.5 rounded-full mt-2 overflow-hidden">
              <div class="bg-cyan-500 h-full" :style="{ width: stock?.trend_score + '%' }"></div>
            </div>
          </div>

          <div class="p-3.5 rounded-2xl bg-theme-subtle border border-theme-border">
            <span class="text-[11px] text-theme-sub font-medium">Động Lượng (Momentum)</span>
            <div class="text-lg font-bold font-mono text-theme-text mt-0.5">{{ stock?.momentum_score }} / 100</div>
            <div class="w-full bg-theme-subtle-2 h-1.5 rounded-full mt-2 overflow-hidden">
              <div class="bg-emerald-500 h-full" :style="{ width: stock?.momentum_score + '%' }"></div>
            </div>
          </div>

          <div class="p-3.5 rounded-2xl bg-theme-subtle border border-theme-border">
            <span class="text-[11px] text-theme-sub font-medium">Dòng Tiền (Money Flow)</span>
            <div class="text-lg font-bold font-mono text-theme-text mt-0.5">{{ stock?.flow_score }} / 100</div>
            <div class="w-full bg-theme-subtle-2 h-1.5 rounded-full mt-2 overflow-hidden">
              <div class="bg-amber-500 h-full" :style="{ width: stock?.flow_score + '%' }"></div>
            </div>
          </div>

          <div class="p-3.5 rounded-2xl bg-theme-subtle border border-theme-border">
            <span class="text-[11px] text-theme-sub font-medium">Xác Suất Tăng AI (T+3)</span>
            <div class="text-lg font-bold font-mono text-cyan-600 dark:text-cyan-300 mt-0.5">{{ stock?.ml_prob_up }}%</div>
            <div class="w-full bg-theme-subtle-2 h-1.5 rounded-full mt-2 overflow-hidden">
              <div class="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full" :style="{ width: stock?.ml_prob_up + '%' }"></div>
            </div>
          </div>
        </div>

        <!-- Strategy Levels Banner -->
        <div class="p-4 rounded-2xl bg-theme-subtle border border-theme-border flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
          <div class="flex items-center gap-2">
            <span class="text-theme-sub">Vùng Mua:</span>
            <span class="px-2.5 py-1 rounded-lg bg-cyan-500/10 text-cyan-600 dark:text-cyan-300 font-bold border border-cyan-500/20">
              {{ stock?.entry_range || '--' }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-theme-sub">Cắt Lỗ (Stoploss):</span>
            <span class="px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold border border-rose-500/20">
              {{ formatPrice(stock?.stoploss) }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-theme-sub">Mục Tiêu 1 (Target):</span>
            <span class="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/20">
              {{ formatPrice(stock?.target_1) }}
            </span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-theme-sub">Tỷ Lệ R/R:</span>
            <span class="font-bold text-theme-text">{{ stock?.risk_reward_ratio }} : 1</span>
          </div>
        </div>

        <!-- TradingView Candlestick Chart Container -->
        <div class="bg-theme-subtle p-4 rounded-2xl border border-theme-border space-y-2">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-bold text-theme-text uppercase tracking-wider flex items-center gap-2">
              <Activity class="w-4 h-4 text-cyan-500" />
              Biểu Đồ Nến Nhật & Khối Lượng (TradingView Engine)
            </h4>
            <span v-if="isLoadingCandles" class="text-xs text-theme-muted font-mono animate-pulse">
              Đang tải dữ liệu nến...
            </span>
          </div>

          <!-- Chart Div -->
          <div ref="chartContainer" class="w-full h-80 rounded-xl overflow-hidden"></div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="p-4 border-t border-theme-border bg-theme-subtle flex justify-end">
        <button 
          @click="$emit('close')" 
          class="px-5 py-2 rounded-xl bg-theme-subtle-2 hover:bg-theme-border text-theme-text text-xs font-semibold transition shadow-sm"
        >
          Đóng
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { X, Activity } from 'lucide-vue-next'
import { createChart } from 'lightweight-charts'
import { fetchStockCandles } from '../api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  stock: {
    type: Object,
    default: null
  }
})

defineEmits(['close'])

const chartContainer = ref(null)
const isLoadingCandles = ref(false)
let chart = null
let candleSeries = null
let volumeSeries = null

watch(() => props.isOpen, async (val) => {
  if (val && props.stock) {
    await nextTick()
    renderChart()
  } else {
    destroyChart()
  }
})

watch(() => props.stock, async () => {
  if (props.isOpen && props.stock) {
    await nextTick()
    renderChart()
  }
})

async function renderChart() {
  if (!chartContainer.value || !props.stock) return
  destroyChart()

  isLoadingCandles.value = true
  const candles = await fetchStockCandles(props.stock.ticker, 120)
  isLoadingCandles.value = false

  if (!candles || candles.length === 0) return

  const isDark = document.documentElement.classList.contains('dark')

  // Khởi tạo Lightweight Chart với màu sắc thích ứng theo Dark/Light Mode
  chart = createChart(chartContainer.value, {
    layout: {
      background: { color: isDark ? '#0b1120' : '#ffffff' },
      textColor: isDark ? '#94a3b8' : '#475569',
      fontFamily: 'JetBrains Mono',
    },
    grid: {
      vertLines: { color: isDark ? '#1e293b' : '#f1f5f9' },
      horzLines: { color: isDark ? '#1e293b' : '#f1f5f9' },
    },
    crosshair: {
      mode: 1,
    },
    rightPriceScale: {
      borderColor: isDark ? '#334155' : '#cbd5e1',
    },
    timeScale: {
      borderColor: isDark ? '#334155' : '#cbd5e1',
      timeVisible: false,
    },
  })

  // Series nến
  candleSeries = chart.addCandlestickSeries({
    upColor: '#10b981',
    downColor: '#ef4444',
    borderVisible: false,
    wickUpColor: '#10b981',
    wickDownColor: '#ef4444',
  })

  candleSeries.setData(candles)

  // Series Volume
  volumeSeries = chart.addHistogramSeries({
    color: '#38bdf8',
    priceFormat: {
      type: 'volume',
    },
    priceScaleId: '',
  })

  volumeSeries.priceScale().applyOptions({
    scaleMargins: {
      top: 0.8,
      bottom: 0,
    },
  })

  const volData = candles.map(c => ({
    time: c.time,
    value: c.volume,
    color: c.close >= c.open ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'
  }))
  volumeSeries.setData(volData)

  // Đường kẻ Target & Stoploss
  if (props.stock.target_1) {
    candleSeries.createPriceLine({
      price: props.stock.target_1,
      color: '#10b981',
      lineWidth: 2,
      lineStyle: 1,
      axisLabelVisible: true,
      title: 'TARGET 1',
    })
  }

  if (props.stock.stoploss) {
    candleSeries.createPriceLine({
      price: props.stock.stoploss,
      color: '#ef4444',
      lineWidth: 2,
      lineStyle: 1,
      axisLabelVisible: true,
      title: 'STOPLOSS',
    })
  }

  chart.timeScale().fitContent()
}

function destroyChart() {
  if (chart) {
    chart.remove()
    chart = null
    candleSeries = null
    volumeSeries = null
  }
}

onBeforeUnmount(() => {
  destroyChart()
})

function formatPrice(val) {
  if (!val) return '--'
  return Number(val).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getSignalBadge(signal) {
  if (!signal) return ''
  if (signal.includes('MUA MẠNH')) {
    return `<span class="whitespace-nowrap inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/40">MUA MẠNH</span>`
  } else if (signal.includes('MUA')) {
    return `<span class="whitespace-nowrap inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-300 border border-emerald-500/20">MUA</span>`
  } else if (signal.includes('BÁN MẠNH')) {
    return `<span class="whitespace-nowrap inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/20 text-rose-600 dark:text-rose-400 border border-rose-500/40">BÁN MẠNH</span>`
  } else if (signal.includes('BÁN')) {
    return `<span class="whitespace-nowrap inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-600 dark:text-rose-300 border border-rose-500/20">BÁN</span>`
  } else if (signal.includes('Chờ AI')) {
    return `<span class="whitespace-nowrap inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-cyan-500/20 text-cyan-600 dark:text-cyan-300 border border-cyan-500/40">THEO DÕI (CHỜ AI)</span>`
  } else {
    return `<span class="whitespace-nowrap inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-600 dark:text-amber-300 border border-amber-500/20">QUAN SÁT</span>`
  }
}
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to { opacity: 1; transform: scale(1); }
}
.animate-fade-in {
  animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
</style>
