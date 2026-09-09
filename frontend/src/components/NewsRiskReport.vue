<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Header -->
    <div class="p-6 rounded-3xl bg-gradient-to-r from-amber-500/10 via-theme-subtle to-rose-500/10 border border-theme-border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-amber-500/10 text-amber-500 border border-amber-500/30 flex items-center gap-1">
            <ShieldAlert class="w-3.5 h-3.5" /> BÁO CÁO RỦI RO
          </span>
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
            24/7 REAL-TIME
          </span>
          <h2 class="text-xl font-bold text-theme-text">Báo Cáo Đánh Giá Rủi Ro Tin Tức Vĩ Mô</h2>
        </div>
        <p class="text-xs text-theme-sub mt-1">
          Mô hình lượng hóa mức độ rủi ro từ các sự kiện chính trị, lạm phát và dòng vốn toàn cầu lên danh mục đầu tư.
        </p>
      </div>

      <div class="text-xs font-mono text-theme-sub">
        Cập nhật: <strong class="text-theme-text">{{ reportData?.last_updated || '--' }}</strong>
      </div>
    </div>

    <!-- Overall Risk Gauge & Executive Summary -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Risk Index Meter -->
      <div class="p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm flex flex-col justify-between items-center text-center">
        <span class="text-xs uppercase font-bold text-theme-muted tracking-wider">CHỈ SỐ RỦI RO TIN TỨC VĨ MÔ</span>
        
        <div class="my-6 relative flex items-center justify-center">
          <!-- Circular Meter Indicator -->
          <div class="w-36 h-36 rounded-full border-8 border-theme-subtle-2 flex flex-col items-center justify-center relative shadow-inner">
            <span class="text-4xl font-extrabold font-mono text-amber-500">{{ reportData?.market_risk_index || 58 }}</span>
            <span class="text-[11px] text-theme-muted font-mono">/ 100 ĐIỂM</span>
          </div>
        </div>

        <div class="space-y-1">
          <span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30">
            {{ reportData?.risk_status || 'TRUNG BÌNH - THẬN TRỌNG' }}
          </span>
          <p class="text-[11px] text-theme-muted mt-2">Ngưỡng rủi ro hiện tại khuyến nghị duy trì tỷ trọng an toàn</p>
        </div>
      </div>

      <!-- Executive Summary -->
      <div class="lg:col-span-2 p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm flex flex-col justify-between space-y-4">
        <div>
          <div class="flex items-center gap-2 text-theme-text font-bold text-sm">
            <AlertTriangle class="w-4 h-4 text-amber-500" />
            Tóm Tắt Bối Cảnh Thị Trường (Executive Summary)
          </div>
          <p class="text-xs sm:text-sm text-theme-sub leading-relaxed mt-3">
            {{ reportData?.executive_summary }}
          </p>
        </div>

        <!-- Risk Spectrum Bar -->
        <div class="pt-4 border-t border-theme-border space-y-2">
          <div class="flex justify-between text-[11px] font-mono text-theme-muted">
            <span>0: Rất An Toàn</span>
            <span>50: Cân Bằng</span>
            <span>100: Báo Động</span>
          </div>
          <div class="w-full bg-theme-subtle-2 h-2.5 rounded-full overflow-hidden flex">
            <div class="bg-emerald-500 h-full" style="width: 35%" title="Vùng An Toàn"></div>
            <div class="bg-amber-500 h-full" style="width: 35%" title="Vùng Thận Trọng"></div>
            <div class="bg-rose-500 h-full" style="width: 30%" title="Vùng Báo Động"></div>
          </div>
        </div>
      </div>

    </div>

    <!-- 4 Asset Impact Cards Matrix -->
    <div class="space-y-3">
      <h3 class="text-base font-bold text-theme-text flex items-center gap-2">
        <Layers class="w-4 h-4 text-cyan-500" />
        Ma Trận Đánh Giá Tác Động Lên Từng Loại Tài Sản
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="(matrix, idx) in reportData?.asset_impact_matrix" 
          :key="idx"
          class="p-5 rounded-2xl bg-theme-card border border-theme-border shadow-sm space-y-3 flex flex-col justify-between"
        >
          <div>
            <div class="flex items-center justify-between pb-2 border-b border-theme-border">
              <h4 class="font-bold text-sm text-theme-text">{{ matrix.asset_name }}</h4>
              <span 
                class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="matrix.impact_level === 'Cao' ? 'bg-rose-500/10 text-rose-500 border border-rose-500/30' : 'bg-amber-500/10 text-amber-500 border border-amber-500/30'"
              >
                Rủi ro: {{ matrix.impact_level }}
              </span>
            </div>

            <div class="mt-3 space-y-2 text-xs">
              <div>
                <span class="text-theme-muted font-medium">Xu hướng dự báo:</span>
                <span class="font-semibold text-cyan-600 dark:text-cyan-400 ml-1.5">{{ matrix.trend_bias }}</span>
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
            <p class="text-theme-sub">{{ matrix.recommendation }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Actionable Hedging Strategies (Phòng Vệ Rủi Ro) -->
    <div class="p-6 rounded-3xl bg-theme-card border border-theme-border shadow-sm space-y-4">
      <h3 class="text-base font-bold text-theme-text flex items-center gap-2">
        <ShieldCheck class="w-4 h-4 text-emerald-500" />
        Chiến Lược Quản Trị Rủi Ro & Phòng Vệ Danh Mục (Hedging Strategy)
      </h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="(strategy, s_idx) in reportData?.actionable_hedging_strategies" 
          :key="s_idx"
          class="p-4 rounded-2xl bg-theme-subtle border border-theme-border text-xs space-y-1.5"
        >
          <div class="font-bold text-sm text-theme-text flex items-center gap-2">
            <span class="w-5 h-5 rounded-full bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 flex items-center justify-center font-mono text-xs">
              {{ s_idx + 1 }}
            </span>
            {{ strategy.title }}
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
import { ShieldAlert, AlertTriangle, Layers, ShieldCheck } from 'lucide-vue-next'
import { fetchNewsRiskAssessment } from '../api'

const reportData = ref(null)
const isLoading = ref(true)

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
