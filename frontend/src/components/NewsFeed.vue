<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header Banner -->
    <div class="p-6 rounded-3xl bg-gradient-to-r from-cyan-500/10 via-theme-subtle to-emerald-500/10 border border-theme-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-rose-500/10 text-rose-500 border border-rose-500/30 flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping"></span> LIVE RADAR
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
            24/7 REAL-TIME
          </span>
          <h2 class="text-xl font-bold text-theme-text">Dòng Chảy Tin Tức Thị Trường Tài Chính</h2>
        </div>
        <p class="text-xs text-theme-sub mt-1">
          Cập nhật tức thì các biến số vĩ mô trong nước & thế giới tác động trực tiếp tới Cổ phiếu VN30, Giá Vàng, Bitcoin và Địa chính trị.
        </p>
      </div>

      <div class="flex items-center gap-2 text-xs font-mono text-theme-sub">
        <Clock class="w-4 h-4 text-cyan-500" />
        <span>Cập nhật: <strong class="text-theme-text">{{ currentTime }}</strong></span>
      </div>
    </div>

    <!-- ================= CỔ PHIẾU TĂNG NÓNG TRONG PHIÊN & GIẢI MÃ LÝ DO (HOT MOVERS RADAR) ================= -->
    <div class="p-5 rounded-3xl bg-gradient-to-br from-amber-500/10 via-theme-card to-emerald-500/10 border border-amber-500/30 shadow-md space-y-4">
      <!-- Section Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-theme-border pb-3">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-xl bg-amber-500/20 text-amber-500 border border-amber-500/30 flex items-center justify-center shrink-0 shadow-sm">
            <Flame class="w-5 h-5 animate-pulse text-amber-500" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-base font-bold text-theme-text flex items-center gap-1.5">
                <span>Cổ Phiếu Tăng Nóng Trong Phiên</span>
                <span class="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-600 dark:text-rose-400 border border-rose-500/30 animate-pulse">
                  RADAR CATALYST
                </span>
              </h3>
            </div>
            <p class="text-xs text-theme-sub mt-0.5">
              Tự động phát hiện các mã tăng giá bứt phá và giải mã chính xác nguyên nhân / tin tức kích hoạt đà tăng.
            </p>
          </div>
        </div>

        <span class="text-[11px] font-mono text-theme-sub flex items-center gap-1">
          <Sparkles class="w-3.5 h-3.5 text-amber-500" /> Bóc tách dòng tiền & sự kiện
        </span>
      </div>

      <!-- Hot Movers Grid Cards -->
      <div v-if="isLoadingMovers" class="py-6 text-center text-xs text-theme-sub font-mono">
        <div class="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
        Đang quét dữ liệu và giải mã các mã tăng nóng...
      </div>

      <div v-else-if="hotMovers.length === 0" class="p-4 text-center text-xs text-theme-sub">
        Chưa ghi nhận biến động tăng nóng đột biến trong phiên hiện tại.
      </div>

      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div 
          v-for="mover in hotMovers" 
          :key="mover.ticker"
          class="p-4 rounded-2xl bg-white dark:bg-slate-900/80 border border-theme-border hover:border-amber-500/50 shadow-sm hover:shadow-md transition duration-200 flex flex-col justify-between space-y-3 relative overflow-hidden group"
        >
          <!-- Accent Top Bar -->
          <div 
            class="absolute top-0 left-0 right-0 h-1"
            :class="mover.is_ceiling ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gradient-to-r from-emerald-500 to-cyan-500'"
          ></div>

          <!-- Mover Header: Ticker, Price, Change Badge -->
          <div class="flex items-start justify-between gap-3 pt-1">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-lg font-black font-mono text-theme-text group-hover:text-cyan-500 transition-colors">
                  {{ mover.ticker }}
                </span>
                <span class="text-xs text-theme-sub font-medium truncate max-w-[160px] sm:max-w-[210px]">
                  {{ mover.company_name }}
                </span>
              </div>
              <div class="flex items-center gap-2 text-[11px] font-mono text-theme-muted mt-0.5">
                <span>Giá: <strong class="text-theme-text font-bold">{{ mover.price }}</strong></span>
                <span>&bull;</span>
                <span>KL: <strong class="text-theme-text">{{ mover.volume_str }}</strong></span>
                <span class="px-1.5 py-0.2 rounded bg-theme-subtle text-[10px] text-cyan-600 dark:text-cyan-400 font-bold border border-theme-border">
                  {{ mover.vol_ratio }}
                </span>
              </div>
            </div>

            <!-- Status Badge -->
            <div class="flex flex-col items-end gap-1">
              <span 
                class="px-2.5 py-1 rounded-xl text-xs font-black font-mono shadow-sm flex items-center gap-1"
                :class="mover.is_ceiling ? 'bg-purple-500/20 text-purple-600 dark:text-purple-300 border border-purple-500/40' : 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/40'"
              >
                <TrendingUp class="w-3.5 h-3.5" />
                {{ mover.status_badge }}
              </span>
              <span class="text-[10px] font-mono text-amber-500 font-semibold">
                {{ mover.tag }}
              </span>
            </div>
          </div>

          <!-- Catalyst News (Chất xúc tác tin tức) -->
          <div class="p-2.5 rounded-xl bg-theme-subtle/70 border border-theme-border text-xs space-y-1">
            <div class="flex items-center gap-1.5 text-[11px] font-bold text-theme-text">
              <Zap class="w-3.5 h-3.5 text-amber-500 shrink-0" />
              <span>Tin tức & Sự kiện kích hoạt:</span>
            </div>
            <p class="text-xs font-semibold text-cyan-600 dark:text-cyan-400 leading-snug">
              {{ mover.catalyst_title }}
            </p>
            <p v-if="mover.catalyst_summary" class="text-[11px] text-theme-sub leading-relaxed">
              {{ mover.catalyst_summary }}
            </p>
          </div>

          <!-- Surge Reason Breakdown (Giải mã nguyên nhân tăng mạnh) -->
          <div class="p-3 rounded-xl bg-emerald-500/10 dark:bg-emerald-950/30 border border-emerald-500/20 text-xs space-y-1">
            <div class="flex items-center gap-1.5 text-[11px] font-bold text-emerald-700 dark:text-emerald-300">
              <Target class="w-3.5 h-3.5 text-emerald-500 shrink-0" />
              <span>Giải mã lý do tăng nóng:</span>
            </div>
            <p class="text-[11px] text-theme-text/90 leading-relaxed font-sans">
              {{ mover.surge_reason }}
            </p>
          </div>

          <!-- Actionable Note -->
          <div class="flex items-center justify-between gap-2 pt-1 border-t border-theme-border/60 text-[11px]">
            <span class="text-theme-muted font-mono flex items-center gap-1 truncate text-[10px]">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              {{ mover.flow_status }}
            </span>
            <span class="text-[10px] font-mono text-cyan-600 dark:text-cyan-400 shrink-0">
              {{ mover.actionable_insight.split('.')[0] }}
            </span>
          </div>

        </div>
      </div>
    </div>

    <!-- Filter Toolbar -->
    <div class="p-4 rounded-2xl bg-theme-card border border-theme-border shadow-sm space-y-4">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
        
        <!-- Region Filter (Trong Nước vs Quốc Tế) -->
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs text-theme-muted font-semibold mr-1">Khu vực:</span>
          <button 
            @click="setRegion(null)" 
            class="px-3 py-1.5 rounded-xl text-xs font-semibold transition"
            :class="selectedRegion === null ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
          >
            Tất cả ({{ newsList.length }})
          </button>
          <button 
            @click="setRegion('domestic')" 
            class="px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
            :class="selectedRegion === 'domestic' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
          >
            <MapPin class="w-3.5 h-3.5 text-rose-500" />
            <span>Trong Nước</span>
          </button>
          <button 
            @click="setRegion('international')" 
            class="px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
            :class="selectedRegion === 'international' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
          >
            <Globe class="w-3.5 h-3.5 text-cyan-500" />
            <span>Quốc Tế</span>
          </button>
        </div>

        <!-- Keyword Search Bar -->
        <div class="relative w-full md:w-80">
          <Search class="w-4 h-4 text-theme-muted absolute left-3 top-1/2 -translate-y-1/2" />
          <input 
            v-model="searchKeyword" 
            type="text" 
            placeholder="Tìm kiếm (ví dụ: vàng, fed, tỷ giá, btc)..." 
            class="w-full pl-9 pr-4 py-2 bg-theme-subtle border border-theme-border rounded-xl text-xs text-theme-text placeholder-theme-muted focus:outline-none focus:border-cyan-500 transition font-mono shadow-inner"
          />
        </div>
      </div>

      <!-- Asset Tags Filter -->
      <div class="flex flex-wrap items-center gap-2 pt-2 border-t border-theme-border">
        <span class="text-xs text-theme-muted font-semibold mr-1">Tài sản ảnh hưởng:</span>
        <button 
          @click="setAsset(null)"
          class="px-2.5 py-1 rounded-lg text-xs transition"
          :class="selectedAsset === null ? 'bg-theme-text text-theme-bg font-bold' : 'text-theme-sub hover:text-theme-text'"
        >
          Tất cả
        </button>
        <button 
          @click="setAsset('stocks')"
          class="px-2.5 py-1 rounded-lg text-xs transition flex items-center gap-1"
          :class="selectedAsset === 'stocks' ? 'bg-emerald-500 text-white font-bold' : 'text-theme-sub hover:text-emerald-500'"
        >
          📈 Cổ Phiếu VN30
        </button>
        <button 
          @click="setAsset('gold')"
          class="px-2.5 py-1 rounded-lg text-xs transition flex items-center gap-1"
          :class="selectedAsset === 'gold' ? 'bg-amber-500 text-slate-950 font-bold' : 'text-theme-sub hover:text-amber-500'"
        >
          🥇 Giá Vàng (SJC / Spot Gold)
        </button>
        <button 
          @click="setAsset('btc')"
          class="px-2.5 py-1 rounded-lg text-xs transition flex items-center gap-1"
          :class="selectedAsset === 'btc' ? 'bg-cyan-500 text-slate-950 font-bold' : 'text-theme-sub hover:text-cyan-500'"
        >
          🪙 Bitcoin (BTC / Crypto)
        </button>
        <button 
          @click="setAsset('politics')"
          class="px-2.5 py-1 rounded-lg text-xs transition flex items-center gap-1"
          :class="selectedAsset === 'politics' ? 'bg-rose-500 text-white font-bold' : 'text-theme-sub hover:text-rose-500'"
        >
          ⚔️ Chính Trị & Địa Chính Trị
        </button>
      </div>
    </div>

    <!-- News List -->
    <div v-if="isLoading" class="py-16 text-center space-y-3">
      <div class="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
      <p class="text-xs text-theme-muted font-mono">Đang tổng hợp tin tức tài chính mới nhất...</p>
    </div>

    <div v-else-if="filteredNews.length === 0" class="p-12 text-center rounded-2xl bg-theme-card border border-theme-border">
      <p class="text-theme-sub text-sm">Không tìm thấy tin tức nào khớp với bộ lọc hoặc từ khóa.</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div 
        v-for="item in filteredNews" 
        :key="item.id"
        class="p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm hover:shadow-md hover:border-cyan-500/40 transition duration-200 flex flex-col justify-between space-y-4"
      >
        <!-- Card Header Badges -->
        <div class="space-y-2.5">
          <div class="flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono">
            <div class="flex items-center gap-1.5">
              <!-- Region badge -->
              <span 
                class="px-2 py-0.5 rounded-md font-bold whitespace-nowrap shrink-0 flex items-center gap-1"
                :class="item.region === 'domestic' ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20' : 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'"
              >
                <MapPin v-if="item.region === 'domestic'" class="w-3 h-3 text-rose-500" />
                <Globe v-else class="w-3 h-3 text-blue-500" />
                <span>{{ item.region === 'domestic' ? 'Trong Nước' : 'Quốc Tế' }}</span>
              </span>

              <!-- Source -->
              <span class="text-theme-muted">&bull; {{ item.source }}</span>
            </div>

            <!-- Published At -->
            <span class="text-theme-muted flex items-center gap-1 whitespace-nowrap shrink-0">
              <Clock class="w-3 h-3" /> {{ item.published_at }}
            </span>
          </div>

          <!-- Title -->
          <h3 class="text-sm sm:text-base font-bold text-theme-text leading-snug hover:text-cyan-500 transition">
            <a 
              v-if="item.url" 
              :href="item.url" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="hover:text-cyan-500 transition-colors"
            >
              {{ item.title }}
            </a>
            <span v-else>{{ item.title }}</span>
          </h3>

          <!-- Summary -->
          <p class="text-xs text-theme-sub leading-relaxed">
            {{ item.summary }}
          </p>

          <!-- Source Citation Link (Link bài viết trích dẫn) -->
          <div v-if="item.url" class="pt-1 flex items-center">
            <a 
              :href="item.url" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-theme-subtle hover:bg-cyan-500/10 border border-theme-border hover:border-cyan-500/30 text-xs font-semibold text-cyan-600 dark:text-cyan-400 hover:text-cyan-500 dark:hover:text-cyan-300 transition-all group/link shadow-sm"
              title="Mở bài viết trích dẫn gốc"
            >
              <ExternalLink class="w-3.5 h-3.5 shrink-0 group-hover/link:translate-x-0.5 group-hover/link:-translate-y-0.5 transition-transform" />
              <span>Nguồn trích dẫn: {{ item.source }}</span>
            </a>
          </div>
        </div>

        <!-- Card Footer: Impacted Asset & Sentiment -->
        <div class="pt-3 border-t border-theme-border flex flex-wrap items-center justify-between gap-2 text-xs">
          <!-- Tags -->
          <div class="flex flex-wrap items-center gap-1.5">
            <span 
              v-for="tag in item.asset_tags" 
              :key="tag"
              class="px-2 py-0.5 rounded-md bg-theme-subtle text-theme-sub text-[10px] font-mono font-medium"
            >
              #{{ tag }}
            </span>
          </div>

          <!-- Impact Status Badge -->
          <div class="flex items-center gap-2 shrink-0">
            <span 
              class="px-2.5 py-0.5 rounded-full text-[10px] font-bold whitespace-nowrap shrink-0"
              :class="getSentimentClass(item.sentiment)"
            >
              {{ item.sentiment_label }}
            </span>
          </div>
        </div>

        <!-- Khối Phân Tích Cổ Phiếu Tác Động & Kết Luận Cơ Chế (Luôn hiển thị 100%) -->
        <div class="mt-3 p-3.5 rounded-xl border bg-theme-subtle/80 dark:bg-slate-900/60 border-cyan-500/30 text-xs space-y-2 shadow-inner">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div class="flex items-center gap-1.5 font-semibold text-theme-text min-w-0">
              <Target class="w-4 h-4 text-cyan-500 shrink-0" />
              <span class="text-theme-sub text-[11px] whitespace-nowrap">Cổ phiếu / Nhóm tác động:</span>
              <span 
                class="font-mono px-2.5 py-0.5 rounded-md text-[11px] font-bold truncate bg-cyan-500/15 text-cyan-700 dark:text-cyan-300 border border-cyan-500/30 shadow-sm"
              >
                {{ item.affected_stocks || 'Toàn rổ VN30 & Cổ phiếu liên quan' }}
              </span>
            </div>

            <!-- Mức độ tác động -->
            <span 
              class="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase tracking-wider shrink-0"
              :class="getImpactDegreeClass(item.impact_degree, item.is_direct_stock_impact)"
            >
              {{ item.impact_degree || 'Trực tiếp' }}
            </span>
          </div>

          <!-- Kết luận & Lý do tại sao ảnh hưởng -->
          <div class="pt-1.5 border-t border-theme-border/60 text-[11px] leading-relaxed">
            <div class="text-theme-text font-semibold flex items-center gap-1 mb-1">
              <Zap class="w-3.5 h-3.5 text-amber-500 shrink-0" />
              <span>Kết luận tác động & Cơ chế lý giải:</span>
            </div>
            <p class="text-theme-sub font-normal leading-relaxed pl-4">
              {{ item.impact_reason || 'Tin tức vĩ mô / kinh tế tác động trực tiếp đến dòng tiền thị trường và tâm lý nhà đầu tư giao dịch rổ VN30.' }}
            </p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Clock, Search, ExternalLink, MapPin, Globe, Target, Flame, Zap, TrendingUp, Sparkles } from 'lucide-vue-next'
import { fetchNewsFeed, fetchHotMovers } from '../api'

const newsList = ref([])
const hotMovers = ref([])
const isLoading = ref(true)
const isLoadingMovers = ref(true)
const selectedRegion = ref(null)
const selectedAsset = ref(null)
const searchKeyword = ref('')
const currentTime = ref('')
let newsTimer = null

async function loadNews(isInitial = false) {
  if (isInitial) {
    isLoading.value = true
    isLoadingMovers.value = true
  }
  try {
    const [newsData, moversData] = await Promise.all([
      fetchNewsFeed(),
      fetchHotMovers()
    ])
    if (newsData && newsData.length > 0) {
      newsList.value = newsData
    }
    if (moversData && moversData.length > 0) {
      hotMovers.value = moversData
    }
  } catch (err) {
    console.error('Lỗi nạp tin tức và cổ phiếu tăng nóng:', err)
  } finally {
    if (isInitial) {
      isLoading.value = false
      isLoadingMovers.value = false
    }
    currentTime.value = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
  }
}

function setRegion(r) {
  selectedRegion.value = r
}

function setAsset(a) {
  selectedAsset.value = a
}

const filteredNews = computed(() => {
  let list = [...newsList.value]

  if (selectedRegion.value) {
    list = list.filter(n => n.region === selectedRegion.value)
  }

  if (selectedAsset.value) {
    list = list.filter(n => n.asset_category === selectedAsset.value || n.asset_tags?.some(t => t.toLowerCase().includes(selectedAsset.value)))
  }

  if (searchKeyword.value.trim()) {
    const q = searchKeyword.value.toLowerCase().trim()
    list = list.filter(n => 
      n.title?.toLowerCase().includes(q) || 
      n.summary?.toLowerCase().includes(q) ||
      n.asset_tags?.some(t => t.toLowerCase().includes(q))
    )
  }

  return list
})

function getSentimentClass(sentiment) {
  if (sentiment === 'positive') return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
  if (sentiment === 'negative') return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
  return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
}

function getImpactDegreeClass(degree, isDirect) {
  if (!isDirect || degree === 'Không ảnh hưởng') {
    return 'bg-slate-500/10 text-slate-500 dark:text-slate-400 border border-slate-500/20'
  }
  if (degree === 'Trực tiếp') {
    return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
  }
  if (degree === 'Ngành trọng điểm') {
    return 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
  }
  if (degree === 'Toàn thị trường') {
    return 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/30'
  }
  return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
}

onMounted(() => {
  loadNews(true)
  newsTimer = setInterval(() => {
    loadNews(false)
  }, 30000)
})

onBeforeUnmount(() => {
  if (newsTimer) clearInterval(newsTimer)
})
</script>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeIn 0.25s ease-out;
}
</style>
