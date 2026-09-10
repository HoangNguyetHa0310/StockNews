<template>
  <div class="space-y-6 animate-fade-in pb-12 md:pb-6">
    <!-- Header -->
    <div class="p-4 sm:p-6 rounded-3xl bg-gradient-to-r from-amber-500/10 via-theme-subtle to-rose-500/10 border border-theme-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex flex-wrap items-center gap-2">
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30 flex items-center gap-1 whitespace-nowrap shrink-0">
            <ShieldAlert class="w-3.5 h-3.5" /> BÁO CÁO RỦI RO
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 whitespace-nowrap shrink-0">
            24/7 REAL-TIME
          </span>
          <h2 class="text-lg sm:text-xl font-bold text-theme-text">Báo Cáo Đánh Giá Rủi Ro & Chiến Lược Đầu Tư</h2>
        </div>
        <p class="text-xs text-theme-sub mt-1">
          Lượng hóa rủi ro từ tin tức vĩ mô, dòng tiền khối ngoại và trạng thái rổ VN30 nhằm đưa ra kịch bản hành động cụ thể cho nhà đầu tư.
        </p>
      </div>

      <div class="text-xs font-mono text-theme-sub whitespace-nowrap shrink-0 flex items-center gap-1.5">
        <Clock class="w-3.5 h-3.5 text-amber-500" />
        <span>Cập nhật: <strong class="text-theme-text">{{ reportData?.last_updated || '--' }}</strong></span>
      </div>
    </div>

    <!-- 1. Overall Risk Gauge & Executive Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Risk Index Meter -->
      <div class="p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm flex flex-col justify-between items-center text-center">
        <span class="text-xs uppercase font-bold text-theme-muted tracking-wider">CHỈ SỐ RỦI RO THỊ TRƯỜNG</span>
        
        <div class="my-5 relative flex items-center justify-center">
          <div 
            class="w-36 h-36 rounded-full border-8 flex flex-col items-center justify-center relative shadow-inner transition-colors duration-300"
            :class="getMeterBorderClass(reportData?.market_risk_index)"
          >
            <span 
              class="text-4xl font-extrabold font-mono transition-colors duration-300"
              :class="getRiskTextColor(reportData?.market_risk_index)"
            >
              {{ reportData?.market_risk_index || 50 }}
            </span>
            <span class="text-[11px] text-theme-muted font-mono">/ 100 ĐIỂM</span>
          </div>
        </div>

        <div class="space-y-1.5">
          <span 
            class="px-3 py-1 rounded-full text-xs font-bold shadow-sm inline-block"
            :class="getRiskBadgeClassFromScore(reportData?.market_risk_index)"
          >
            {{ reportData?.risk_status || 'TRUNG BÌNH - THẬN TRỌNG' }}
          </span>
          <p class="text-[11px] text-theme-muted mt-1">
            Được tính toán động từ biến động VN-INDEX, tỷ lệ Mua/Bán VN30 & dòng tiền
          </p>
        </div>
      </div>

      <!-- Executive Summary & Portfolio Allocation -->
      <div class="lg:col-span-2 p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm flex flex-col justify-between space-y-4">
        <div>
          <div class="flex items-center gap-2 text-theme-text font-bold text-sm">
            <AlertTriangle class="w-4 h-4 text-amber-500" />
            Tóm Tắt Bối Cảnh Thị Trường & Khuyến Nghị Trọng Tâm
          </div>
          <p class="text-xs sm:text-sm text-theme-sub leading-relaxed mt-2.5">
            {{ reportData?.executive_summary }}
          </p>
        </div>

        <!-- Khuyến Nghị Tỷ Trọng Phân Bổ Danh Mục Cụ Thể -->
        <div v-if="reportData?.portfolio_allocation" class="p-4 rounded-2xl bg-theme-subtle border border-theme-border space-y-3">
          <div class="flex items-center justify-between text-xs font-bold">
            <span class="text-theme-text flex items-center gap-1.5">
              <PieChart class="w-4 h-4 text-cyan-500" />
              Khuyến Nghị Phân Bổ Vốn Danh Mục
            </span>
            <span class="text-cyan-600 dark:text-cyan-400 font-mono text-[11px]">
              Tỷ lệ Cổ / Tiền: {{ reportData.portfolio_allocation.stocks_pct }}% / {{ reportData.portfolio_allocation.cash_pct }}%
            </span>
          </div>

          <!-- Progress Bar Tỷ lệ Cổ phiếu vs Tiền mặt -->
          <div class="w-full bg-theme-subtle-2 h-3 rounded-full overflow-hidden flex shadow-inner">
            <div 
              class="bg-gradient-to-r from-cyan-500 to-emerald-500 h-full transition-all duration-500" 
              :style="{ width: `${reportData.portfolio_allocation.stocks_pct}%` }" 
              :title="`Cổ phiếu: ${reportData.portfolio_allocation.stocks_pct}%`"
            ></div>
            <div 
              class="bg-slate-400 dark:bg-slate-600 h-full transition-all duration-500" 
              :style="{ width: `${reportData.portfolio_allocation.cash_pct}%` }" 
              :title="`Tiền mặt dự phòng: ${reportData.portfolio_allocation.cash_pct}%`"
            ></div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-sm bg-cyan-500 shrink-0"></span>
              <span class="text-theme-sub">
                Cổ phiếu mục tiêu: <strong class="text-theme-text">{{ reportData.portfolio_allocation.stocks_pct }}%</strong>
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-sm bg-slate-400 shrink-0"></span>
              <span class="text-theme-sub">
                Tiền mặt chờ cơ hội: <strong class="text-theme-text">{{ reportData.portfolio_allocation.cash_pct }}%</strong>
              </span>
            </div>
          </div>

          <div class="pt-2 border-t border-theme-border text-[11px] text-theme-sub space-y-1">
            <p><strong>Khuyến nghị Margin:</strong> {{ reportData.portfolio_allocation.margin_recommendation }}</p>
            <p><strong>Định hướng:</strong> {{ reportData.portfolio_allocation.strategy_mode }}</p>
          </div>
        </div>

      </div>

    </div>

    <!-- 2. KỊCH BẢN HÀNH ĐỘNG CỤ THỂ CHO CHỈ SỐ VN-INDEX -->
    <div v-if="reportData?.index_scenarios" class="p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-bold text-theme-text flex items-center gap-2">
          <Compass class="w-4 h-4 text-cyan-500" />
          Kịch Bản Hành Động Cụ Thể Cho Chỉ Số VN-INDEX
        </h3>
        <span class="text-[11px] font-mono text-theme-muted hidden sm:inline">Chiến thuật giải ngân & phòng vệ</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="(scen, s_idx) in reportData.index_scenarios" 
          :key="s_idx"
          class="p-5 rounded-2xl border transition duration-200 flex flex-col justify-between space-y-3 shadow-sm"
          :class="scen.badge_color === 'emerald' 
            ? 'bg-emerald-500/[0.04] border-emerald-500/30' 
            : 'bg-rose-500/[0.04] border-rose-500/30'"
        >
          <div class="space-y-2">
            <div class="flex items-start justify-between gap-2">
              <h4 class="font-bold text-sm text-theme-text leading-snug">
                {{ scen.name }}
              </h4>
              <span 
                class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold shrink-0"
                :class="scen.badge_color === 'emerald' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30' : 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'"
              >
                Xác suất: {{ scen.probability }}
              </span>
            </div>

            <div class="text-xs space-y-1.5 pt-1">
              <p class="text-theme-sub">
                <span class="text-theme-muted font-medium">Vùng điểm:</span> 
                <strong class="text-theme-text ml-1">{{ scen.target_range }}</strong>
              </p>
              <p class="text-theme-sub">
                <span class="text-theme-muted font-medium">Tín hiệu kích hoạt:</span> 
                <span class="ml-1">{{ scen.trigger_condition }}</span>
              </p>
            </div>
          </div>

          <!-- Kế hoạch hành động cụ thể -->
          <div class="p-3.5 rounded-xl bg-theme-card border border-theme-border text-xs space-y-1 shadow-inner">
            <span class="font-bold text-cyan-600 dark:text-cyan-400 flex items-center gap-1.5">
              <ArrowRightCircle class="w-3.5 h-3.5" />
              HÀNH ĐỘNG CỤ THỂ:
            </span>
            <p class="text-theme-text leading-relaxed font-medium">
              {{ scen.action_plan }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. BẢNG CHIẾN LƯỢC HÀNH ĐỘNG TỪNG NHÓM NGÀNH VN30 (SECTOR PLAYBOOK) -->
    <div v-if="reportData?.sector_playbook" class="p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
        <h3 class="text-base font-bold text-theme-text flex items-center gap-2">
          <Briefcase class="w-4 h-4 text-emerald-500" />
          Bảng Hành Động Chi Tiết Từng Nhóm Ngành VN30
        </h3>
        <span class="text-xs text-theme-sub font-mono">Định hướng giải ngân theo chu kỳ dòng tiền</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs min-w-[700px] border-separate border-spacing-y-2">
          <thead>
            <tr class="text-[11px] text-theme-muted uppercase tracking-wider font-mono">
              <th class="py-2 px-3">Nhóm Ngành</th>
              <th class="py-2 px-3">Cổ Phiếu Tiêu Biểu</th>
              <th class="py-2 px-3 text-center">Tỷ Trọng</th>
              <th class="py-2 px-3 text-center">Hành Động Khuyến Nghị</th>
              <th class="py-2 px-4">Lý Do Cốt Lõi & Cơ Hội / Rủi Ro</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="(sec, s_idx) in reportData.sector_playbook" 
              :key="s_idx"
              class="bg-theme-subtle hover:bg-theme-subtle-2 transition rounded-xl"
            >
              <td class="py-3 px-3 font-bold text-theme-text rounded-l-xl whitespace-nowrap">
                {{ sec.sector_name }}
              </td>
              <td class="py-3 px-3 font-mono font-semibold text-cyan-600 dark:text-cyan-400 whitespace-nowrap">
                {{ sec.tickers }}
              </td>
              <td class="py-3 px-3 font-mono font-bold text-center text-theme-text whitespace-nowrap">
                {{ sec.allocation_pct }}
              </td>
              <td class="py-3 px-3 text-center whitespace-nowrap">
                <span 
                  class="px-2.5 py-1 rounded-lg text-[10px] font-bold inline-block"
                  :class="getSectorActionClass(sec.action_color)"
                >
                  {{ sec.action }}
                </span>
              </td>
              <td class="py-3 px-4 text-theme-sub text-[11px] leading-relaxed rounded-r-xl min-w-[240px]">
                {{ sec.key_reason }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 4. Ma Trận Đánh Giá Tác Động Lên Từng Loại Tài Sản -->
    <div class="space-y-3">
      <h3 class="text-base font-bold text-theme-text flex items-center gap-2">
        <Layers class="w-4 h-4 text-cyan-500" />
        Ma Trận Tác Động Vĩ Mô Lên Các Loại Tài Sản (Asset Matrix)
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="(matrix, idx) in reportData?.asset_impact_matrix" 
          :key="idx"
          class="p-4 sm:p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm space-y-3 flex flex-col justify-between"
        >
          <div>
            <div class="flex items-start justify-between gap-3 pb-2.5 border-b border-theme-border">
              <h4 class="font-bold text-sm text-theme-text leading-snug min-w-0 flex-1">{{ matrix.asset_name }}</h4>
              <span 
                class="px-2.5 py-1 rounded-lg text-[10px] sm:text-[11px] font-bold whitespace-nowrap shrink-0 leading-none shadow-sm"
                :class="getRiskBadgeClass(matrix)"
              >
                {{ matrix.impact_level }}
              </span>
            </div>

            <div class="mt-3 space-y-2 text-xs">
              <div class="flex flex-wrap items-baseline gap-1.5">
                <span class="text-theme-muted font-medium shrink-0">Xu hướng dự báo:</span>
                <span class="font-semibold text-cyan-600 dark:text-cyan-400 leading-snug">{{ matrix.trend_bias }}</span>
              </div>
              <div>
                <span class="text-theme-muted font-medium">Động lực hỗ trợ:</span>
                <p class="text-theme-sub mt-0.5 leading-relaxed">{{ matrix.key_driver }}</p>
              </div>
              <div>
                <span class="text-theme-muted font-medium">Yếu tố rủi ro chính:</span>
                <p class="text-rose-600 dark:text-rose-400 mt-0.5 leading-relaxed">{{ matrix.risk_factors }}</p>
              </div>
            </div>
          </div>

          <!-- Recommendation Banner -->
          <div class="p-3 rounded-xl bg-theme-subtle border border-theme-border text-xs">
            <span class="font-bold text-theme-text block mb-0.5">Khuyến nghị chiến lược:</span>
            <p class="text-theme-sub leading-relaxed">{{ matrix.recommendation }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. Chiến Lược Quản Trị Rủi Ro & Phòng Vệ Danh Mục (Hedging Strategy) -->
    <div class="p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm space-y-4">
      <h3 class="text-base font-bold text-theme-text flex items-center gap-2">
        <ShieldCheck class="w-4 h-4 text-emerald-500" />
        3 Nguyên Tắc Quản Trị Rủi Ro & Phòng Vệ Danh Mục Sống Còn
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="(strategy, s_idx) in reportData?.actionable_hedging_strategies" 
          :key="s_idx"
          class="p-4 rounded-2xl bg-theme-subtle border border-theme-border text-xs space-y-1.5"
        >
          <div class="font-bold text-sm text-theme-text flex items-center gap-2">
            <span class="w-5 h-5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-mono text-xs font-bold shrink-0">
              {{ s_idx + 1 }}
            </span>
            <span>{{ strategy.title }}</span>
          </div>
          <p class="text-theme-sub leading-relaxed pt-1">
            {{ strategy.desc }}
          </p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  ShieldAlert, 
  AlertTriangle, 
  Layers, 
  ShieldCheck, 
  PieChart, 
  Compass, 
  Briefcase, 
  ArrowRightCircle,
  Clock 
} from 'lucide-vue-next'
import { fetchNewsRiskAssessment } from '../api'

const reportData = ref(null)
const isLoading = ref(true)

function getMeterBorderClass(score) {
  const s = Number(score) || 50
  if (s <= 40) return 'border-emerald-500/30'
  if (s <= 60) return 'border-amber-500/30'
  return 'border-rose-500/30'
}

function getRiskTextColor(score) {
  const s = Number(score) || 50
  if (s <= 40) return 'text-emerald-500'
  if (s <= 60) return 'text-amber-500'
  return 'text-rose-500'
}

function getRiskBadgeClassFromScore(score) {
  const s = Number(score) || 50
  if (s <= 40) return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
  if (s <= 60) return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
  return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
}

function getRiskBadgeClass(matrix) {
  const level = (matrix?.impact_level || '').toLowerCase()
  const color = (matrix?.impact_color || '').toLowerCase()
  if (level.includes('cao') || color === 'rose' || color === 'red') {
    return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
  }
  if (level.includes('trung') || color === 'amber' || color === 'yellow') {
    return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
  }
  return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
}

function getSectorActionClass(color) {
  if (color === 'emerald') return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
  if (color === 'cyan') return 'bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 border border-cyan-500/30'
  if (color === 'amber') return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30'
  if (color === 'indigo') return 'bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-500/30'
  return 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/30'
}

async function loadReport() {
  isLoading.value = true
  const data = await fetchNewsRiskAssessment()
  reportData.value = data
  isLoading.value = false
}

onMounted(() => {
  loadReport()
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
