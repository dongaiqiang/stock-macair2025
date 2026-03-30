"""
测试数据获取模块
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.fetcher import StockData, get_a_stock, get_us_stock, get_stock


# 标记需要外部数据源连接的测试
pytestmark = pytest.mark.integration


@pytest.fixture
def stock_data():
    """创建 StockData 实例"""
    return StockData()


class TestStockData:
    """测试 StockData 类"""

    def test_init(self, stock_data):
        """测试初始化"""
        assert stock_data is not None

    def test_get_a_stock_returns_dataframe(self, stock_data):
        """测试获取 A 股返回 DataFrame"""
        # 使用较短的日期范围进行测试
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_a_stock('600519', start_date, end_date)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'close' in df.columns
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'volume' in df.columns

    def test_get_a_stock_numeric_columns(self, stock_data):
        """测试获取 A 股返回的数值列类型正确"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_a_stock('600519', start_date, end_date)

        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(df[col])

    def test_get_a_stock_date_index(self, stock_data):
        """测试获取 A 股返回的日期索引正确"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_a_stock('600519', start_date, end_date)

        assert isinstance(df.index, pd.DatetimeIndex)

    def test_get_us_stock_returns_dataframe(self, stock_data):
        """测试获取美股返回 DataFrame"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_us_stock('AAPL', start_date, end_date)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_stock_auto_detect_a_stock(self, stock_data):
        """测试自动识别 A 股"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_stock('600519', start_date, end_date, market='auto')

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_stock_auto_detect_us_stock(self, stock_data):
        """测试自动识别美股"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_stock('AAPL', start_date, end_date, market='auto')

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_invalid_market_type(self, stock_data):
        """测试无效市场类型抛出异常"""
        with pytest.raises(ValueError):
            stock_data.get_stock('INVALID', '2024-01-01', '2024-12-31', market='invalid_market')


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_get_a_stock_function(self):
        """测试 get_a_stock 便捷函数"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = get_a_stock('600519', start_date, end_date)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_us_stock_function(self):
        """测试 get_us_stock 便捷函数"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = get_us_stock('AAPL', start_date, end_date)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_get_stock_function(self):
        """测试 get_stock 便捷函数"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = get_stock('600519', start_date, end_date)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestDataQuality:
    """测试数据质量"""

    def test_no_negative_prices(self, stock_data):
        """测试没有负价格"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_a_stock('600519', start_date, end_date)

        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            assert (df[col] >= 0).all(), f"Found negative values in {col}"

    def test_high_low_consistency(self, stock_data):
        """测试最高价不低于最低价"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_a_stock('600519', start_date, end_date)

        assert (df['high'] >= df['low']).all(), "Found high < low"

    def test_volume_non_negative(self, stock_data):
        """测试成交量非负"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        df = stock_data.get_a_stock('600519', start_date, end_date)

        assert (df['volume'] >= 0).all(), "Found negative volume"
