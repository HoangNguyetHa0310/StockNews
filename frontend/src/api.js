// Khi deploy All-in-One (chạy cùng origin trên Cloud), để rỗng '' để tự động gọi relative path.
// Khi dev bằng Vite hoặc deploy tách biệt, ưu tiên VITE_API_BASE_URL hoặc fallback về localhost:8000.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')

export async function fetchMarketOverview() {
  try {
    const res = await fetch(`${API_BASE}/api/market/overview`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
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

    const url = `${API_BASE}/api/vn30/leaderboard${query.toString() ? '?' + query.toString() : ''}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data || []
  } catch (err) {
    console.error('Lỗi lấy bảng xếp hạng VN30:', err)
    return []
  }
}

export async function fetchStockAnalysis(ticker) {
  try {
    const res = await fetch(`${API_BASE}/api/stocks/${ticker}/analysis`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data
  } catch (err) {
    console.error(`Lỗi lấy phân tích mã ${ticker}:`, err)
    return null
  }
}

export async function fetchStockCandles(ticker, limit = 120) {
  try {
    const res = await fetch(`${API_BASE}/api/stocks/${ticker}/candles?limit=${limit}`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data || []
  } catch (err) {
    console.error(`Lỗi lấy nến mã ${ticker}:`, err)
    return []
  }
}

export async function triggerMarketRefresh() {
  try {
    const res = await fetch(`${API_BASE}/api/market/refresh`, { method: 'POST' })
    return await res.json()
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

    const url = `${API_BASE}/api/news/feed${query.toString() ? '?' + query.toString() : ''}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data || []
  } catch (err) {
    console.error('Lỗi lấy tin tức thị trường:', err)
    return []
  }
}

export async function fetchNewsRiskAssessment() {
  try {
    const res = await fetch(`${API_BASE}/api/news/risk-assessment`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data || null
  } catch (err) {
    console.error('Lỗi lấy báo cáo rủi ro tin tức:', err)
    return null
  }
}

export async function fetchMarketRecommendationReport() {
  try {
    const res = await fetch(`${API_BASE}/api/market/recommendation-report`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data || null
  } catch (err) {
    console.error('Lỗi lấy báo cáo khuyến nghị & lý do VN30:', err)
    return null
  }
}

export async function fetchMarketTradingFlow(period = 'today') {
  try {
    const res = await fetch(`${API_BASE}/api/market/trading-flow?period=${period}`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json || null
  } catch (err) {
    console.error(`Lỗi lấy dòng tiền giao dịch VN30 (${period}):`, err)
    return null
  }
}

export async function fetchHotMovers() {
  try {
    const res = await fetch(`${API_BASE}/api/news/hot-movers`)
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
    const json = await res.json()
    return json.data || []
  } catch (err) {
    console.error('Lỗi lấy danh sách cổ phiếu tăng nóng:', err)
    return []
  }
}


