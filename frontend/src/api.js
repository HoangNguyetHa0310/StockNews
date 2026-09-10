// Khi deploy All-in-One (chạy cùng origin trên Cloud), để rỗng '' để tự động gọi relative path.
// Khi dev bằng Vite hoặc deploy tách biệt, ưu tiên VITE_API_BASE_URL hoặc fallback về localhost:8000.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')

/**
 * Hàm gọi API trung tâm với cơ chế Chống Cache (Cache-Busting):
 * - Tự động đính kèm timestamp `_t` để URL luôn luôn là duy nhất.
 * - Gửi kèm các HTTP Headers: 'Cache-Control: no-cache, no-store, must-revalidate', 'Pragma: no-cache'.
 * - Hoạt động giống hệt phím tắt 'Ctrl + Shift + R' trên trình duyệt,
 *   đảm bảo mỗi lần người dùng mở lại tab hoặc bật màn hình đều lấy dữ liệu mới nhất 100%.
 */
async function apiFetch(endpoint, options = {}) {
  const separator = endpoint.includes('?') ? '&' : '?'
  const url = `${API_BASE}${endpoint}${separator}_t=${Date.now()}`

  const headers = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    ...(options.headers || {})
  }

  const response = await fetch(url, {
    ...options,
    headers,
    cache: 'no-store'
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return await response.json()
}

export async function fetchMarketOverview() {
  try {
    const json = await apiFetch('/api/market/overview')
    return json.data
  } catch (err) {
    console.error('Lỗi lấy tổng quan thị trường:', err)
    return null
  }
}

export async function fetchVN30Leaderboard(params = {}) {
  try {
    const query = new URLSearchParams()
    if (params.signal) query.append('signal', params.signal)
    if (params.search) query.append('search', params.search)
    if (params.sort_by) query.append('sort_by', params.sort_by)
    if (params.order) query.append('order', params.order)

    const qStr = query.toString()
    const json = await apiFetch(`/api/vn30/leaderboard${qStr ? '?' + qStr : ''}`)
    return json.data || []
  } catch (err) {
    console.error('Lỗi lấy bảng xếp hạng VN30:', err)
    return []
  }
}

export async function fetchStockAnalysis(ticker) {
  try {
    const json = await apiFetch(`/api/stocks/${ticker}/analysis`)
    return json.data
  } catch (err) {
    console.error(`Lỗi lấy phân tích mã ${ticker}:`, err)
    return null
  }
}

export async function fetchStockCandles(ticker, limit = 120) {
  try {
    const json = await apiFetch(`/api/stocks/${ticker}/candles?limit=${limit}`)
    return json.data || []
  } catch (err) {
    console.error(`Lỗi lấy nến mã ${ticker}:`, err)
    return []
  }
}

export async function triggerMarketRefresh() {
  try {
    return await apiFetch('/api/market/refresh', { method: 'POST' })
  } catch (err) {
    console.error('Lỗi kích hoạt refresh:', err)
    return { status: 'error', message: err.message }
  }
}

export async function fetchNewsFeed(params = {}) {
  try {
    const query = new URLSearchParams()
    if (params.region) query.append('region', params.region)
    if (params.asset) query.append('asset', params.asset)
    if (params.search) query.append('search', params.search)

    const qStr = query.toString()
    const json = await apiFetch(`/api/news/feed${qStr ? '?' + qStr : ''}`)
    return json.data || []
  } catch (err) {
    console.error('Lỗi lấy tin tức thị trường:', err)
    return []
  }
}

export async function fetchNewsRiskAssessment() {
  try {
    const json = await apiFetch('/api/news/risk-assessment')
    return json.data || null
  } catch (err) {
    console.error('Lỗi lấy báo cáo rủi ro tin tức:', err)
    return null
  }
}

export async function fetchMarketRecommendationReport() {
  try {
    const json = await apiFetch('/api/market/recommendation-report')
    return json.data || null
  } catch (err) {
    console.error('Lỗi lấy báo cáo khuyến nghị & lý do VN30:', err)
    return null
  }
}

export async function fetchMarketTradingFlow(period = 'today') {
  try {
    return await apiFetch(`/api/market/trading-flow?period=${period}`)
  } catch (err) {
    console.error(`Lỗi lấy dòng tiền giao dịch VN30 (${period}):`, err)
    return null
  }
}

export async function fetchHotMovers() {
  try {
    const json = await apiFetch('/api/news/hot-movers')
    return json.data || []
  } catch (err) {
    console.error('Lỗi lấy danh sách cổ phiếu tăng nóng:', err)
    return []
  }
}
