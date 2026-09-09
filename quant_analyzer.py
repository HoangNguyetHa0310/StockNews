# -*- coding: utf-8 -*-
"""
Module Phân tích Định lượng Đa nhân tố (Quantitative Multi-Factor Analyzer)
Tính toán điểm số kỹ thuật, đánh giá dòng tiền, dự đoán xác suất,
xác định vùng giá hỗ trợ, kháng cự, mục tiêu (Target) và cắt lỗ (Stoploss).
"""
import numpy as np
import pandas as pd
from config import QUANT_WEIGHTS, SIGNAL_THRESHOLDS
from vn30_insights import generate_ticker_reasoning


class QuantAnalyzer:
    def __init__(self, weights: dict = None):
        self.weights = weights or QUANT_WEIGHTS

    def calculate_trend_score(self, row: pd.Series) -> float:
        """Chấm điểm xu hướng (0 - 100)."""
        score = 0.0
        close = row.get('close', 0)
        
        # Vị thế so với các đường MA
        if close > row.get('sma_20', 0):
            score += 25.0
        if close > row.get('sma_50', 0):
            score += 25.0
        if close > row.get('sma_200', 0):
            score += 20.0
            
        # Tương quan EMA ngắn hạn
        if row.get('is_ema9_gt_ema21', 0) == 1:
            score += 15.0
            
        # Độ dốc SMA20
        if row.get('sma_20_slope', 0) > 0:
            score += 15.0
            
        return min(max(score, 0.0), 100.0)

    def calculate_momentum_score(self, row: pd.Series) -> float:
        """Chấm điểm động lượng (0 - 100)."""
        score = 0.0
        rsi = row.get('rsi', 50)
        
        # RSI phân tích
        if 48 <= rsi <= 65:
            score += 35.0  # Vùng tăng trưởng mạnh, chưa quá mua
        elif 35 <= rsi < 48:
            score += 20.0  # Vùng phục hồi
        elif rsi < 35:
            score += 25.0  # Vùng quá bán, cơ hội bắt đáy kỹ thuật
        elif rsi > 70:
            score += 10.0  # Quá mua, rủi ro điều chỉnh cao
        else:
            score += 15.0

        # MACD
        if row.get('macd', 0) > row.get('macd_signal', 0):
            score += 30.0
        if row.get('macd_hist', 0) > 0 and row.get('macd_hist_diff', 0) > 0:
            score += 20.0

        # Stochastic
        if row.get('stoch_k', 0) > row.get('stoch_d', 0) and row.get('stoch_k', 0) < 80:
            score += 15.0

        return min(max(score, 0.0), 100.0)

    def calculate_money_flow_score(self, row: pd.Series) -> float:
        """Chấm điểm dòng tiền & khối lượng (0 - 100)."""
        score = 0.0
        vol_ratio = row.get('volume_ratio', 1.0)
        
        # Đột biến khối lượng dòng tiền
        if 1.2 <= vol_ratio <= 3.0:
            score += 40.0  # Vol tăng đẹp, xác nhận dòng tiền vào
        elif vol_ratio > 3.0:
            score += 25.0  # Vol quá lớn có thể là cao trào mua/bán (climax)
        elif 0.9 <= vol_ratio < 1.2:
            score += 20.0  # Khối lượng duy trì mức trung bình
        else:
            score += 10.0  # Thanh khoản thấp cạn kiệt

        # OBV xu hướng gom hàng
        if row.get('obv_trend', 0) == 1:
            score += 35.0

        # MFI (Chỉ số dòng tiền)
        mfi = row.get('mfi', 50)
        if 45 <= mfi <= 75:
            score += 25.0
        elif mfi < 30:
            score += 20.0  # Dòng tiền cạn kiệt sắp đảo chiều
        else:
            score += 10.0

        return min(max(score, 0.0), 100.0)

    def determine_signal(self, total_score: float, ml_prob_up: float) -> str:
        """Xác định khuyến nghị giao dịch chuẩn mực và hài hòa giữa Kỹ thuật & AI."""
        # Tín hiệu Mua
        if total_score >= SIGNAL_THRESHOLDS["STRONG_BUY"] and ml_prob_up >= 0.52:
            return "MUA MẠNH"
        elif total_score >= SIGNAL_THRESHOLDS["BUY"] and ml_prob_up >= 0.45:
            return "MUA"
        elif total_score >= SIGNAL_THRESHOLDS["BUY"] and ml_prob_up < 0.45:
            # Điểm kỹ thuật tốt nhưng AI thận trọng -> Khuyên theo dõi, chưa vội mua/bán
            return "THEO DÕI (Chờ AI đồng thuận)"

        # Tín hiệu Bán
        if total_score <= 30 or (total_score < 40 and ml_prob_up < 0.35):
            return "BÁN MẠNH"
        elif total_score < SIGNAL_THRESHOLDS["HOLD"] or (total_score < 50 and ml_prob_up < 0.40):
            return "BÁN / HẠ TỶ TRỌNG"

        # Trạng thái trung lập
        return "QUAN SÁT / NẮM GIỮ"

    def calculate_price_levels(self, df: pd.DataFrame) -> dict:
        """
        Tính toán vùng hỗ trợ, kháng cự, mục tiêu lợi nhuận (Target) và điểm dừng lỗ (Stoploss).
        """
        if df is None or len(df) < 20:
            return {}

        last_row = df.iloc[-1]
        close = last_row['close']
        atr = last_row.get('atr', close * 0.02)
        if np.isnan(atr) or atr <= 0:
            atr = close * 0.02

        # Hỗ trợ: đáy 10 phiên gần nhất hoặc SMA20
        recent_10 = df.tail(10)
        recent_20 = df.tail(20)
        
        support_1 = min(recent_10['low'].min(), last_row.get('sma_20', close * 0.97))
        support_2 = min(recent_20['low'].min(), last_row.get('sma_50', close * 0.94))
        
        # Kháng cự: đỉnh 10 phiên hoặc Bollinger Upper
        resistance_1 = max(recent_10['high'].max(), last_row.get('bb_upper', close * 1.03))
        resistance_2 = max(recent_20['high'].max(), close * 1.07)

        # Mức dừng lỗ khuyến nghị: dưới đáy gần nhất hoặc cách 1.8 ATR
        stoploss = round(max(close - (1.8 * atr), support_1 * 0.985), 2)
        
        # Mức chốt lời khuyến nghị theo Risk/Reward >= 1:1.8
        risk = close - stoploss
        if risk <= 0:
            risk = close * 0.03
            stoploss = round(close - risk, 2)
            
        target_1 = round(close + (1.5 * risk), 2)
        target_2 = round(close + (2.5 * risk), 2)

        entry_low = round(min(close * 0.99, support_1 * 1.005), 2)
        entry_high = round(max(close * 1.005, close), 2)

        return {
            "close": round(close, 2),
            "entry_range": f"{entry_low} - {entry_high}",
            "support_1": round(support_1, 2),
            "support_2": round(support_2, 2),
            "resistance_1": round(resistance_1, 2),
            "resistance_2": round(resistance_2, 2),
            "stoploss": stoploss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_reward_ratio": round((target_1 - close) / (risk + 1e-6), 2)
        }

    def analyze_ticker(self, ticker: str, df: pd.DataFrame, ml_result: dict) -> dict:
        """Phân tích toàn diện 1 mã cổ phiếu và tổng hợp tín hiệu."""
        if df is None or len(df) < 20:
            return {}

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Điểm từng thành phần
        trend_score = self.calculate_trend_score(last_row)
        momentum_score = self.calculate_momentum_score(last_row)
        flow_score = self.calculate_money_flow_score(last_row)
        
        ml_prob_up = ml_result.get("prob_up", 0.5)
        ml_score = ml_prob_up * 100.0

        # Tổng hợp điểm trọng số
        total_score = (
            trend_score * self.weights["trend"] +
            momentum_score * self.weights["momentum"] +
            flow_score * self.weights["money_flow"] +
            ml_score * self.weights["ml_prediction"]
        )
        total_score = round(total_score, 1)

        signal = self.determine_signal(total_score, ml_prob_up)
        levels = self.calculate_price_levels(df)

        change_pct = ((last_row['close'] / prev_row['close']) - 1.0) * 100.0

        base_res = {
            "ticker": ticker.upper(),
            "date": last_row['time'].strftime("%Y-%m-%d") if hasattr(last_row['time'], 'strftime') else str(last_row['time']),
            "close": round(last_row['close'], 2),
            "change_pct": round(change_pct, 2),
            "volume": int(last_row['volume']),
            "vol_vs_ma20": round(last_row.get('volume_ratio', 1.0), 2),
            "rsi": round(last_row.get('rsi', 50), 1),
            "macd_status": "Bullish" if last_row.get('macd', 0) > last_row.get('macd_signal', 0) else "Bearish",
            "trend_score": round(trend_score, 1),
            "momentum_score": round(momentum_score, 1),
            "flow_score": round(flow_score, 1),
            "ml_prob_up": round(ml_prob_up * 100.0, 1),
            "ml_confidence": ml_result.get("confidence", "Trung tính"),
            "total_score": total_score,
            "signal": signal,
            **levels
        }

        # Sinh lý do khuyến nghị, tin tức tác động và động lực giá
        insights = generate_ticker_reasoning(ticker, base_res)
        base_res.update(insights)

        return base_res

    def analyze_market_regime(self, vnindex_df: pd.DataFrame, stock_analyses: list[dict]) -> dict:
        """
        Đánh giá bối cảnh và độ rộng thị trường chung (Market Breadth)
        cùng tỷ lệ phần trăm phân bổ khuyến nghị Mua / Chờ / Bán.
        """
        if vnindex_df is None or vnindex_df.empty:
            return {}

        last_vn = vnindex_df.iloc[-1]
        prev_vn = vnindex_df.iloc[-2]
        vn_close = last_vn['close']
        vn_change = ((vn_close / prev_vn['close']) - 1.0) * 100.0

        total_stocks = len(stock_analyses)
        if total_stocks == 0:
            return {}

        buy_tickers = [s['ticker'] for s in stock_analyses if "MUA" in s.get('signal', '')]
        sell_tickers = [s['ticker'] for s in stock_analyses if "BÁN" in s.get('signal', '')]
        hold_tickers = [s['ticker'] for s in stock_analyses if s['ticker'] not in buy_tickers and s['ticker'] not in sell_tickers]

        buy_count = len(buy_tickers)
        sell_count = len(sell_tickers)
        hold_count = len(hold_tickers)

        pct_buy = round((buy_count / total_stocks) * 100.0, 1)
        pct_hold = round((hold_count / total_stocks) * 100.0, 1)
        pct_sell = round((sell_count / total_stocks) * 100.0, 1)

        if pct_buy >= 60:
            sentiment = "Rất Tích Cực (Uptrend mạnh)"
            regime_explanation = (
                f"Thị trường đang trong xu hướng tăng điểm mạnh mẽ với {pct_buy}% cổ phiếu VN30 phát tín hiệu MUA. "
                "Dòng tiền lan tỏa đều ở các nhóm ngành dẫn dắt (Ngân hàng, Thép, Bán lẻ), lực cầu chủ động chiếm ưu thế áp đảo."
            )
        elif pct_buy >= 40:
            sentiment = "Tích Cực (Có sự phân hóa)"
            regime_explanation = (
                f"Thị trường trong trạng thái tích cực có chọn lọc ({pct_buy}% MUA, {pct_hold}% CHỜ). "
                "Cơ hội tập trung ở các cổ phiếu đầu ngành có kết quả kinh doanh đột phá và dòng tiền tổ chức bảo trợ."
            )
        elif pct_buy >= 20:
            sentiment = "Trung Tính / Giằng Co"
            regime_explanation = (
                f"Chỉ số giằng co quanh vùng cân bằng với {pct_hold}% cổ phiếu duy trì trạng thái tích lũy. "
                "Bên mua và bên bán duy trì thế phòng thủ, thanh khoản thăm dò."
            )
        else:
            if hold_count >= total_stocks * 0.5:
                sentiment = "Thận Trọng / Tích Lũy Chờ Xu Hướng Mới"
                regime_explanation = (
                    f"Thị trường đang trong giai đoạn tích lũy thận trọng: Chiếm đa số là {pct_hold}% ({hold_count}/{total_stocks} mã) "
                    f"ở trạng thái QUAN SÁT / NẮM GIỮ (THEO DÕI), {pct_sell}% ({sell_count} mã) phát tín hiệu BÁN / HẠ TỶ TRỌNG "
                    f"và {pct_buy}% ({buy_count} mã) tín hiệu MUA. Dòng tiền lớn đang chờ đợi các tín hiệu xác nhận từ vĩ mô và dòng tiền ETF ngoại."
                )
            else:
                sentiment = "Thận Trọng / Áp Lực Bán Chi Phối"
                regime_explanation = (
                    f"Áp lực điều chỉnh ngắn hạn gia tăng với {pct_sell}% cổ phiếu VN30 chạm ngưỡng BÁN / HẠ TỶ TRỌNG. "
                    "Chiến lược ưu tiên là quản trị rủi ro danh mục, hạ đòn bẩy margin và giữ tỷ trọng tiền mặt an toàn."
                )

        return {
            "vnindex_close": round(vn_close, 2),
            "vnindex_change_pct": round(vn_change, 2),
            "vnindex_volume": int(last_vn['volume']),
            "market_sentiment": sentiment,
            "regime_explanation": regime_explanation,
            "total_stocks_analyzed": total_stocks,
            "buy_count": buy_count,
            "hold_count": hold_count,
            "sell_count": sell_count,
            "pct_buy": pct_buy,
            "pct_hold": pct_hold,
            "pct_sell": pct_sell,
            "buy_tickers": buy_tickers,
            "hold_tickers": hold_tickers,
            "sell_tickers": sell_tickers
        }
