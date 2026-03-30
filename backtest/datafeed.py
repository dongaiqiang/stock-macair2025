"""
Backtrader 数据源适配器
将 baostock/yfinance 数据转换为 Backtrader 格式
"""

import backtrader as bt
import pandas as pd
from datetime import datetime


class PandasData(bt.feeds.PandasData):
    """Pandas 数据源适配器"""

    params = (
        ('datetime', 0),  # 第一列是datetime
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', -1),
    )


def dataframe_to_backtest(df: pd.DataFrame) -> PandasData:
    """
    将 pandas DataFrame 转换为 Backtrader 数据源

    Args:
        df: 包含 open, high, low, close, volume 的 DataFrame

    Returns:
        Backtrader PandasData 对象
    """
    # 创建副本
    df_copy = df.copy()

    # 确保索引是日期时间
    if isinstance(df_copy.index, pd.DatetimeIndex):
        df_copy = df_copy.reset_index()
    elif 'date' in df_copy.columns:
        df_copy['date'] = pd.to_datetime(df_copy['date'])
        df_copy = df_copy.set_index('date')
        df_copy = df_copy.reset_index()
    else:
        df_copy.reset_index(inplace=True)

    # 重命名列为 Backtrader 需要的格式
    cols = df_copy.columns.tolist()
    new_cols = []
    for col in cols:
        col_lower = col.lower()
        if col_lower == 'index':
            new_cols.append('datetime')
        elif col_lower == 'date':
            new_cols.append('datetime')
        else:
            new_cols.append(col_lower)

    df_copy.columns = new_cols

    return PandasData(dataname=df_copy)
