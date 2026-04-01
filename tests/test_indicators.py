"""
测试技术指标模块
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.indicators import (
    MA, EMA, MACD, RSI, KDJ, BOLL, OBV, ATR, ADX, add_indicators, clean_data
)


@pytest.fixture
def sample_df():
    """创建示例数据用于测试"""
    np.random.seed(42)
    n = 100
    dates = pd.date_range('2024-01-01', periods=n, freq='D')

    # 生成合理的股票价格数据
    close = 100 + np.cumsum(np.random.randn(n) * 2)
    high = close + np.abs(np.random.randn(n))
    low = close - np.abs(np.random.randn(n))
    open_price = close + np.random.randn(n)
    volume = np.random.randint(1000, 10000, n)

    df = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    df = df.set_index('date')

    # 确保 high >= close >= low
    df['high'] = df[['high', 'close', 'open']].max(axis=1)
    df['low'] = df[['low', 'close', 'open']].min(axis=1)

    return df


class TestMA:
    """测试移动平均线"""

    def test_ma_length(self, sample_df):
        """测试 MA 返回长度正确"""
        result = MA(sample_df, period=20)
        assert len(result) == len(sample_df)

    def test_ma_values_not_nan_after_period(self, sample_df):
        """测试 MA 在预热期后不为 NaN"""
        result = MA(sample_df, period=20)
        # 前 19 个值应该是 NaN（因为窗口是 20）
        assert result.iloc[:19].isna().all()
        # 第 20 个值开始不应该为 NaN
        assert not pd.isna(result.iloc[19])

    def test_ema_length(self, sample_df):
        """测试 EMA 返回长度正确"""
        result = EMA(sample_df, period=20)
        assert len(result) == len(sample_df)


class TestMACD:
    """测试 MACD 指标"""

    def test_macd_columns(self, sample_df):
        """测试 MACD 返回正确的列"""
        result = MACD(sample_df)
        assert 'macd' in result.columns
        assert 'signal' in result.columns
        assert 'histogram' in result.columns

    def test_macd_length(self, sample_df):
        """测试 MACD 返回长度正确"""
        result = MACD(sample_df)
        assert len(result) == len(sample_df)


class TestRSI:
    """测试 RSI 指标"""

    def test_rsi_range(self, sample_df):
        """测试 RSI 值在 0-100 范围内"""
        result = RSI(sample_df, period=14)
        # 跳过前 14 个 NaN 值
        valid_values = result.dropna()
        assert (valid_values >= 0).all()
        assert (valid_values <= 100).all()

    def test_rsi_no_inf(self, sample_df):
        """测试 RSI 不产生 Inf 值"""
        result = RSI(sample_df, period=14)
        assert not np.isinf(result).any()

    def test_rsi_length(self, sample_df):
        """测试 RSI 返回长度正确"""
        result = RSI(sample_df, period=14)
        assert len(result) == len(sample_df)


class TestKDJ:
    """测试 KDJ 指标"""

    def test_kdj_columns(self, sample_df):
        """测试 KDJ 返回正确的列"""
        result = KDJ(sample_df)
        assert 'k' in result.columns
        assert 'd' in result.columns
        assert 'j' in result.columns

    def test_kdj_no_nan_from_division_by_zero(self, sample_df):
        """测试 KDJ 在最高价等于最低价时不产生 NaN"""
        # 创建一个特殊情况的数据框
        special_df = pd.DataFrame({
            'high': [100, 100, 100, 100, 100],
            'low': [100, 100, 100, 100, 100],
            'close': [100, 100, 100, 100, 100]
        })
        result = KDJ(special_df)
        # 不应该有 NaN 值（因为用 fillna(50) 处理了）
        assert not result.isna().any().any()

    def test_kdj_length(self, sample_df):
        """测试 KDJ 返回长度正确"""
        result = KDJ(sample_df)
        assert len(result) == len(sample_df)


class TestBOLL:
    """测试布林带指标"""

    def test_boll_columns(self, sample_df):
        """测试布林带返回正确的列"""
        result = BOLL(sample_df)
        assert 'upper' in result.columns
        assert 'middle' in result.columns
        assert 'lower' in result.columns

    def test_boll_order(self, sample_df):
        """测试布林带上下轨关系正确"""
        result = BOLL(sample_df)
        valid_mask = result.notna().all(axis=1)
        if valid_mask.any():
            valid_data = result[valid_mask]
            assert (valid_data['upper'] >= valid_data['middle']).all()
            assert (valid_data['middle'] >= valid_data['lower']).all()


class TestOBV:
    """测试 OBV 指标"""

    def test_obv_length(self, sample_df):
        """测试 OBV 返回长度正确"""
        result = OBV(sample_df)
        assert len(result) == len(sample_df)

    def test_obv_no_nan(self, sample_df):
        """测试 OBV 不产生 NaN"""
        result = OBV(sample_df)
        assert not result.isna().any()


class TestATR:
    """测试 ATR 指标"""

    def test_atr_length(self, sample_df):
        """测试 ATR 返回长度正确"""
        result = ATR(sample_df, period=14)
        assert len(result) == len(sample_df)

    def test_atr_positive(self, sample_df):
        """测试 ATR 值为正"""
        result = ATR(sample_df, period=14)
        valid_values = result.dropna()
        assert (valid_values >= 0).all()


class TestADX:
    """测试 ADX 指标"""

    def test_adx_length(self, sample_df):
        """测试 ADX 返回长度正确"""
        result = ADX(sample_df, period=14)
        assert len(result) == len(sample_df)

    def test_adx_no_inf(self, sample_df):
        """测试 ADX 不产生 Inf 值"""
        result = ADX(sample_df, period=14)
        assert not np.isinf(result).any()


class TestAddIndicators:
    """测试批量添加指标"""

    def test_add_indicators_columns(self, sample_df):
        """测试添加指标后包含所有必需的列"""
        result = add_indicators(sample_df)
        expected_cols = [
            'ma5', 'ma10', 'ma20', 'ma60',
            'ema12', 'ema26',
            'macd', 'macd_signal', 'macd_hist',
            'rsi',
            'kdj_k', 'kdj_d', 'kdj_j',
            'boll_upper', 'boll_middle', 'boll_lower',
            'obv', 'atr', 'adx'
        ]
        for col in expected_cols:
            assert col in result.columns

    def test_add_indicators_original_data_preserved(self, sample_df):
        """测试添加指标后原始数据保留"""
        result = add_indicators(sample_df)
        assert 'open' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'close' in result.columns
        assert 'volume' in result.columns


class TestCleanData:
    """测试数据清理函数"""

    def test_clean_data_removes_inf(self):
        """测试清理函数移除 Inf 值"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, float('inf'), 4.0],
            'b': [1.0, float('-inf'), 3.0, 4.0]
        })
        result = clean_data(df)
        # clean_data 将 inf 转换为 None
        # 检查是否没有 inf 值（使用 applymap 检查每个元素）
        for col in result.columns:
            for val in result[col]:
                assert not (isinstance(val, float) and np.isinf(val))

    def test_clean_data_removes_nan(self):
        """测试清理函数移除 NaN 值"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, np.nan, 4.0],
            'b': [1.0, np.nan, 3.0, 4.0]
        })
        result = clean_data(df)
        # clean_data 将 NaN 转换为 None
        # 检查是否没有 NaN 值
        for col in result.columns:
            for val in result[col]:
                assert not (isinstance(val, float) and np.isnan(val))
