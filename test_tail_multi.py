#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
尾盘突破策略多股票测试 - A股数据
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockData
from backtest import run_backtest, TailBreakoutStrategy


def test_multi_stocks():
    print("=" * 60)
    print("  尾盘突破策略 - 多股票测试")
    print("=" * 60)

    # 测试多只A股
    stock_list = [
        ('600519', '贵州茅台'),
        ('000858', '五粮液'),
        ('601318', '中国平安'),
        ('600036', '招商银行'),
        ('000001', '平安银行'),
    ]

    sd = StockData()

    results_list = []
    for code, name in stock_list:
        print(f"\n【{name}({code})】")
        try:
            df = sd.get_a_stock(code, '2023-01-01', '2024-12-31')
            print(f"  数据条数: {len(df)}")

            # 使用优化参数
            results = run_backtest(
                df,
                strategy=TailBreakoutStrategy,
                initial_cash=1000000,
                commission=0.001,
                lookback=30,
                breakout_rate=0.98
            )

            print(f"  最终资金: ¥{results['final_value']:,.0f}")
            print(f"  总收益率: {results['total_return']:+.2f}%")
            print(f"  交易次数: {results['total_trades']}")
            print(f"  胜率: {results['win_rate']:.1f}%")

            results_list.append((name, results))
        except Exception as e:
            print(f"  错误: {e}")

    # 汇总
    print("\n" + "=" * 60)
    print("  汇总结果")
    print("=" * 60)
    for name, r in results_list:
        print(f"  {name}: {r['total_return']:+.2f}% ({r['total_trades']}笔)")

    # 最佳
    if results_list:
        best = max(results_list, key=lambda x: x[1]['total_return'])
        avg_return = sum(r['total_return'] for _, r in results_list) / len(results_list)
        print(f"\n  最佳: {best[0]} ({best[1]['total_return']:+.2f}%)")
        print(f"  平均: {avg_return:+.2f}%")

    return results_list


if __name__ == '__main__':
    try:
        result = test_multi_stocks()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()