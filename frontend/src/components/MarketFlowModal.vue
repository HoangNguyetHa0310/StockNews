<template>
  <div 
    v-if="isOpen" 
    class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-6 bg-theme-backdrop backdrop-blur-md animate-fade-in overflow-y-auto"
    style="padding-top: max(1.25rem, env(safe-area-inset-top, 24px)); padding-bottom: max(3rem, calc(3rem + env(safe-area-inset-bottom, 24px)));"
    @click.self="$emit('close')"
  >
    <div 
      class="bg-theme-card border border-theme-border rounded-2xl sm:rounded-3xl w-full max-w-7xl max-h-[calc(100dvh-5rem)] sm:max-h-[90vh] flex flex-col shadow-2xl overflow-hidden transition-colors duration-200 my-auto text-theme-text"
    >
      <!-- ==================== MODAL HEADER ==================== -->
      <div class="px-4 sm:px-6 py-3.5 sm:py-5 border-b border-theme-border flex items-center justify-between bg-theme-subtle">
        <div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
          <div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 shrink-0">
            <ArrowLeftRight class="w-4 h-4 sm:w-5 sm:h-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div class="min-w-0 truncate">
            <div class="flex items-center gap-2">
              <h2 class="text-sm sm:text-base font-bold tracking-tight text-theme-text truncate">
                BÁO CÁO DÒNG TIỀN KHỐI NGOẠI & TỰ DOANH VN30
              </h2>
              <span class="text-[9px] sm:text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30 shrink-0">
                REAL-TIME DATA
              </span>
            </div>
            <p class="text-[10px] sm:text-xs text-theme-muted hidden sm:block truncate mt-0.5">
              Theo dõi biến động dòng vốn Khối Ngoại & Khối Nội theo phiên, 1 tuần và 1 tháng
            </p>
          </div>
        </div>

        <button 
          @click="$emit('close')"
          class="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 flex items-center justify-center transition border border-theme-border shadow-md shrink-0 active:scale-95"
          title="Đóng cửa sổ (Esc)"
        >
          <X class="w-5 h-5 text-slate-600 dark:text-slate-300" />
        </button>
      </div>

      <!-- ==================== PERIOD SELECTOR BAR ==================== -->
      <div class="px-4 sm:px-6 py-2.5 sm:py-3 border-b border-theme-border bg-theme-subtle flex flex-wrap items-center justify-between gap-2.5 sm:gap-3">
        <!-- 3 Time Period Tabs -->
        <div class="flex items-center gap-1.5 p-1 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-theme-border text-xs font-semibold">
          <button 
            @click="switchPeriod('today')"
            class="px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5 font-mono"
            :class="selectedPeriod === 'today' 
              ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm shadow-cyan-500/30' 
              : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'"
          >
            <Zap class="w-3.5 h-3.5" />
            <span>Hôm nay (1 phiên)</span>
          </button>

          <button 
            @click="switchPeriod('1_week')"
            class="px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5 font-mono"
            :class="selectedPeriod === '1_week' 
              ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm shadow-cyan-500/30' 
              : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'"
          >
            <Calendar class="w-3.5 h-3.5" />
            <span>1 tuần qua (5 phiên)</span>
          </button>

          <button 
            @click="switchPeriod('1_month')"
            class="px-3.5 py-1.5 rounded-lg transition flex items-center gap-1.5 font-mono"
            :class="selectedPeriod === '1_month' 
              ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm shadow-cyan-500/30' 
              : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-700/60'"
          >
            <Clock class="w-3.5 h-3.5" />
            <span>1 tháng qua (20 phiên)</span>
          </button>
        </div>

        <!-- Info Badges -->
        <div class="flex items-center gap-3 text-xs font-mono text-theme-sub">
          <span class="flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Phiên chốt: <strong class="text-theme-text">{{ flowData?.latest_date || '--' }}</strong>
          </span>
          <span class="hidden md:inline">•</span>
          <span class="hidden md:inline text-cyan-600 dark:text-cyan-400 font-semibold">
            Đơn vị tính: Triệu Cổ Phiếu (Tr CP)
          </span>
        </div>
      </div>

      <!-- ==================== MODAL BODY (SCROLLABLE) ==================== -->
      <div class="p-6 overflow-y-auto space-y-6 flex-1 text-theme-text">
        
        <!-- Loading State -->
        <div v-if="isLoading" class="py-20 text-center space-y-3">
          <div class="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p class="text-xs text-slate-500 dark:text-slate-400 font-mono">Đang tổng hợp khối lượng mua bán Khối ngoại & Trong nước rổ VN30...</p>
        </div>

        <template v-else>
          <!-- Section 1: 4 Metric Cards Tổng Hợp Rổ VN30 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            <!-- Card 1: Khối Ngoại (Foreign Investors) -->
            <div class="p-4 rounded-2xl bg-theme-card border border-cyan-500/30 shadow-sm relative overflow-hidden">
              <div class="flex justify-between items-start">
                <div>
                  <p class="text-[11px] font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider flex items-center gap-1">
                    <Globe class="w-3.5 h-3.5" /> Khối Ngoại (Nước Ngoài)
                  </p>
                  <div class="mt-2 space-y-1 font-mono text-xs">
                    <div class="flex items-center justify-between gap-2">
                      <span class="text-theme-sub">Mua:</span>
                      <span class="font-bold text-emerald-500 dark:text-emerald-400">{{ formatNumber(flowData?.summary?.foreign?.buy_million) }} Tr CP</span>
                    </div>
                    <div class="flex items-center justify-between gap-2">
                      <span class="text-theme-sub">Bán:</span>
                      <span class="font-bold text-rose-500 dark:text-rose-400">{{ formatNumber(flowData?.summary?.foreign?.sell_million) }} Tr CP</span>
                    </div>
                  </div>
                </div>
                <div class="p-2 rounded-xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/20">
                  <Globe class="w-4 h-4" />
                </div>
              </div>
              
              <div class="mt-3 pt-2.5 border-t border-theme-border flex items-center justify-between text-xs font-mono">
                <span class="text-theme-sub font-semibold">Mua/Bán Ròng:</span>
                <span 
                  class="font-bold px-2 py-0.5 rounded text-[11px]"
                  :class="(flowData?.summary?.foreign?.net_million || 0) >= 0 
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                    : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'"
                >
                  {{ (flowData?.summary?.foreign?.net_million || 0) >= 0 ? '+' : '' }}{{ formatNumber(flowData?.summary?.foreign?.net_million) }} Tr CP
                </span>
              </div>
              <div class="mt-2 text-[10px] text-theme-muted font-mono flex items-center justify-between">
                <span>Tỷ trọng tham gia:</span>
                <span class="font-semibold text-theme-text">{{ flowData?.summary?.foreign?.participation_pct || 0 }}%</span>
              </div>
            </div>

            <!-- Card 2: Nhà Đầu Tư Trong Nước (Domestic Investors) -->
            <div class="p-4 rounded-2xl bg-theme-card border border-emerald-500/30 shadow-sm relative overflow-hidden">
              <div class="flex justify-between items-start">
                <div>
                  <p class="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                    <Users class="w-3.5 h-3.5" /> Nhà Đầu Tư Trong Nước
                  </p>
                  <div class="mt-2 space-y-1 font-mono text-xs">
                    <div class="flex items-center justify-between gap-2">
                      <span class="text-theme-sub">Mua:</span>
                      <span class="font-bold text-emerald-500 dark:text-emerald-400">{{ formatNumber(flowData?.summary?.domestic?.buy_million) }} Tr CP</span>
                    </div>
                    <div class="flex items-center justify-between gap-2">
                      <span class="text-theme-sub">Bán:</span>
                      <span class="font-bold text-rose-500 dark:text-rose-400">{{ formatNumber(flowData?.summary?.domestic?.sell_million) }} Tr CP</span>
                    </div>
                  </div>
                </div>
                <div class="p-2 rounded-xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  <Users class="w-4 h-4" />
                </div>
              </div>

              <div class="mt-3 pt-2.5 border-t border-theme-border flex items-center justify-between text-xs font-mono">
                <span class="text-theme-sub font-semibold">Mua/Bán Ròng:</span>
                <span 
                  class="font-bold px-2 py-0.5 rounded text-[11px]"
                  :class="(flowData?.summary?.domestic?.net_million || 0) >= 0 
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                    : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'"
                >
                  {{ (flowData?.summary?.domestic?.net_million || 0) >= 0 ? '+' : '' }}{{ formatNumber(flowData?.summary?.domestic?.net_million) }} Tr CP
                </span>
              </div>
              <div class="mt-2 text-[10px] text-theme-muted font-mono flex items-center justify-between">
                <span>Tỷ trọng tham gia:</span>
                <span class="font-semibold text-theme-text">{{ flowData?.summary?.domestic?.participation_pct || 0 }}%</span>
              </div>
            </div>

            <!-- Card 3: Tổng Khối Lượng Toàn Rổ VN30 -->
            <div class="p-4 rounded-2xl bg-theme-card border border-theme-border shadow-sm relative overflow-hidden">
              <div class="flex justify-between items-start">
                <div>
                  <p class="text-[11px] font-bold text-theme-sub uppercase tracking-wider flex items-center gap-1">
                    <Layers class="w-3.5 h-3.5" /> Tổng Khối Lượng Khớp Lệnh
                  </p>
                  <h3 class="text-2xl font-bold font-mono text-theme-text mt-2">
                    {{ formatNumber(flowData?.summary?.total_vn30_volume_million) }}
                    <span class="text-xs font-semibold text-theme-sub">Tr CP</span>
                  </h3>
                  <p class="text-[11px] text-theme-muted font-mono mt-0.5">
                    30 cổ phiếu đầu ngành VN30
                  </p>
                </div>
                <div class="p-2 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">
                  <BarChart3 class="w-4 h-4" />
                </div>
              </div>

              <div class="mt-3 pt-2.5 border-t border-theme-border flex items-center justify-between text-xs font-mono text-theme-sub">
                <span>Số mã Ngoại gom:</span>
                <span class="font-bold text-emerald-500 dark:text-emerald-400">
                  {{ flowData?.summary?.foreign?.net_buy_count || 0 }} / 30 mã
                </span>
              </div>
              <div class="mt-2 text-[10px] text-theme-muted font-mono flex items-center justify-between">
                <span>Số mã Ngoại xả:</span>
                <span class="font-bold text-rose-500 dark:text-rose-400">
                  {{ flowData?.summary?.foreign?.net_sell_count || 0 }} / 30 mã
                </span>
              </div>
            </div>

            <!-- Card 4: Tâm Điểm Dòng Tiền Ngoại -->
            <div class="p-4 rounded-2xl bg-gradient-to-br from-cyan-500/5 to-purple-500/5 bg-theme-card border border-theme-border shadow-sm relative overflow-hidden">
              <div class="flex justify-between items-start">
                <div>
                  <p class="text-[11px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider flex items-center gap-1">
                    <Flame class="w-3.5 h-3.5" /> Tâm Điểm Giao Dịch
                  </p>
                  <div class="mt-2 space-y-1 text-xs">
                    <div>
                      <span class="text-[10px] text-theme-muted block">Ngoại Mua ròng top đầu:</span>
                      <div class="flex flex-wrap gap-1 mt-0.5">
                        <span 
                          v-for="s in (flowData?.top_foreign_net_buy || []).slice(0, 3)" 
                          :key="s.ticker"
                          class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                        >
                          {{ s.ticker }} (+{{ s.foreign_net_million }}M)
                        </span>
                      </div>
                    </div>

                    <div class="pt-1">
                      <span class="text-[10px] text-theme-muted block">Ngoại Bán ròng top đầu:</span>
                      <div class="flex flex-wrap gap-1 mt-0.5">
                        <span 
                          v-for="s in (flowData?.top_foreign_net_sell || []).slice(0, 3)" 
                          :key="s.ticker"
                          class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20"
                        >
                          {{ s.ticker }} ({{ s.foreign_net_million }}M)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- Section 2: Search & Filter Pills -->
          <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
            <!-- Search Input -->
            <div class="relative flex-1 max-w-md">
              <Search class="w-4 h-4 text-theme-muted absolute left-3 top-1/2 -translate-y-1/2" />
              <input 
                v-model="searchQuery"
                type="text"
                placeholder="Tìm mã cổ phiếu (VCB, FPT, HPG...) hoặc tên công ty..."
                class="w-full pl-9 pr-4 py-2 rounded-xl bg-theme-input border border-theme-border text-xs text-theme-text placeholder-theme-muted focus:outline-none focus:border-cyan-500 transition"
              />
              <button 
                v-if="searchQuery" 
                @click="searchQuery = ''"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-theme-muted hover:text-theme-text text-xs"
              >
                ✕
              </button>
            </div>

            <!-- Filter Buttons -->
            <div class="flex items-center flex-wrap gap-1.5 text-xs font-semibold">
              <button 
                @click="activeFilter = 'ALL'"
                class="px-3 py-1.5 rounded-xl border transition"
                :class="activeFilter === 'ALL'
                  ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-sm'
                  : 'bg-theme-card border-theme-border text-theme-sub hover:text-theme-text'"
              >
                Tất cả ({{ allStocksCount }})
              </button>

              <button 
                @click="activeFilter = 'FOREIGN_BUY'"
                class="px-3 py-1.5 rounded-xl border transition flex items-center gap-1"
                :class="activeFilter === 'FOREIGN_BUY'
                  ? 'bg-emerald-500 text-slate-950 border-emerald-500 font-bold shadow-sm'
                  : 'bg-theme-card border-theme-border text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20'"
              >
                <span>Ngoại Mua Ròng</span>
                <span class="text-[10px] font-mono px-1 rounded bg-black/10">({{ countForeignBuy }})</span>
              </button>

              <button 
                @click="activeFilter = 'FOREIGN_SELL'"
                class="px-3 py-1.5 rounded-xl border transition flex items-center gap-1"
                :class="activeFilter === 'FOREIGN_SELL'
                  ? 'bg-rose-500 text-white border-rose-500 font-bold shadow-sm'
                  : 'bg-theme-card border-theme-border text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20'"
              >
                <span>Ngoại Bán Ròng</span>
                <span class="text-[10px] font-mono px-1 rounded bg-black/10">({{ countForeignSell }})</span>
              </button>

              <button 
                @click="activeFilter = 'DOMESTIC_BUY'"
                class="px-3 py-1.5 rounded-xl border transition flex items-center gap-1"
                :class="activeFilter === 'DOMESTIC_BUY'
                  ? 'bg-cyan-500 text-slate-950 border-cyan-500 font-bold shadow-sm'
                  : 'bg-theme-card border-theme-border text-cyan-600 dark:text-cyan-400 hover:bg-cyan-50 dark:hover:bg-cyan-950/20'"
              >
                <span>Trong Nước Mua Ròng</span>
                <span class="text-[10px] font-mono px-1 rounded bg-black/10">({{ countDomesticBuy }})</span>
              </button>
            </div>
          </div>

          <!-- Section 3: Detailed Table of 30 VN30 Stocks -->
          <div class="rounded-2xl border border-theme-border overflow-hidden bg-theme-card shadow-sm">
            <!-- Mobile Scroll Hint -->
            <div class="md:hidden px-3.5 py-2 bg-cyan-500/5 border-b border-theme-border flex items-center justify-between gap-2 text-[11px] text-cyan-600 dark:text-cyan-400 font-medium">
              <div class="flex items-center gap-1.5">
                <ArrowLeftRight class="w-3.5 h-3.5 shrink-0 animate-pulse" />
                <span>Vuốt ngang xem Mua/Bán &bull; Bấm vào mã xem chi tiết</span>
              </div>
              <span class="text-[10px] bg-cyan-500/10 px-2 py-0.5 rounded font-mono font-bold border border-cyan-500/20 shrink-0">Cố định Mã CP</span>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs text-theme-text border-separate border-spacing-0 min-w-[840px]">
                <thead>
                  <tr class="bg-theme-subtle text-theme-sub text-[11px] font-bold uppercase tracking-wider select-none">
                    <!-- Column: Mã CP (Cố định sticky left-0, siêu gọn nhẹ) -->
                    <th 
                      @click="toggleSort('ticker')" 
                      class="py-3 px-2 sm:px-3 text-center sm:text-left cursor-pointer transition select-none group sticky left-0 z-30 border-b border-r border-theme-border shadow-[3px_0_6px_-2px_rgba(0,0,0,0.08)] dark:shadow-[3px_0_6px_-2px_rgba(0,0,0,0.35)] w-16 sm:w-20 min-w-[65px] sm:min-w-[75px] max-w-[80px]"
                      :class="isSorted('ticker') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'bg-theme-subtle text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                      title="Bấm để sắp xếp theo Mã cổ phiếu"
                    >
                      <div class="flex items-center justify-center sm:justify-start gap-1">
                        <span>Mã CP</span>
                        <component :is="getSortIcon('ticker')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('ticker')" />
                      </div>
                    </th>

                    <!-- Group: Khối Ngoại -->
                    <th 
                      @click="toggleSort('foreign_buy_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('foreign_buy_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Ngoại Mua</span>
                        <component :is="getSortIcon('foreign_buy_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('foreign_buy_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('foreign_buy_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <th 
                      @click="toggleSort('foreign_sell_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('foreign_sell_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Ngoại Bán</span>
                        <component :is="getSortIcon('foreign_sell_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('foreign_sell_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('foreign_sell_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <th 
                      @click="toggleSort('foreign_net_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('foreign_net_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Ngoại Mua Ròng</span>
                        <component :is="getSortIcon('foreign_net_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('foreign_net_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('foreign_net_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <!-- Group: Trong Nước -->
                    <th 
                      @click="toggleSort('domestic_buy_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('domestic_buy_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Nội Mua</span>
                        <component :is="getSortIcon('domestic_buy_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('domestic_buy_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('domestic_buy_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <th 
                      @click="toggleSort('domestic_sell_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('domestic_sell_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Nội Bán</span>
                        <component :is="getSortIcon('domestic_sell_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('domestic_sell_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('domestic_sell_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <th 
                      @click="toggleSort('domestic_net_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('domestic_net_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Nội Mua Ròng</span>
                        <component :is="getSortIcon('domestic_net_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('domestic_net_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('domestic_net_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <!-- Group: Tổng Khối Lượng -->
                    <th 
                      @click="toggleSort('total_volume_million')" 
                      class="py-3 px-3 text-right cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('total_volume_million') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-end gap-1">
                        <span>Tổng KL</span>
                        <component :is="getSortIcon('total_volume_million')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('total_volume_million')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('total_volume_million') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(Tr CP)</span>
                    </th>

                    <th 
                      @click="toggleSort('foreign_ratio_pct')" 
                      class="py-3 px-3 text-center cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                      :class="isSorted('foreign_ratio_pct') ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500 hover:bg-theme-subtle-2'"
                    >
                      <div class="flex items-center justify-center gap-1">
                        <span>Tỷ Trọng Ngoại</span>
                        <component :is="getSortIcon('foreign_ratio_pct')" class="w-3.5 h-3.5 shrink-0" :class="getSortIconClass('foreign_ratio_pct')" />
                      </div>
                      <span class="text-[9px] font-normal lowercase block" :class="isSorted('foreign_ratio_pct') ? 'text-cyan-600 dark:text-cyan-400 font-semibold' : 'text-theme-muted'">(%)</span>
                    </th>

                    <th class="py-3 px-3 text-center text-theme-sub border-b border-theme-border bg-theme-subtle">Tín Hiệu Dòng Tiền</th>
                  </tr>
                </thead>

                <tbody class="font-mono">
                  <tr 
                    v-for="s in displayedStocks" 
                    :key="s.ticker"
                    class="hover:bg-theme-card-hover transition duration-150 cursor-pointer group"
                    @click="$emit('select-stock', s)"
                    title="Bấm để xem biểu đồ TradingView & phân tích chi tiết mã này"
                  >
                    <!-- Ticker (Cố định sticky left-0, tối ưu siêu gọn nhẹ - chỉ hiển thị Mã CP) -->
                    <td 
                      class="py-2.5 sm:py-3 px-2 sm:px-3 text-center sm:text-left sticky left-0 z-20 border-b border-r border-theme-border shadow-[3px_0_6px_-2px_rgba(0,0,0,0.08)] dark:shadow-[3px_0_6px_-2px_rgba(0,0,0,0.35)] transition-colors w-16 sm:w-20 min-w-[65px] sm:min-w-[75px] max-w-[80px]"
                      :class="isSorted('ticker') ? 'bg-cyan-500/[0.08] dark:bg-cyan-500/[0.12]' : 'bg-theme-card group-hover:bg-theme-card-hover'"
                    >
                      <div class="flex items-center justify-center sm:justify-start">
                        <span class="font-bold text-xs sm:text-sm font-mono text-cyan-600 dark:text-cyan-400 group-hover:underline">
                          {{ s.ticker }}
                        </span>
                      </div>
                    </td>

                    <!-- Foreign Buy (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right font-semibold text-emerald-600 dark:text-emerald-400 border-b border-theme-border"
                      :class="isSorted('foreign_buy_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      {{ formatNumber(s.foreign_buy_million) }}
                    </td>

                    <!-- Foreign Sell (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right font-semibold text-rose-500 dark:text-rose-400 border-b border-theme-border"
                      :class="isSorted('foreign_sell_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      {{ formatNumber(s.foreign_sell_million) }}
                    </td>

                    <!-- Foreign Net (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right border-b border-theme-border"
                      :class="isSorted('foreign_net_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      <span 
                        class="px-2 py-0.5 rounded font-bold text-xs inline-block"
                        :class="s.foreign_net_million > 0 
                          ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                          : s.foreign_net_million < 0 
                            ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30' 
                            : 'text-theme-muted'"
                      >
                        {{ s.foreign_net_million > 0 ? '+' : '' }}{{ formatNumber(s.foreign_net_million) }}
                      </span>
                    </td>

                    <!-- Domestic Buy (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right text-theme-text border-b border-theme-border"
                      :class="isSorted('domestic_buy_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      {{ formatNumber(s.domestic_buy_million) }}
                    </td>

                    <!-- Domestic Sell (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right text-theme-text border-b border-theme-border"
                      :class="isSorted('domestic_sell_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      {{ formatNumber(s.domestic_sell_million) }}
                    </td>

                    <!-- Domestic Net (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right border-b border-theme-border"
                      :class="isSorted('domestic_net_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      <span 
                        class="px-2 py-0.5 rounded font-bold text-xs inline-block"
                        :class="s.domestic_net_million > 0 
                          ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' 
                          : s.domestic_net_million < 0 
                            ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30' 
                            : 'text-theme-muted'"
                      >
                        {{ s.domestic_net_million > 0 ? '+' : '' }}{{ formatNumber(s.domestic_net_million) }}
                      </span>
                    </td>

                    <!-- Total Volume (Tr CP) -->
                    <td 
                      class="py-3 px-3 text-right font-bold text-theme-text border-b border-theme-border"
                      :class="isSorted('total_volume_million') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      {{ formatNumber(s.total_volume_million) }}
                    </td>

                    <!-- Foreign Ratio (%) -->
                    <td 
                      class="py-3 px-3 text-center border-b border-theme-border"
                      :class="isSorted('foreign_ratio_pct') ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                    >
                      <div class="flex items-center justify-center gap-1.5">
                        <div class="w-12 bg-theme-subtle-2 h-1.5 rounded-full overflow-hidden shrink-0">
                          <div class="bg-cyan-500 h-full rounded-full" :style="{ width: Math.min(s.foreign_ratio_pct * 3, 100) + '%' }"></div>
                        </div>
                        <span class="text-[11px] font-semibold text-theme-sub">{{ s.foreign_ratio_pct }}%</span>
                      </div>
                    </td>

                    <!-- Signal Badge -->
                    <td class="py-3 px-3 text-center border-b border-theme-border">
                      <span 
                        class="px-2 py-0.5 rounded-full text-[10px] font-sans font-bold inline-block border whitespace-nowrap"
                        :class="getSignalBadgeClass(s.signal_type)"
                      >
                        {{ s.signal }}
                      </span>
                    </td>
                  </tr>

                  <!-- Empty Result State -->
                  <tr v-if="displayedStocks.length === 0">
                    <td colspan="10" class="py-12 text-center text-theme-muted font-sans text-xs border-b border-theme-border">
                      Không tìm thấy mã cổ phiếu nào phù hợp với bộ lọc hiện tại.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Explanatory Footnote -->
          <div class="p-4 rounded-2xl bg-theme-subtle border border-theme-border text-xs text-theme-sub space-y-1 font-sans">
            <p class="font-bold text-theme-text flex items-center gap-1.5">
              <Info class="w-4 h-4 text-cyan-500 shrink-0" /> Quy Tắc Tính Toán & Cân Đối Dòng Tiền (Market Flow Balance):
            </p>
            <p class="text-[11px]">
              &bull; <strong>Đơn vị thống kê:</strong> Triệu cổ phiếu (Tr CP) &bull; <strong>Nguyên lý bảo toàn:</strong> Tổng Khối Lượng Khớp Lệnh = Ngoại Mua + Nội Mua = Ngoại Bán + Nội Bán.
            </p>
            <p class="text-[11px]">
              &bull; <strong>Mua/Bán Ròng:</strong> Khối ngoại Mua ròng (+) đồng nghĩa Nhà đầu tư trong nước Bán ròng (-) và ngược lại. Tín hiệu giúp nhà đầu tư nhận diện cổ phiếu nào đang được dòng tiền tổ chức quốc tế gom giữ hay rút vốn.
            </p>
          </div>
        </template>

      </div>

      <!-- ==================== MODAL FOOTER ==================== -->
      <div class="px-4 sm:px-6 py-3 border-t border-theme-border bg-theme-subtle flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div class="text-theme-muted text-[11px] font-mono text-center sm:text-left">
          <span>Tổng số mã VN30: <strong>{{ allStocksCount }}</strong> cổ phiếu</span>
          <span class="mx-2">•</span>
          <span>Hiển thị: <strong>{{ displayedStocks.length }}</strong> mã</span>
        </div>

        <button 
          @click="$emit('close')"
          class="w-auto px-7 py-2 rounded-full bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 font-semibold transition text-xs shadow-sm hover:shadow active:scale-95 flex items-center justify-center gap-1.5 border border-theme-border"
        >
          <X class="w-3.5 h-3.5 text-slate-400" />
          <span>Đóng Cửa Sổ</span>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { 
  X, ArrowLeftRight, Globe, Users, Layers, Zap, 
  Calendar, Clock, Search, ArrowUp, ArrowDown, ArrowUpDown, 
  Flame, BarChart3, Info 
} from 'lucide-vue-next'
import { fetchMarketTradingFlow } from '../api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'select-stock'])

const selectedPeriod = ref('today')
const flowData = ref(null)
const isLoading = ref(false)
const searchQuery = ref('')
const activeFilter = ref('ALL') // 'ALL' | 'FOREIGN_BUY' | 'FOREIGN_SELL' | 'DOMESTIC_BUY'

// Sorting state
const sortColumn = ref('total_volume_million')
const sortOrder = ref('desc')

async function loadFlow(period) {
  isLoading.value = true
  try {
    const res = await fetchMarketTradingFlow(period)
    if (res && res.status === 'success') {
      flowData.value = res
    }
  } catch (err) {
    console.error('Lỗi khi tải dòng tiền VN30:', err)
  } finally {
    isLoading.value = false
  }
}

function switchPeriod(period) {
  if (selectedPeriod.value === period) return
  selectedPeriod.value = period
  loadFlow(period)
}

// Counts for filter pills
const allStocksCount = computed(() => flowData.value?.stocks?.length || 0)
const countForeignBuy = computed(() => (flowData.value?.stocks || []).filter(s => s.foreign_net_million > 0).length)
const countForeignSell = computed(() => (flowData.value?.stocks || []).filter(s => s.foreign_net_million < 0).length)
const countDomesticBuy = computed(() => (flowData.value?.stocks || []).filter(s => s.domestic_net_million > 0).length)

// Filter and sort stocks
const displayedStocks = computed(() => {
  let list = flowData.value?.stocks || []

  // 1. Search Query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toUpperCase()
    list = list.filter(s => 
      s.ticker.toUpperCase().includes(q) || 
      (s.company_name && s.company_name.toUpperCase().includes(q))
    )
  }

  // 2. Filter Pills
  if (activeFilter.value === 'FOREIGN_BUY') {
    list = list.filter(s => s.foreign_net_million > 0)
  } else if (activeFilter.value === 'FOREIGN_SELL') {
    list = list.filter(s => s.foreign_net_million < 0)
  } else if (activeFilter.value === 'DOMESTIC_BUY') {
    list = list.filter(s => s.domestic_net_million > 0)
  }

  // 3. Sorting
  const col = sortColumn.value
  const order = sortOrder.value
  return [...list].sort((a, b) => {
    let valA = a[col] ?? 0
    let valB = b[col] ?? 0

    if (typeof valA === 'string') {
      return order === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA)
    }

    return order === 'asc' ? (valA - valB) : (valB - valA)
  })
})

function toggleSort(col) {
  if (sortColumn.value === col) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = col
    sortOrder.value = 'desc'
  }
}

function isSorted(col) {
  return sortColumn.value === col
}

function getSortIcon(col) {
  if (sortColumn.value !== col) return ArrowUpDown
  return sortOrder.value === 'asc' ? ArrowUp : ArrowDown
}

function getSortIconClass(col) {
  if (sortColumn.value === col) {
    return 'text-cyan-600 dark:text-cyan-400 stroke-[2.5]'
  }
  return 'text-theme-muted/40 group-hover:text-cyan-500 transition'
}

function getSignalBadgeClass(type) {
  switch (type) {
    case 'foreign_heavy_buy':
      return 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
    case 'foreign_buy':
      return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20'
    case 'foreign_heavy_sell':
      return 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30'
    case 'foreign_sell':
      return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20'
    default:
      return 'bg-theme-subtle text-theme-muted border-theme-border'
  }
}

function formatNumber(val) {
  if (val === undefined || val === null || isNaN(val)) return '0.00'
  return Number(val).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Watch isOpen to auto fetch when opened
watch(() => props.isOpen, (newVal) => {
  if (newVal && !flowData.value) {
    loadFlow(selectedPeriod.value)
  }
})

function handleKeydown(e) {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  if (props.isOpen) {
    loadFlow(selectedPeriod.value)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
