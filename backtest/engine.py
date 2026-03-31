"""
回测引擎
提供简洁的 API 进行回测
"""

import backtrader as bt
import pandas as pd
from datetime import datetime
from typing import Optional, Union
import warnings

from .datafeed import dataframe_to_backtest
from .strategies import MAStrategy, RSIStrategy, BollStrategy, MACDStrategy


class BacktestEngine:
    """回测引擎"""

    def __init__(
        self,
        initial_cash: float = 1000000,
        commission: float = 0.001,
        printlog: bool = False
    ):
        """
        初始化回测引擎

        Args:
            initial_cash: 初始资金，默认 100 万
            commission: 手续费率，默认千分之一
            printlog: 是否打印交易日志
        """
        self.initial_cash = initial_cash
        self.commission = commission
        self.printlog = printlog
        self.cerebro = None
        self.results = None
        self.trades_log = []  # 记录买卖点

    def run(
        self,
        df: pd.DataFrame,
        strategy: type = MAStrategy,
        **strategy_params
    ) -> dict:
        """
        运行回测

        Args:
            df: 股票数据 DataFrame
            strategy: 策略类
            **strategy_params: 策略参数

        Returns:
            dict: 回测结果
        """
        # 重置交易日志
        self.trades_log = []

        # 创建大脑
        self.cerebro = bt.Cerebro()

        # 设置初始资金和手续费
        self.cerebro.broker.setcash(self.initial_cash)
        self.cerebro.broker.setcommission(commission=self.commission)

        # 添加数据源
        data = dataframe_to_backtest(df)
        self.cerebro.adddata(data)

        # 添加策略（传入 trades_log 引用）
        self.cerebro.addstrategy(
            strategy,
            printlog=self.printlog,
            trades_log=self.trades_log,
            **strategy_params
        )

        # 设置分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='time_return', timeframe=bt.TimeFrame.Days)

        # 运行回测
        self.results = self.cerebro.run()
        strat = self.results[0]

        # 提取结果
        return self._extract_results(strat, df)

    def _extract_results(self, strat, df: pd.DataFrame = None) -> dict:
        """提取回测结果"""
        # 最终资金
        final_value = self.cerebro.broker.getvalue()

        # 收益率
        returns = strat.analyzers.returns.get_analysis()
        total_return = returns.get('rtot', 0) * 100  # 转换为百分比

        # 夏普比率
        sharpe = strat.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe.get('sharperatio', 0)

        # 回撤
        drawdown = strat.analyzers.drawdown.get_analysis()
        max_drawdown = drawdown.get('max', {}).get('drawdown', 0)

        # 交易统计
        trades = strat.analyzers.trades.get_analysis()
        total_trades = trades.get('total', {}).get('total', 0)
        won_trades = trades.get('won', {}).get('total', 0)
        lost_trades = trades.get('lost', {}).get('total', 0)

        win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0

        # 组合价值曲线
        portfolio_values = []
        if hasattr(strat.analyzers, 'time_return'):
            time_returns = strat.analyzers.time_return.get_analysis()
            cumulative = self.initial_cash
            portfolio_values = [{'value': self.initial_cash}]
            for date, ret in time_returns.items():
                cumulative *= (1 + ret)
                portfolio_values.append({'date': str(date), 'value': cumulative})

        return {
            'initial_cash': self.initial_cash,
            'final_value': final_value,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'won_trades': won_trades,
            'lost_trades': lost_trades,
            'win_rate': win_rate,
            'trades_log': self.trades_log,  # 添加买卖点记录
            'portfolio_values': portfolio_values,  # 添加组合价值曲线
        }

    def print_results(self, results: dict):
        """打印回测结果"""
        print("=" * 50)
        print("回测结果")
        print("=" * 50)
        print(f"初始资金:     ¥{results['initial_cash']:,.2f}")
        print(f"最终资金:     ¥{results['final_value']:,.2f}")
        print(f"总收益率:     {results['total_return']:.2f}%")
        print(f"夏普比率:     {results['sharpe_ratio']:.4f}")
        print(f"最大回撤:     {results['max_drawdown']:.2f}%")
        print(f"总交易次数:   {results['total_trades']}")
        print(f"盈利次数:     {results['won_trades']}")
        print(f"亏损次数:     {results['lost_trades']}")
        print(f"胜率:         {results['win_rate']:.2f}%")
        print("=" * 50)


def run_backtest(
    df: pd.DataFrame,
    strategy: type = MAStrategy,
    initial_cash: float = 1000000,
    commission: float = 0.001,
    printlog: bool = False,
    **strategy_params
) -> dict:
    """
    便捷的回测函数

    Args:
        df: 股票数据
        strategy: 策略类
        initial_cash: 初始资金
        commission: 手续费率
        printlog: 是否打印交易日志
        **strategy_params: 策略参数

    Returns:
        dict: 回测结果
    """
    engine = BacktestEngine(
        initial_cash=initial_cash,
        commission=commission,
        printlog=printlog
    )
    results = engine.run(df, strategy, **strategy_params)
    if printlog:
        engine.print_results(results)
    return results


if __name__ == '__main__':
    # 测试回测
    from data.fetcher import StockData

    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    print("测试双均线策略...")
    results = run_backtest(
        df,
        strategy=MAStrategy,
        fast_period=5,
        slow_period=20,
        initial_cash=1000000,
        printlog=False
    )

    print(f"\n最终资金: ¥{results['final_value']:,.2f}")
    print(f"总收益率: {results['total_return']:.2f}%")
    print(f"胜率: {results['win_rate']:.2f}%")
