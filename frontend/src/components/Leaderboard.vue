<template>
  <section class="space-y-4">
    <!-- Toolbar: Filter Tabs & Search Bar -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4 bg-theme-card p-3 sm:p-4 rounded-2xl border border-theme-border shadow-sm transition-colors duration-200">
      
      <!-- Filter Tabs -->
      <div class="flex flex-wrap gap-1.5 sm:gap-2">
        <button 
          @click="setFilter('ALL')" 
          class="px-2.5 sm:px-3.5 py-1.5 rounded-xl text-[11px] sm:text-xs font-bold transition"
          :class="activeFilter === 'ALL' ? 'bg-cyan-500 text-slate-950 shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
        >
          Tất cả ({{ stocks.length }})
        </button>
        <button 
          @click="setFilter('BUY')" 
          class="px-2.5 sm:px-3.5 py-1.5 rounded-xl text-[11px] sm:text-xs font-semibold transition"
          :class="activeFilter === 'BUY' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
        >
          Tín hiệu MUA
        </button>
        <button 
          @click="setFilter('HOLD')" 
          class="px-2.5 sm:px-3.5 py-1.5 rounded-xl text-[11px] sm:text-xs font-semibold transition"
          :class="activeFilter === 'HOLD' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
        >
          Nắm giữ / Chờ
        </button>
        <button 
          @click="setFilter('SELL')" 
          class="px-2.5 sm:px-3.5 py-1.5 rounded-xl text-[11px] sm:text-xs font-semibold transition"
          :class="activeFilter === 'SELL' ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm' : 'bg-theme-subtle text-theme-sub hover:bg-theme-subtle-2 hover:text-theme-text'"
        >
          Cảnh báo BÁN
        </button>
      </div>

      <!-- Search Input -->
      <div class="relative w-full md:w-80">
        <Search class="w-4 h-4 text-theme-muted absolute left-3 top-1/2 -translate-y-1/2" />
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Tìm theo mã (FPT, HPG)..." 
          class="w-full pl-9 pr-4 py-2 bg-theme-subtle border border-theme-border rounded-xl text-xs text-theme-text placeholder-theme-muted focus:outline-none focus:border-cyan-500 transition font-mono shadow-inner"
        />
      </div>
    </div>

    <!-- Leaderboard Table Card -->
    <div class="bg-theme-card rounded-2xl border border-theme-border shadow-sm overflow-hidden backdrop-blur-sm transition-colors duration-200">
      <div class="p-3.5 sm:p-5 border-b border-theme-border flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 sm:gap-2">
        <div>
          <h2 class="text-sm sm:text-base font-bold text-theme-text flex items-center gap-2">
            BẢNG XẾP HẠNG 30 CỔ PHIẾU VN30
          </h2>
          <p class="text-[11px] sm:text-xs text-theme-sub mt-0.5">
            Sắp xếp theo Điểm Định Lượng Đa Nhân Tố & Xác suất Tăng Học Máy (LightGBM)
          </p>
        </div>
        <div class="text-[11px] sm:text-xs font-mono text-theme-sub">
          Hiển thị: <span class="text-theme-text font-bold">{{ filteredStocks.length }}</span> mã
        </div>
      </div>

      <!-- Mobile Scroll Hint -->
      <div class="md:hidden px-3.5 py-2 bg-cyan-500/5 border-b border-theme-border flex items-center justify-between gap-2 text-[11px] text-cyan-600 dark:text-cyan-400 font-medium">
        <div class="flex items-center gap-1.5">
          <ArrowLeftRight class="w-3.5 h-3.5 shrink-0 animate-pulse" />
          <span>Vuốt ngang để xem 11 chỉ số còn lại</span>
        </div>
        <span class="text-[10px] bg-cyan-500/10 px-2 py-0.5 rounded font-mono font-bold border border-cyan-500/20 shrink-0">2 cột cố định</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs min-w-[980px] border-separate border-spacing-0">
          <thead class="bg-theme-subtle text-theme-sub font-semibold text-[11px] uppercase tracking-wider select-none">
            <tr>
              <!-- Cột 1: Hạng (Cố định đứng yên / Sticky) -->
              <th class="py-3.5 px-2 text-center w-12 min-w-[48px] max-w-[48px] text-theme-muted sticky left-0 z-30 bg-theme-subtle border-b border-theme-border">
                Hạng
              </th>

              <!-- Cột 2: Mã CK (Cố định đứng yên / Sticky) -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group w-20 min-w-[76px] max-w-[80px] sticky left-12 z-30 bg-theme-subtle border-b border-r border-theme-border shadow-[3px_0_6px_-2px_rgba(0,0,0,0.08)] dark:shadow-[3px_0_6px_-2px_rgba(0,0,0,0.35)]"
                :class="sortKey === 'ticker' ? 'text-cyan-600 dark:text-cyan-400 font-bold' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('ticker')"
                title="Bấm để sắp xếp theo Mã CK"
              >
                <div class="flex items-center gap-1.5">
                  <span>Mã CK</span>
                  <ArrowUp v-if="sortKey === 'ticker' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'ticker' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột Giá Đóng -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'close' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('close')"
                title="Bấm để sắp xếp theo Giá Đóng Cửa"
              >
                <div class="flex items-center justify-end gap-1.5">
                  <span>Giá Đóng</span>
                  <ArrowUp v-if="sortKey === 'close' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'close' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột Biến Động -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'change_pct' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('change_pct')"
                title="Bấm để sắp xếp theo % Biến Động"
              >
                <div class="flex items-center justify-end gap-1.5">
                  <span>Biến Động</span>
                  <ArrowUp v-if="sortKey === 'change_pct' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'change_pct' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột RSI (14) -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'rsi' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('rsi')"
                title="Bấm để sắp xếp theo RSI (14)"
              >
                <div class="flex items-center justify-center gap-1.5">
                  <span>RSI (14)</span>
                  <ArrowUp v-if="sortKey === 'rsi' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'rsi' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột Vol/MA20 -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'vol_vs_ma20' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('vol_vs_ma20')"
                title="Bấm để sắp xếp theo Tỷ Lệ Vol/MA20"
              >
                <div class="flex items-center justify-center gap-1.5">
                  <span>Vol/MA20</span>
                  <ArrowUp v-if="sortKey === 'vol_vs_ma20' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'vol_vs_ma20' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột Dự Báo AI (T+3) -->
              <th 
                class="py-3.5 px-4 cursor-pointer transition select-none group min-w-[190px] border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'ml_prob_up' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('ml_prob_up')"
                title="Dự báo xác suất giá tăng sau 3 phiên (T+3) do AI tính toán. Dưới 50% là xác suất thấp (khả năng giảm chiếm ưu thế)"
              >
                <div class="flex items-center justify-center gap-1.5">
                  <span>Dự Báo AI (T+3)</span>
                  <ArrowUp v-if="sortKey === 'ml_prob_up' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'ml_prob_up' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột Điểm Tổng Hợp Quant (100) -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group min-w-[150px] border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'total_score' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('total_score')"
                title="Điểm định lượng đa nhân tố tổng hợp từ Xu hướng, Động lượng, Dòng tiền & AI (0-100) - Quyết định trực tiếp khuyến nghị Mua/Bán"
              >
                <div class="flex items-center justify-center gap-1.5">
                  <span>Điểm Tổng Hợp (100)</span>
                  <ArrowUp v-if="sortKey === 'total_score' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'total_score' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>
              
              <!-- Cột Khuyến Nghị Đầu Tư -->
              <th 
                class="py-3.5 px-4 cursor-pointer transition select-none group whitespace-nowrap min-w-[160px] border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'signal' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('signal')"
                title="Khuyến nghị đầu tư Mua/Bán được kết luận từ Điểm Tổng Hợp & Dự báo AI"
              >
                <div class="flex items-center justify-center gap-1.5">
                  <span>Khuyến Nghị Đầu Tư</span>
                  <ArrowUp v-if="sortKey === 'signal' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'signal' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>
              
              <!-- Cột Vùng Mua -->
              <th class="py-3.5 px-3 text-center whitespace-nowrap min-w-[110px] text-theme-sub border-b border-theme-border bg-theme-subtle">Vùng Mua</th>

              <!-- Cột Dừng Lỗ -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group whitespace-nowrap border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'stoploss' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('stoploss')"
                title="Bấm để sắp xếp theo Mức Cắt Lỗ"
              >
                <div class="flex items-center justify-end gap-1.5">
                  <span>Dừng Lỗ</span>
                  <ArrowUp v-if="sortKey === 'stoploss' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'stoploss' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <!-- Cột Mục Tiêu 1 -->
              <th 
                class="py-3.5 px-3 cursor-pointer transition select-none group whitespace-nowrap border-b border-theme-border bg-theme-subtle"
                :class="sortKey === 'target_1' ? 'text-cyan-600 dark:text-cyan-400 font-bold bg-cyan-500/10 dark:bg-cyan-500/20' : 'text-theme-sub hover:text-cyan-500'"
                @click="sortBy('target_1')"
                title="Bấm để sắp xếp theo Mức Giá Mục Tiêu 1"
              >
                <div class="flex items-center justify-end gap-1.5">
                  <span>Mục Tiêu 1</span>
                  <ArrowUp v-if="sortKey === 'target_1' && sortOrder === 'asc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowDown v-else-if="sortKey === 'target_1' && sortOrder === 'desc'" class="w-3.5 h-3.5 text-cyan-600 dark:text-cyan-400 stroke-[2.5]" />
                  <ArrowUpDown v-else class="w-3 h-3 text-theme-muted/40 group-hover:text-cyan-500 transition" />
                </div>
              </th>

              <th class="py-3.5 px-3 text-center w-14 text-theme-sub border-b border-theme-border bg-theme-subtle">Biểu Đồ</th>
            </tr>
          </thead>
          <tbody class="font-mono">
            <tr 
              v-for="(s, idx) in filteredStocks" 
              :key="s.ticker"
              @click="$emit('select-stock', s)"
              class="hover:bg-theme-card-hover transition duration-150 cursor-pointer group"
            >
              <!-- Cột 1: Hạng (Cố định đứng yên / Sticky) -->
              <td class="py-3.5 px-2 text-center text-theme-muted text-[11px] font-semibold sticky left-0 z-20 bg-theme-card group-hover:bg-theme-card-hover border-b border-theme-border transition-colors w-12 min-w-[48px] max-w-[48px]">
                {{ idx + 1 }}
              </td>
              
              <!-- Cột 2: Mã CK (Cố định đứng yên / Sticky) -->
              <td 
                class="py-3.5 px-3 font-bold text-theme-text group-hover:text-cyan-500 transition text-sm sticky left-12 z-20 bg-theme-card group-hover:bg-theme-card-hover border-b border-r border-theme-border shadow-[3px_0_6px_-2px_rgba(0,0,0,0.08)] dark:shadow-[3px_0_6px_-2px_rgba(0,0,0,0.35)] transition-colors w-20 min-w-[76px] max-w-[80px]"
                :class="sortKey === 'ticker' ? 'text-cyan-500 font-extrabold' : ''"
              >
                <span>{{ s.ticker }}</span>
              </td>
              
              <td 
                class="py-3.5 px-3 text-right font-semibold text-theme-text border-b border-theme-border"
                :class="sortKey === 'close' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
              >
                {{ formatPrice(s.close) }}
              </td>
              
              <td 
                class="py-3.5 px-3 text-right font-semibold whitespace-nowrap border-b border-theme-border"
                :class="[
                  s.change_pct >= 0 ? 'text-emerald-500 dark:text-emerald-400' : 'text-rose-500 dark:text-rose-400',
                  sortKey === 'change_pct' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''
                ]"
              >
                {{ s.change_pct >= 0 ? '+' : '' }}{{ s.change_pct?.toFixed(2) }}%
              </td>
              
              <td 
                class="py-3.5 px-3 text-center text-theme-text border-b border-theme-border"
                :class="sortKey === 'rsi' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
              >
                {{ s.rsi?.toFixed(1) || '--' }}
              </td>
              
              <td 
                class="py-3.5 px-3 text-center whitespace-nowrap border-b border-theme-border"
                :class="[
                  s.vol_vs_ma20 >= 1.3 ? 'text-amber-500 dark:text-amber-400 font-bold' : 'text-theme-text',
                  sortKey === 'vol_vs_ma20' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''
                ]"
              >
                {{ s.vol_vs_ma20?.toFixed(2) || '--' }}x
              </td>
              
              <td 
                class="py-3.5 px-4 whitespace-nowrap border-b border-theme-border"
                :class="sortKey === 'ml_prob_up' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
                :title="`Khả năng tăng giá T+3: ${s.ml_prob_up}% | Khả năng giảm/đi ngang: ${(100 - s.ml_prob_up).toFixed(1)}%`"
              >
                <div class="flex items-center justify-center gap-2">
                  <span 
                    class="w-12 text-right font-semibold text-xs"
                    :class="s.ml_prob_up >= 55 ? 'text-emerald-500 dark:text-emerald-400' : (s.ml_prob_up >= 50 ? 'text-cyan-500 dark:text-cyan-400' : (s.ml_prob_up >= 40 ? 'text-amber-500 dark:text-amber-400' : 'text-rose-500 dark:text-rose-400'))"
                  >
                    {{ s.ml_prob_up }}%
                  </span>
                  <div class="w-16 bg-theme-subtle-2 rounded-full h-1.5 overflow-hidden">
                    <div 
                      class="h-full transition-all duration-300 rounded-full"
                      :class="s.ml_prob_up >= 55 ? 'bg-emerald-500' : (s.ml_prob_up >= 50 ? 'bg-cyan-500' : (s.ml_prob_up >= 40 ? 'bg-amber-500' : 'bg-rose-500'))"
                      :style="{ width: Math.min(Math.max(s.ml_prob_up, 10), 100) + '%' }"
                    ></div>
                  </div>
                  <span 
                    class="text-[9px] font-bold px-1.5 py-0.5 rounded shrink-0"
                    :class="s.ml_prob_up >= 50 ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'"
                  >
                    {{ s.ml_prob_up >= 50 ? 'Khả quan' : 'Thấp' }}
                  </span>
                </div>
              </td>
              
              <td 
                class="py-3.5 px-3 text-center whitespace-nowrap border-b border-theme-border"
                :class="sortKey === 'total_score' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
              >
                <span 
                  class="px-2.5 py-0.5 rounded-lg text-xs"
                  :class="getScoreBadge(s.total_score)"
                >
                  {{ s.total_score }}
                </span>
              </td>
              
              <!-- Khuyến Nghị Cell: whitespace-nowrap để TUYỆT ĐỐI không bao giờ bị xuống dòng -->
              <td 
                class="py-3.5 px-4 text-center whitespace-nowrap border-b border-theme-border"
                :class="sortKey === 'signal' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
              >
                <span v-html="getSignalBadge(s.signal)"></span>
              </td>
              
              <td class="py-3.5 px-3 text-center text-theme-sub text-[11px] whitespace-nowrap border-b border-theme-border">
                {{ s.entry_range || '--' }}
              </td>
              
              <td 
                class="py-3.5 px-3 text-right text-rose-500 dark:text-rose-400 font-semibold whitespace-nowrap border-b border-theme-border"
                :class="sortKey === 'stoploss' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
              >
                {{ formatPrice(s.stoploss) }}
              </td>
              
              <td 
                class="py-3.5 px-3 text-right text-emerald-500 dark:text-emerald-400 font-semibold whitespace-nowrap border-b border-theme-border"
                :class="sortKey === 'target_1' ? 'bg-cyan-500/[0.04] dark:bg-cyan-500/[0.07]' : ''"
              >
                {{ formatPrice(s.target_1) }}
              </td>
              
              <td class="py-3.5 px-3 text-center border-b border-theme-border">
                <button 
                  @click.stop="$emit('select-stock', s)"
                  class="p-1.5 rounded-lg bg-theme-subtle group-hover:bg-cyan-500 group-hover:text-slate-950 text-theme-muted transition shadow-sm"
                  title="Xem biểu đồ & chi tiết AI"
                >
                  <CandlestickChart class="w-3.5 h-3.5" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, CandlestickChart, ArrowUp, ArrowDown, ArrowUpDown, ArrowLeftRight } from 'lucide-vue-next'

const props = defineProps({
  stocks: {
    type: Array,
    default: () => []
  }
})

defineEmits(['select-stock'])

const activeFilter = ref('ALL')
const searchQuery = ref('')
const sortKey = ref('total_score')
const sortOrder = ref('desc')

function setFilter(f) {
  activeFilter.value = f
}

function sortBy(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    // Mã CK mặc định từ A-Z (asc), các chỉ số định lượng/giá mặc định từ cao xuống thấp (desc)
    sortOrder.value = key === 'ticker' ? 'asc' : 'desc'
  }
}

function getSignalRank(signal) {
  const s = (signal || '').toUpperCase()
  if (s.includes('MUA MẠNH')) return 6
  if (s.includes('MUA')) return 5
  if (s.includes('QUAN SÁT')) return 4
  if (s.includes('THEO DÕI')) return 3
  if (s.includes('BÁN MẠNH')) return 1
  if (s.includes('BÁN')) return 2
  return 3.5
}

const filteredStocks = computed(() => {
  let list = [...props.stocks]

  // Filter tab
  if (activeFilter.value === 'BUY') {
    list = list.filter(s => s.signal?.includes('MUA'))
  } else if (activeFilter.value === 'HOLD') {
    list = list.filter(s => s.signal?.includes('QUAN SÁT') || s.signal?.includes('NẮM GIỮ') || s.signal?.includes('THEO DÕI'))
  } else if (activeFilter.value === 'SELL') {
    list = list.filter(s => s.signal?.includes('BÁN'))
  }

  // Search input
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toUpperCase()
    list = list.filter(s => s.ticker?.includes(q))
  }

  // Sort
  list.sort((a, b) => {
    if (sortKey.value === 'signal') {
      const rankA = getSignalRank(a.signal)
      const rankB = getSignalRank(b.signal)
      if (rankA !== rankB) {
        return sortOrder.value === 'asc' ? rankA - rankB : rankB - rankA
      }
      const scoreA = a.total_score ?? 0
      const scoreB = b.total_score ?? 0
      return sortOrder.value === 'asc' ? scoreA - scoreB : scoreB - scoreA
    }

    const va = a[sortKey.value] ?? 0
    const vb = b[sortKey.value] ?? 0
    if (typeof va === 'string') {
      return sortOrder.value === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
    }
    return sortOrder.value === 'asc' ? va - vb : vb - va
  })

  return list
})

function formatPrice(val) {
  if (!val) return '--'
  return Number(val).toLocaleString('vi-VN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getScoreBadge(score) {
  if (score >= 75) return 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/40'
  if (score >= 60) return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-300 font-bold'
  if (score <= 35) return 'bg-rose-500/20 text-rose-600 dark:text-rose-400 font-bold border border-rose-500/40'
  if (score <= 45) return 'bg-rose-500/10 text-rose-600 dark:text-rose-300 font-semibold'
  return 'bg-theme-subtle text-theme-sub border border-theme-border'
}

function getSignalBadge(signal) {
  if (!signal) return ''
  // Dùng whitespace-nowrap để KHÔNG BAO GIỜ bị xuống dòng
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
