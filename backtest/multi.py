"""
多股票回测模块
支持多只股票同时回测
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings

warnings.filterwarnings('ignore')

from .engine import BacktestEngine
from .strategies import MAStrategy, RSIStrategy, BollStrategy, MACDStrategy
from data.fetcher import StockData


class MultiStockBacktest:
    """多股票回测"""

    def __init__(
        self,
        stocks: List[str],
        start_date: str,
        end_date: str,
        initial_cash: float = 1000000,
        commission: float = 0.001
    ):
        """
        初始化

        Args:
            stocks: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            initial_cash: 每只股票的初始资金
            commission: 手续费率
        """
        self.stocks = stocks
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = initial_cash
        self.commission = commission
        self.results = {}

    def run(
        self,
        strategy: type = MAStrategy,
        **strategy_params
    ) -> Dict[str, Dict]:
        """
        运行回测

        Args:
            strategy: 策略类
            **strategy_params: 策略参数

        Returns:
            每只股票的回测结果
        """
        results = {}

        for stock in self.stocks:
            try:
                # 获取数据
                sd = StockData()
                df = sd.get_a_stock(stock, self.start_date, self.end_date)

                if df is None or len(df) < 50:
                    print(f"  ⚠ {stock}: 数据不足，跳过")
                    continue

                # 回测
                engine = BacktestEngine(
                    initial_cash=self.initial_cash,
                    commission=self.commission
                )
                result = engine.run(df, strategy, **strategy_params)
                result['stock'] = stock

                results[stock] = result
                print(f"  ✓ {stock}: 收益率 {result['total_return']:+.2f}%")

            except Exception as e:
                print(f"  ✗ {stock}: {str(e)}")

        self.results = results
        return results

    def get_summary(self) -> pd.DataFrame:
        """获取汇总结果"""
        if not self.results:
            return pd.DataFrame()

        summary = []
        for stock, result in self.results.items():
            summary.append({
                'stock': stock,
                'final_value': result['final_value'],
                'total_return': result['total_return'],
                'max_drawdown': result['max_drawdown'],
                'total_trades': result['total_trades'],
                'win_rate': result['win_rate'],
            })

        df = pd.DataFrame(summary)
        df = df.sort_values('total_return', ascending=False)
        return df

    def get_best_stock(self) -> Dict[str, Any]:
        """获取最佳股票"""
        if not self.results:
            return {}

        return max(self.results.items(), key=lambda x: x[1]['total_return'])


def run_multi_stock(
    stocks: List[str],
    start_date: str,
    end_date: str,
    strategy: type = MAStrategy,
    initial_cash: float = 1000000,
    **strategy_params
) -> Dict[str, Dict]:
    """
    便捷的多股票回测函数

    Args:
        stocks: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        strategy: 策略类
        initial_cash: 初始资金
        **strategy_params: 策略参数

    Returns:
        回测结果字典
    """
    backtest = MultiStockBacktest(
        stocks=stocks,
        start_date=start_date,
        end_date=end_date,
        initial_cash=initial_cash
    )
    return backtest.run(strategy, **strategy_params)


if __name__ == '__main__':
    # 测试多股票回测
    print("=" * 50)
    print("多股票回测测试")
    print("=" * 50)

    stocks = ['600519', '000858', '601318']  # 茅台、五粮液、平安

    print(f"\n股票列表: {stocks}")
    print("策略: 双均线 MA5/20")

    results = run_multi_stock(
        stocks=stocks,
        start_date='2023-01-01',
        end_date='2024-12-31',
        strategy=MAStrategy,
        fast_period=5,
        slow_period=20
    )

    print("\n" + "=" * 50)
    print("回测汇总")
    print("=" * 50)

    backtest = MultiStockBacktest(
        stocks=stocks,
        start_date='2023-01-01',
        end_date='2024-12-31'
    )
    backtest.results = results
    summary = backtest.get_summary()
    print(summary.to_string(index=False))

    best = backtest.get_best_stock()
    if best:
        print(f"\n最佳股票: {best[0]}, 收益率: {best[1]['total_return']:+.2f}%")
