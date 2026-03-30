"""
策略优化器
网格搜索最优参数
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from itertools import product

from .engine import BacktestEngine
from .strategies import MAStrategy, RSIStrategy, BollStrategy, MACDStrategy


class StrategyOptimizer:
    """策略优化器"""

    def __init__(self, initial_cash: float = 1000000, commission: float = 0.001):
        self.initial_cash = initial_cash
        self.commission = commission
        self.results = []

    def optimize_ma(
        self,
        df: pd.DataFrame,
        fast_range: tuple = (3, 10),
        slow_range: tuple = (10, 30),
        step: int = 1
    ) -> pd.DataFrame:
        """
        优化双均线策略参数

        Args:
            df: 股票数据
            fast_range: 快速均线范围 (start, end)
            slow_range: 慢速均线范围 (start, end)
            step: 步长

        Returns:
            优化结果 DataFrame
        """
        results = []

        fast_periods = range(fast_range[0], fast_range[1] + 1, step)
        slow_periods = range(slow_range[0], slow_range[1] + 1, step)

        for fast in fast_periods:
            for slow in slow_periods:
                if fast >= slow:
                    continue

                engine = BacktestEngine(
                    initial_cash=self.initial_cash,
                    commission=self.commission
                )
                result = engine.run(df, MAStrategy, fast_period=fast, slow_period=slow)
                result['params'] = f"MA{fast}/{slow}"
                results.append(result)

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('total_return', ascending=False)
        self.results = df_results

        return df_results

    def optimize_rsi(
        self,
        df: pd.DataFrame,
        period_range: tuple = (7, 21),
        upper_range: tuple = (60, 80),
        lower_range: tuple = (20, 40),
    ) -> pd.DataFrame:
        """
        优化RSI策略参数
        """
        results = []

        for period in range(period_range[0], period_range[1] + 1):
            for upper in range(upper_range[0], upper_range[1] + 1, 5):
                for lower in range(lower_range[0], lower_range[1] + 1, 5):
                    if lower >= upper:
                        continue

                    engine = BacktestEngine(
                        initial_cash=self.initial_cash,
                        commission=self.commission
                    )
                    result = engine.run(
                        df, RSIStrategy,
                        rsi_period=period,
                        rsi_upper=upper,
                        rsi_lower=lower
                    )
                    result['params'] = f"RSI({period},{upper},{lower})"
                    results.append(result)

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('total_return', ascending=False)
        self.results = df_results

        return df_results

    def optimize_boll(
        self,
        df: pd.DataFrame,
        period_range: tuple = (10, 30),
        devfactor_range: tuple = (1.5, 3.0),
    ) -> pd.DataFrame:
        """
        优化布林带策略参数
        """
        results = []

        for period in range(period_range[0], period_range[1] + 1, 2):
            for dev in np.arange(devfactor_range[0], devfactor_range[1] + 0.5, 0.5):

                engine = BacktestEngine(
                    initial_cash=self.initial_cash,
                    commission=self.commission
                )
                result = engine.run(
                    df, BollStrategy,
                    period=period,
                    devfactor=dev
                )
                result['params'] = f"BOLL({period},{dev})"
                results.append(result)

        df_results = pd.DataFrame(results)
        df_results = df_results.sort_values('total_return', ascending=False)
        self.results = df_results

        return df_results

    def get_best_params(self, top_n: int = 5) -> List[Dict]:
        """获取最佳参数"""
        if self.results.empty:
            return []

        best = self.results.head(top_n)
        return best.to_dict('records')


def quick_optimize(df: pd.DataFrame, strategy: str = 'ma') -> pd.DataFrame:
    """
    快速优化

    Args:
        df: 股票数据
        strategy: 策略类型 'ma', 'rsi', 'boll'

    Returns:
        优化结果
    """
    optimizer = StrategyOptimizer()

    if strategy == 'ma':
        return optimizer.optimize_ma(df)
    elif strategy == 'rsi':
        return optimizer.optimize_rsi(df)
    elif strategy == 'boll':
        return optimizer.optimize_boll(df)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


if __name__ == '__main__':
    from data.fetcher import StockData

    print("=" * 50)
    print("策略参数优化测试")
    print("=" * 50)

    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    # 优化双均线
    print("\n优化双均线策略...")
    optimizer = StrategyOptimizer()
    results = optimizer.optimize_ma(df, fast_range=(3, 10), slow_range=(10, 30), step=1)

    print("\nTop 5 参数:")
    print(results[['params', 'total_return', 'win_rate', 'total_trades']].head(10).to_string(index=False))
