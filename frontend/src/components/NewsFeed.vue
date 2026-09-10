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
            🇻🇳 Trong Nước
          </button>
          <button 
            @click="setRegion('international')" 
            class="px-3 py-1.5 rounded-xl text-xs font-semibold transition flex items-center gap-1.5"
            :class="selectedRegion === 'international' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
          >
            🌐 Quốc Tế
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
                class="px-2 py-0.5 rounded-md font-bold whitespace-nowrap shrink-0"
                :class="item.region === 'domestic' ? 'bg-red-500/10 text-red-600 dark:text-red-400 border border-red-500/20' : 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20'"
              >
                {{ item.region === 'domestic' ? '🇻🇳 Trong Nước' : '🌐 Quốc Tế' }}
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

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Clock, Search, ExternalLink } from 'lucide-vue-next'
import { fetchNewsFeed } from '../api'

const newsList = ref([])
const isLoading = ref(true)
const selectedRegion = ref(null)
const selectedAsset = ref(null)
const searchKeyword = ref('')
const currentTime = ref('')

async function loadNews() {
  isLoading.value = true
  const data = await fetchNewsFeed()
  newsList.value = data
  isLoading.value = false
  currentTime.value = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
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

onMounted(() => {
  loadNews()
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
