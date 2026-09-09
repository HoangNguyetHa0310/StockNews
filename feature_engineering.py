# -*- coding: utf-8 -*-
"""
Module xây dựng và tính toán các chỉ báo định lượng (Quantitative Features)
Bao gồm: Xu hướng (Trend), Động lượng (Momentum), Dòng tiền (Money Flow),
Độ biến động (Volatility) và Nhãn mục tiêu Machine Learning (T+3, T+5).
Toàn bộ được tối ưu hóa vector trên Pandas/Numpy không phụ thuộc C library ngoài.
"""
import numpy as np
import pandas as pd
from config import INDICATOR_PARAMS, ML_CONFIG


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Tính chỉ số sức mạnh tương đối RSI theo chuẩn Wilder's Smoothing."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Tính đường MACD, Signal Line và Histogram."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0):
    """Tính dải Bollinger Bands (Middle, Upper, Lower, %B, Bandwidth)."""
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    pct_b = (series - lower) / (upper - lower + 1e-10)
    bandwidth = (upper - lower) / (middle + 1e-10)
    return upper, middle, lower, pct_b, bandwidth


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Tính chỉ báo biên độ dao động thực tế bình quân (ATR)."""
    high = df['high']
    low = df['low']
    prev_close = df['close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    return atr


def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3):
    """Tính dao động Stochastic %K và %D."""
    low_min = df['low'].rolling(window=k_period).min()
    high_max = df['high'].rolling(window=k_period).max()
    k = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
    d = k.rolling(window=d_period).mean()
    return k, d


def calculate_obv(df: pd.DataFrame) -> pd.Series:
    """Tính chỉ báo khối lượng cân bằng (On-Balance Volume - OBV)."""
    direction = np.sign(df['close'].diff())
    direction.iloc[0] = 0
    obv = (direction * df['volume']).cumsum()
    return obv


def calculate_mfi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Tính chỉ báo dòng tiền (Money Flow Index - MFI)."""
    typical_price = (df['high'] + df['low'] + df['close']) / 3.0
    money_flow = typical_price * df['volume']
    
    delta = typical_price.diff()
    pos_flow = np.where(delta > 0, money_flow, 0.0)
    neg_flow = np.where(delta < 0, money_flow, 0.0)
    
    pos_mf = pd.Series(pos_flow, index=df.index).rolling(window=period).sum()
    neg_mf = pd.Series(neg_flow, index=df.index).rolling(window=period).sum()
    
    mfr = pos_mf / (neg_mf + 1e-10)
    mfi = 100 - (100 / (1 + mfr))
    return mfi


def add_technical_features(df: pd.DataFrame, vnindex_df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Tính toán toàn bộ bộ đặc trưng kỹ thuật & động lượng cho một cổ phiếu.
    """
    if df is None or len(df) < 30:
        return df

    out = df.copy()
    close = out['close']
    high = out['high']
    low = out['low']
    vol = out['volume']

    # 1. Các tỷ suất sinh lời (Returns)
    out['return_1d'] = close.pct_change(1)
    out['return_3d'] = close.pct_change(3)
    out['return_5d'] = close.pct_change(5)
    out['return_10d'] = close.pct_change(10)
    out['return_20d'] = close.pct_change(20)

    # 2. Đặc trưng hình nến (Candlestick characteristics)
    candle_range = (high - low).replace(0, 1e-6)
    out['body_to_range'] = (close - out['open']).abs() / candle_range
    out['close_position'] = (close - low) / candle_range

    # 3. Đường trung bình (Moving Averages)
    for p in INDICATOR_PARAMS["sma_periods"]:
        sma = close.rolling(window=p).mean()
        out[f'sma_{p}'] = sma
        out[f'ratio_close_sma_{p}'] = (close / (sma + 1e-10)) - 1.0

    for p in INDICATOR_PARAMS["ema_periods"]:
        out[f'ema_{p}'] = close.ewm(span=p, adjust=False).mean()

    # Độ dốc SMA20 & MA alignments
    out['sma_20_slope'] = (out['sma_20'] - out['sma_20'].shift(5)) / (out['sma_20'].shift(5) + 1e-10)
    out['is_ema9_gt_ema21'] = (out['ema_9'] > out['ema_21']).astype(int)
    out['is_sma20_gt_sma50'] = (out['sma_20'] > out['sma_50']).astype(int)

    # 4. Động lượng (Momentum)
    out['rsi'] = calculate_rsi(close, period=INDICATOR_PARAMS["rsi_period"])
    macd_line, macd_sig, macd_hist = calculate_macd(close, **INDICATOR_PARAMS["macd"])
    out['macd'] = macd_line
    out['macd_signal'] = macd_sig
    out['macd_hist'] = macd_hist
    out['macd_hist_diff'] = macd_hist - macd_hist.shift(1)
    
    stoch_k, stoch_d = calculate_stochastic(out, **INDICATOR_PARAMS["stochastic"])
    out['stoch_k'] = stoch_k
    out['stoch_d'] = stoch_d

    # 5. Độ biến động (Volatility)
    bb_upper, bb_mid, bb_lower, bb_pct_b, bb_width = calculate_bollinger_bands(
        close, **INDICATOR_PARAMS["bollinger"]
    )
    out['bb_upper'] = bb_upper
    out['bb_middle'] = bb_mid
    out['bb_lower'] = bb_lower
    out['bb_pct_b'] = bb_pct_b
    out['bb_width'] = bb_width
    
    out['atr'] = calculate_atr(out, period=INDICATOR_PARAMS["atr_period"])
    out['atr_pct'] = out['atr'] / (close + 1e-10)

    # 6. Dòng tiền & Khối lượng (Volume & Flow)
    vol_sma = vol.rolling(window=INDICATOR_PARAMS["volume_sma"]).mean()
    out['volume_sma20'] = vol_sma
    out['volume_ratio'] = vol / (vol_sma + 1e-10)
    out['is_volume_surge'] = (out['volume_ratio'] > 1.3).astype(int)

    out['obv'] = calculate_obv(out)
    out['obv_ema20'] = out['obv'].ewm(span=20, adjust=False).mean()
    out['obv_trend'] = (out['obv'] > out['obv_ema20']).astype(int)

    out['mfi'] = calculate_mfi(out, period=INDICATOR_PARAMS["mfi_period"])

    # 7. Tương quan với thị trường chung (VN-INDEX Context)
    if vnindex_df is not None and not vnindex_df.empty:
        vn_df = vnindex_df[['time', 'close']].copy()
        vn_df.columns = ['time', 'vnindex_close']
        vn_df['vnindex_ret_1d'] = vn_df['vnindex_close'].pct_change(1)
        vn_df['vnindex_ret_5d'] = vn_df['vnindex_close'].pct_change(5)
        vn_df['vnindex_sma20'] = vn_df['vnindex_close'].rolling(20).mean()
        vn_df['vnindex_trend'] = (vn_df['vnindex_close'] > vn_df['vnindex_sma20']).astype(int)

        out = pd.merge(out, vn_df, on='time', how='left')
        out['rel_strength_5d'] = out['return_5d'] - out['vnindex_ret_5d'].fillna(0)
    else:
        out['vnindex_ret_1d'] = 0.0
        out['vnindex_ret_5d'] = 0.0
        out['vnindex_trend'] = 1
        out['rel_strength_5d'] = 0.0

    # 8. Tạo nhãn tương lai cho bài toán Machine Learning
    horizon = ML_CONFIG["prediction_horizon"]  # mặc định 3 phiên
    thresh = ML_CONFIG["return_threshold"]     # mặc định 1.0%

    # Tỷ suất sinh lời sau T+3 phiên
    out['future_return_t3'] = (close.shift(-3) / close) - 1.0
    out['target_up_t3'] = (out['future_return_t3'] > thresh).astype(int)

    # Tỷ suất sinh lời sau T+5 phiên
    out['future_return_t5'] = (close.shift(-5) / close) - 1.0
    out['target_up_t5'] = (out['future_return_t5'] > thresh).astype(int)

    return out


# Danh sách các feature dạng số dùng làm đầu vào cho Machine Learning
ML_FEATURE_COLUMNS = [
    'return_1d', 'return_3d', 'return_5d', 'return_10d', 'return_20d',
    'body_to_range', 'close_position',
    'ratio_close_sma_10', 'ratio_close_sma_20', 'ratio_close_sma_50', 'ratio_close_sma_200',
    'sma_20_slope', 'is_ema9_gt_ema21', 'is_sma20_gt_sma50',
    'rsi', 'macd_hist', 'macd_hist_diff', 'stoch_k', 'stoch_d',
    'bb_pct_b', 'bb_width', 'atr_pct',
    'volume_ratio', 'is_volume_surge', 'obv_trend', 'mfi',
    'vnindex_ret_1d', 'vnindex_ret_5d', 'vnindex_trend', 'rel_strength_5d'
]
