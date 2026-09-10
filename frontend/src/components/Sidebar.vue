<template>
  <aside 
    class="hidden md:flex bg-theme-card border-r border-theme-border flex-col justify-between transition-all duration-300 z-30 shrink-0 select-none shadow-sm text-theme-text"
    :class="isCollapsed ? 'w-20' : 'w-64'"
  >
    <!-- Top: Logo & Collapse Button -->
    <div class="p-4 border-b border-theme-border flex items-center justify-between">
      <div class="flex items-center gap-3 overflow-hidden">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-md shadow-cyan-500/20 shrink-0">
          <TrendingUp class="w-5 h-5 text-slate-950 stroke-[2.5]" />
        </div>
        <div v-if="!isCollapsed" class="transition-opacity duration-200">
          <span class="font-bold text-sm text-theme-text tracking-tight block">QUANT & AI</span>
          <span class="text-[10px] font-mono text-cyan-600 dark:text-cyan-400">FINANCE PRO</span>
        </div>
      </div>

      <button 
        @click="isCollapsed = !isCollapsed"
        class="p-1.5 rounded-lg text-theme-muted hover:text-theme-text hover:bg-theme-subtle transition"
        :title="isCollapsed ? 'Mở rộng thanh điều hướng' : 'Thu gọn thanh điều hướng'"
      >
        <ChevronLeft v-if="!isCollapsed" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </div>

    <!-- Navigation Menu Items -->
    <nav class="p-3 space-y-1.5 flex-1 overflow-y-auto">
      
      <!-- Item 1: Thị Trường VN30 -->
      <button 
        @click="$emit('select-tab', 'dashboard')"
        class="w-full flex items-center gap-3 px-3 py-3 rounded-2xl text-xs font-semibold transition group relative"
        :class="activeTab === 'dashboard' 
          ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 font-bold' 
          : 'text-theme-sub hover:bg-theme-subtle hover:text-theme-text'"
        :title="isCollapsed ? 'Thị Trường VN30' : ''"
      >
        <LayoutDashboard class="w-5 h-5 shrink-0" :class="activeTab === 'dashboard' ? 'text-slate-950' : 'text-theme-muted group-hover:text-cyan-500'" />
        <span v-if="!isCollapsed" class="truncate text-left flex-1">Thị Trường VN30</span>
        <span v-if="!isCollapsed && activeTab === 'dashboard'" class="w-1.5 h-1.5 rounded-full bg-slate-950"></span>
      </button>

      <!-- Item 2: Tin Tức Thị Trường (Trong nước & Quốc tế) -->
      <button 
        @click="$emit('select-tab', 'news')"
        class="w-full flex items-center gap-3 px-3 py-3 rounded-2xl text-xs font-semibold transition group relative"
        :class="activeTab === 'news' 
          ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 font-bold' 
          : 'text-theme-sub hover:bg-theme-subtle hover:text-theme-text'"
        :title="isCollapsed ? 'Tin Tức Thị Trường' : ''"
      >
        <Newspaper class="w-5 h-5 shrink-0" :class="activeTab === 'news' ? 'text-slate-950' : 'text-theme-muted group-hover:text-cyan-500'" />
        <div v-if="!isCollapsed" class="flex items-center justify-between flex-1 truncate">
          <span class="truncate">Tin Tức Thị Trường</span>
          <span class="text-[9px] px-1.5 py-0.5 rounded-full font-mono font-bold" :class="activeTab === 'news' ? 'bg-slate-950/20 text-slate-950' : 'bg-rose-500/10 text-rose-500 border border-rose-500/30'">
            MỚI
          </span>
        </div>
      </button>

      <!-- Item 3: Đánh Giá Rủi Ro -->
      <button 
        @click="$emit('select-tab', 'risk')"
        class="w-full flex items-center gap-3 px-3 py-3 rounded-2xl text-xs font-semibold transition group relative"
        :class="activeTab === 'risk' 
          ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20 font-bold' 
          : 'text-theme-sub hover:bg-theme-subtle hover:text-theme-text'"
        :title="isCollapsed ? 'Đánh Giá Rủi Ro' : ''"
      >
        <ShieldAlert class="w-5 h-5 shrink-0" :class="activeTab === 'risk' ? 'text-slate-950' : 'text-theme-muted group-hover:text-amber-500'" />
        <div v-if="!isCollapsed" class="flex items-center justify-between flex-1 truncate">
          <span class="truncate">Đánh Giá Rủi Ro</span>
          <span class="text-[9px] px-1.5 py-0.5 rounded-full font-mono font-bold" :class="activeTab === 'risk' ? 'bg-slate-950/20 text-slate-950' : 'bg-amber-500/10 text-amber-500 border border-amber-500/30'">
            AI RISK
          </span>
        </div>
      </button>

    </nav>

    <!-- Bottom: System Status -->
    <div class="p-4 border-t border-theme-border text-xs">
      <div v-if="!isCollapsed" class="space-y-1">
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span class="font-mono text-[11px] text-theme-sub">Hệ thống Online</span>
        </div>
        <p class="text-[10px] text-theme-muted font-mono">Real-time &bull; VN30 v2.5</p>
      </div>
      <div v-else class="flex justify-center">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-500" title="Hệ thống đang hoạt động"></span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { 
  TrendingUp, 
  LayoutDashboard, 
  Newspaper, 
  ShieldAlert, 
  ChevronLeft, 
  ChevronRight 
} from 'lucide-vue-next'

defineProps({
  activeTab: {
    type: String,
    default: 'dashboard'
  }
})

defineEmits(['select-tab'])

const isCollapsed = ref(false)
</script>
