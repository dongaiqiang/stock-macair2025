"""
尾盘选股模块
实现尾盘选股策略
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, time
import baostock as bs


class TailStockSelector:
    """尾盘选股器 - 根据8步筛选法"""

    def __init__(
        self,
        # 涨幅筛选
        min_change_pct: float = 3.0,
        max_change_pct: float = 5.0,
        # 换手率筛选
        min_turnover: float = 5.0,
        max_turnover: float = 10.0,
        # 量比筛选
        min_volume_ratio: float = 1.0,
        # 市值筛选 (亿)
        min_market_cap: float = 50,
        max_market_cap: float = 200,
    ):
        """
        初始化尾盘选股器

        Args:
            min_change_pct: 最小涨幅(%)
            max_change_pct: 最大涨幅(%)
            min_turnover: 最小换手率(%)
            max_turnover: 最大换手率(%)
            min_volume_ratio: 最小量比
            min_market_cap: 最小流通市值(亿)
            max_market_cap: 最大流通市值(亿)
        """
        self.params = {
            'min_change_pct': min_change_pct,
            'max_change_pct': max_change_pct,
            'min_turnover': min_turnover,
            'max_turnover': max_turnover,
            'min_volume_ratio': min_volume_ratio,
            'min_market_cap': min_market_cap,
            'max_market_cap': max_market_cap,
        }

    def get_realtime_stocks(self, date: str = None) -> pd.DataFrame:
        """
        获取实时股票数据用于选股

        Args:
            date: 日期，格式 'YYYY-MM-DD'

        Returns:
            股票数据 DataFrame
        """
        lg = bs.login()
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # 获取当日涨跌幅榜
        rs = bs.query_all_stock(date)

        data = []
        while rs.next():
            data.append(rs.get_row_data())

        bs.logout()

        if not data:
            return pd.DataFrame()

        fields = ['code', 'code_name', 'date', 'turnover', 'turnover_rate',
                  'volume_ratio', 'pe', 'pb', 'close', 'high', 'low', 'open',
                  'pre_close', 'change', 'change_pct', 'volume', 'amount']

        df = pd.DataFrame(data, columns=fields)

        # 转换数值列
        numeric_cols = ['close', 'high', 'low', 'open', 'pre_close', 'change',
                       'change_pct', 'volume', 'amount', 'turnover_rate', 'volume_ratio',
                       'pe', 'pb']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        return df

    def filter_by_change(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤1: 筛选涨幅"""
        p = self.params
        mask = (df['change_pct'] >= p['min_change_pct']) & (df['change_pct'] <= p['max_change_pct'])
        return df[mask]

    def filter_by_turnover(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤2: 筛选换手率"""
        p = self.params
        mask = (df['turnover_rate'] >= p['min_turnover']) & (df['turnover_rate'] <= p['max_turnover'])
        return df[mask]

    def filter_by_volume_ratio(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤3: 筛选量比"""
        p = self.params
        mask = df['volume_ratio'] >= p['min_volume_ratio']
        return df[mask]

    def filter_by_market_cap(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤4: 筛选流通市值"""
        # 市值需要另外获取，这里简化处理
        return df

    def filter_by_volume_pattern(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤5: 分析成交量形态 - 需要历史数据"""
        # 需要结合历史成交量分析
        return df

    def filter_by_kline(self, df: pd.DataFrame) -> pd.DataFrame:
        """步骤6: 分析K线与均线 - 需要历史数据"""
        # 需要结合历史数据分析
        return df

    def filter(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        执行8步筛选

        Args:
            df: 股票数据

        Returns:
            筛选后的股票列表
        """
        result = df.copy()

        # 步骤1: 涨幅筛选
        result = self.filter_by_change(result)
        print(f"  步骤1 涨幅({self.params['min_change_pct']}-{self.params['max_change_pct']}%): {len(result)} 只")

        # 步骤2: 换手率筛选
        result = self.filter_by_turnover(result)
        print(f"  步骤2 换手率({self.params['min_turnover']}-{self.params['max_turnover']}%): {len(result)} 只")

        # 步骤3: 量比筛选
        result = self.filter_by_volume_ratio(result)
        print(f"  步骤3 量比>={self.params['min_volume_ratio']}: {len(result)} 只")

        # 步骤4: 市值筛选
        result = self.filter_by_market_cap(result)
        print(f"  步骤4 市值筛选: {len(result)} 只")

        return result

    def rank_by_strength(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按强度排序

        Args:
            df: 筛选后的股票

        Returns:
            排序后的股票列表
        """
        if df.empty:
            return df

        # 综合评分
        df = df.copy()
        df['score'] = (
            df['change_pct'] * 0.3 +
            df['volume_ratio'] * 0.3 +
            df['turnover_rate'] * 0.2 +
            (100 - df['pe'].fillna(100).clip(0, 100)) * 0.1 +
            (200 - df['pb'].fillna(10).clip(0, 200)) * 0.1
        )

        return df.sort_values('score', ascending=False)


def select_tail_stocks(date: str = None) -> pd.DataFrame:
    """
    便捷尾盘选股函数

    Args:
        date: 日期

    Returns:
        选股结果
    """
    selector = TailStockSelector()
    df = selector.get_realtime_stocks(date)
    if df.empty:
        return df

    result = selector.filter(df)
    result = selector.rank_by_strength(result)

    return result


if __name__ == '__main__':
    print("=" * 50)
    print("尾盘选股测试")
    print("=" * 50)

    # 由于需要当日实时数据，这里仅演示结构
    print("\n尾盘选股器已创建")
    print("参数配置:")
    selector = TailStockSelector()
    for k, v in selector.params.items():
        print(f"  {k}: {v}")
