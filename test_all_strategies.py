#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
所有策略对比测试
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockData
from backtest import (
    run_backtest, MAStrategy, RSIStrategy, BollStrategy,
    MACDStrategy, TurtleStrategy, MeanReversionStrategy, TailBreakoutStrategy
)


def test_all_strategies():
    print("=" * 60)
    print("  所有策略对比测试 - A股数据")
    print("=" * 60)

    # 获取数据
    print("\n【获取数据】贵州茅台 600519 (2023-2024)")
    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')
    print(f"  数据条数: {len(df)}")

    # 定义所有策略
    strategies = [
        ('双均线 MA5/20', MAStrategy, {'fast_period': 5, 'slow_period': 20}),
        ('RSI 超买超卖', RSIStrategy, {}),
        ('布林带突破', BollStrategy, {}),
        ('MACD 金叉死叉', MACDStrategy, {}),
        ('海龟交易法', TurtleStrategy, {}),
        ('均值回归', MeanReversionStrategy, {}),
        ('尾盘突破', TailBreakoutStrategy, {'lookback': 30, 'breakout_rate': 0.98}),
    ]

    print("\n【回测结果】")
    print("-" * 60)

    results_list = []
    for name, strategy, params in strategies:
        try:
            results = run_backtest(
                df,
                strategy=strategy,
                initial_cash=1000000,
                commission=0.001,
                **params
            )
            results_list.append((name, results))

            print(f"\n  【{name}】")
            print(f"    最终资金:    ¥{results['final_value']:,.0f}")
            print(f"    总收益率:   {results['total_return']:+.2f}%")
            print(f"    最大回撤:   {results['max_drawdown']:.2f}%")
            print(f"    交易次数:   {results['total_trades']}")
            print(f"    胜率:       {results['win_rate']:.1f}%")
        except Exception as e:
            print(f"\n  【{name}】错误: {e}")

    # 汇总排名
    print("\n" + "=" * 60)
    print("  策略排名（按收益率）")
    print("=" * 60)

    results_list.sort(key=lambda x: x[1]['total_return'], reverse=True)

    for i, (name, r) in enumerate(results_list, 1):
        print(f"  {i}. {name}: {r['total_return']:+.2f}% (胜率 {r['win_rate']:.0f}%, {r['total_trades']}笔)")

    # 最佳策略
    best = results_list[0]
    print(f"\n  ★ 最佳策略: {best[0]}, 收益率 {best[1]['total_return']:+.2f}%")

    return results_list


if __name__ == '__main__':
    try:
        result = test_all_strategies()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()