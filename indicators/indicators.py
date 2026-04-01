"""
技术指标模块
提供常用的股票技术指标计算
"""

import pandas as pd
import numpy as np
from typing import Optional, Union


# ==================== 移动平均线 ====================

def MA(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """简单移动平均线 (Simple Moving Average)"""
    return df[column].rolling(window=period).mean()


def EMA(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """指数移动平均线 (Exponential Moving Average)"""
    return df[column].ewm(span=period, adjust=False).mean()


def SMA(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """简单移动平均线（同MA）"""
    return MA(df, period, column)


def WMA(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.Series:
    """加权移动平均线 (Weighted Moving Average)"""
    weights = np.arange(1, period + 1)
    return df[column].rolling(period).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )


# ==================== MACD ====================

def MACD(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    column: str = 'close'
) -> pd.DataFrame:
    """
    MACD 指标
    Returns: DataFrame with 'macd', 'signal', 'histogram'
    """
    ema_fast = EMA(df, fast, column)
    ema_slow = EMA(df, slow, column)

    macd_line = ema_fast - ema_slow
    signal_line = EMA(pd.DataFrame({'close': macd_line}), signal, 'close')
    histogram = macd_line - signal_line

    return pd.DataFrame({
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    })


# ==================== RSI ====================

def RSI(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
    """相对强弱指标 (Relative Strength Index)"""
    delta = df[column].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # 使用EMA方式计算后续值
    for i in range(period, len(df)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # 当 avg_loss 为 0 且 avg_gain > 0 时，RSI 设为 100
    rsi = rsi.where(~(avg_loss == 0), 100.0)

    return rsi


# ==================== KDJ ====================

def KDJ(
    df: pd.DataFrame,
    n: int = 9,
    m1: int = 3,
    m2: int = 3
) -> pd.DataFrame:
    """
    KDJ 随机指标
    Returns: DataFrame with 'k', 'd', 'j'
    """
    low_n = df['low'].rolling(window=n).min()
    high_n = df['high'].rolling(window=n).max()

    # 处理分母为 0 的情况（当最高价等于最低价时）
    denominator = (high_n - low_n).replace(0, np.nan)
    rsv = (df['close'] - low_n) / denominator * 100
    rsv = rsv.fillna(50)

    k = rsv.ewm(com=m1-1, adjust=False).mean()
    d = k.ewm(com=m2-1, adjust=False).mean()
    j = 3 * k - 2 * d

    return pd.DataFrame({'k': k, 'd': d, 'j': j})


# ==================== 布林带 ====================

def BOLL(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
    column: str = 'close'
) -> pd.DataFrame:
    """
    布林带 (Bollinger Bands)
    Returns: DataFrame with 'upper', 'middle', 'lower'
    """
    middle = MA(df, period, column)
    std = df[column].rolling(window=period).std()

    upper = middle + std_dev * std
    lower = middle - std_dev * std

    return pd.DataFrame({
        'upper': upper,
        'middle': middle,
        'lower': lower
    })


# ==================== OBV ====================

def OBV(df: pd.DataFrame) -> pd.Series:
    """能量潮指标 (On Balance Volume)"""
    obv = pd.Series(index=df.index, dtype=float)
    obv.iloc[0] = df['volume'].iloc[0]

    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]

    return obv


# ==================== ATR ====================

def ATR(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """平均真实波幅 (Average True Range)"""
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    return true_range.rolling(window=period).mean()


# ==================== ADX ====================

def ADX(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """平均趋向指数 (Average Directional Index)"""
    high_diff = df['high'].diff()
    low_diff = -df['low'].diff()

    plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
    minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)

    atr = ATR(df, period)

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)

    adx = dx.rolling(window=period).mean()

    return adx


# ==================== 便捷函数 ====================


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清理 DataFrame 中的 NaN 和 Inf 值

    将 NaN 和 Inf/-Inf 替换为 None，便于 JSON 序列化

    Args:
        df: 需要清理的 DataFrame

    Returns:
        清理后的 DataFrame
    """
    # 替换 inf 和 -inf 为 NaN，然后替换为 None
    df_clean = df.replace([float('inf'), float('-inf'), np.nan], None)
    return df_clean


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    为数据添加所有常用技术指标
    返回添加了指标的DataFrame副本
    """
    result = df.copy()

    # 移动平均线
    result['ma5'] = MA(df, 5)
    result['ma10'] = MA(df, 10)
    result['ma20'] = MA(df, 20)
    result['ma60'] = MA(df, 60)

    result['ema12'] = EMA(df, 12)
    result['ema26'] = EMA(df, 26)

    # MACD
    macd = MACD(df)
    result['macd'] = macd['macd']
    result['macd_signal'] = macd['signal']
    result['macd_hist'] = macd['histogram']

    # RSI
    result['rsi'] = RSI(df, 14)

    # KDJ
    kdj = KDJ(df)
    result['kdj_k'] = kdj['k']
    result['kdj_d'] = kdj['d']
    result['kdj_j'] = kdj['j']

    # 布林带
    boll = BOLL(df)
    result['boll_upper'] = boll['upper']
    result['boll_middle'] = boll['middle']
    result['boll_lower'] = boll['lower']

    # 其他指标
    result['obv'] = OBV(df)
    result['atr'] = ATR(df, 14)
    result['adx'] = ADX(df, 14)

    return result


if __name__ == '__main__':
    # 测试
    from data.fetcher import StockData

    sd = StockData()
    df = sd.get_a_stock('600519', '2024-01-01', '2024-12-31')

    print("原始数据:")
    print(df.head())

    print("\n添加技术指标:")
    df_with_indicators = add_indicators(df)
    print(df_with_indicators[['close', 'ma20', 'rsi', 'kdj_k', 'boll_upper']].tail())
