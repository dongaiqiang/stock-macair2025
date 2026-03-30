#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
尾盘突破策略测试 - 使用A股数据
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockData
from backtest import run_backtest, TailBreakoutStrategy


def test_tail_breakout():
    print("=" * 60)
    print("  尾盘突破策略测试 - A股数据")
    print("=" * 60)

    # 获取A股数据
    print("\n【步骤1】获取A股数据...")
    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    print(f"  数据条数: {len(df)}")
    print(f"  时间范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")

    # 回测尾盘突破策略
    print("\n【步骤2】回测尾盘突破策略...")

    # 测试不同参数
    params_list = [
        {'lookback': 10, 'breakout_rate': 0.98, 'name': 'MA10 98%'},
        {'lookback': 20, 'breakout_rate': 0.98, 'name': 'MA20 98%'},
        {'lookback': 20, 'breakout_rate': 0.95, 'name': 'MA20 95%'},
        {'lookback': 30, 'breakout_rate': 0.98, 'name': 'MA30 98%'},
    ]

    results_list = []
    for params in params_list:
        name = params.pop('name')
        results = run_backtest(
            df,
            strategy=TailBreakoutStrategy,
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

    # 找出最佳策略
    best = max(results_list, key=lambda x: x[1]['total_return'])
    print(f"\n  ★ 最佳策略: {best[0]}, 收益率 {best[1]['total_return']:+.2f}%")

    return best


if __name__ == '__main__':
    try:
        result = test_tail_breakout()
        print("\n" + "=" * 60)
        print("  测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
