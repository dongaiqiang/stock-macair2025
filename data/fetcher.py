"""
股票数据获取模块
支持 A股（baostock）和美股（yfinance）
"""

import pandas as pd
import baostock as bs
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Union
from functools import lru_cache


class StockData:
    """统一股票数据获取接口"""

    def __init__(self):
        self._bs_login = False

    def _login_baostock(self):
        """登录 baostock"""
        if not self._bs_login:
            bs.login()
            self._bs_login = True

    def _logout_baostock(self):
        """登出 baostock"""
        if self._bs_login:
            bs.logout()
            self._bs_login = False

    def get_a_stock_minute(self, code: str, start_date: str, end_date: str = None,
                            frequency: int = 5, adjustflag: str = "2") -> pd.DataFrame:
        """
        获取A股分钟级数据

        Args:
            code: 股票代码，如 '600519'
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            frequency: 数据频率，5/15/30/60分钟，默认5分钟
            adjustflag: 复权类型，"1"后复权，"2"前复权，"3"不复权

        Returns:
            DataFrame: 包含 date, time, open, high, low, close, volume
        """
        self._login_baostock()

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # 转换股票代码格式
        if '.' not in code:
            code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"

        # frequency: "5"=5分钟,"15"=15分钟,"30"=30分钟,"60"=60分钟
        freq_map = {5: "5", 15: "15", 30: "30", 60: "60"}
        freq_str = freq_map.get(frequency, "5")

        rs = bs.query_history_k_data_plus(
            code,
            "date,time,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency=freq_str,
            adjustflag=adjustflag
        )

        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())

        df = pd.DataFrame(data_list, columns=rs.fields)

        # 转换数据类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 合并date和time为datetime
        # time格式: 20240102093500000 (YYYYMMDDHHMMSSmmm)
        df['datetime'] = pd.to_datetime(df['date'] + df['time'].str[:8], format='%Y%m%d%H%M%S')
        df = df.set_index('datetime')

        return df

    def get_a_stock(self, code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
        """
        获取A股历史数据

        Args:
            code: 股票代码，如 '600519'（茅台）、'000001'（平安银行）
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'，默认今天

        Returns:
            DataFrame: 包含 date, open, high, low, close, volume, amount
        """
        self._login_baostock()

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # 转换股票代码格式
        if '.' not in code:
            code = f"sh.{code}" if code.startswith('6') else f"sz.{code}"

        rs = bs.query_history_k_data_plus(
            code,
            "date,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag="2"  # 前复权
        )

        data_list = []
        while (rs.error_code == '0') and rs.next():
            data_list.append(rs.get_row_data())

        df = pd.DataFrame(data_list, columns=rs.fields)

        # 转换数据类型
        numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        return df

    def get_us_stock(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取美股历史数据

        Args:
            code: 股票代码，如 'AAPL'、'MSFT'
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'，默认今天

        Returns:
            DataFrame: 包含 Open, High, Low, Close, Volume
        """
        ticker = yf.Ticker(code)

        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        df = ticker.history(start=start_date, end=end_date)

        # 统一列名小写
        df.columns = [col.lower() for col in df.columns]

        return df

    def get_stock(self, code: str, start_date: str, end_date: str = None, market: str = 'auto') -> pd.DataFrame:
        """
        统一获取股票数据，自动识别市场

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            market: 市场类型，'a'/'china'/'us'/'auto'，默认自动识别

        Returns:
            DataFrame: 标准化的股票数据
        """
        if market == 'auto':
            # 自动识别市场
            if code.isdigit() and len(code) == 6:
                market = 'a'
            else:
                market = 'us'

        if market in ('a', 'china'):
            df = self.get_a_stock(code, start_date, end_date)
        elif market == 'us':
            df = self.get_us_stock(code, start_date, end_date)
        else:
            raise ValueError(f"Unsupported market: {market}")

        return df

    def get_realtime(self, code: str, market: str = 'auto') -> dict:
        """
        获取实时行情

        Args:
            code: 股票代码
            market: 市场类型

        Returns:
            dict: 实时行情数据
        """
        if market == 'auto':
            if code.isdigit() and len(code) == 6:
                market = 'a'
            else:
                market = 'us'

        if market == 'us':
            ticker = yf.Ticker(code)
            info = ticker.info
            return {
                'symbol': code,
                'name': info.get('shortName', code),
                'price': info.get('currentPrice'),
                'change': info.get('regularMarketChange'),
                'change_pct': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap'),
            }
        else:
            # A股实时数据需要其他接口
            raise NotImplementedError("A股实时数据暂未支持")

    def __del__(self):
        """析构时登出 baostock"""
        try:
            self._logout_baostock()
        except Exception:
            pass


# 便捷函数
def get_a_stock(code: str, start_date: str, end_date: str = None) -> pd.DataFrame:
    """获取A股数据"""
    return StockData().get_a_stock(code, start_date, end_date)


def get_us_stock(code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """获取美股数据"""
    return StockData().get_us_stock(code, start_date, end_date)


def get_stock(code: str, start_date: str, end_date: str = None, market: str = 'auto') -> pd.DataFrame:
    """统一获取股票数据"""
    return StockData().get_stock(code, start_date, end_date, market)


if __name__ == '__main__':
    # 测试
    sd = StockData()

    # 测试获取A股
    print("测试获取A股（茅台600519）...")
    df_a = sd.get_a_stock('600519', '2024-01-01', '2024-12-31')
    print(df_a.head())

    # 测试获取美股
    print("\n测试获取美股（AAPL）...")
    df_us = sd.get_us_stock('AAPL', '2024-01-01', '2024-12-31')
    print(df_us.head())
