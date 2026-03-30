#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
尾盘策略测试 - 使用分钟级数据
真实尾盘：14:30-15:00买入，次日卖出
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockData
import backtrader as bt
import pandas as pd
from datetime import datetime, time


class TailBreakoutMinuteStrategy(bt.Strategy):
    """尾盘突破策略 - 分钟级数据版本

    策略逻辑：
    - 每天14:30后，判断是否突破当日最高价
    - 如果收盘前15分钟涨幅超过阈值，买入
    - 次日开盘卖出
    """

    params = (
        ('breakout_threshold', 0.99),  # 收盘价/最高价阈值
        ('min_gain', 0.005),           # 最小涨幅要求
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.dataopen = self.datas[0].open
        self.order = None
        self.buy_date = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                if self.params.printlog:
                    print(f'尾盘买入: {self.buy_price:.2f}')
            elif self.params.printlog:
                print(f'次日卖出: {order.executed.price:.2f}')
        self.order = None

    def next(self):
        if self.order:
            return

        # 获取当前时间（小时+分钟）
        dt = self.datas[0].datetime.datetime(0)
        current_time = dt.time() if isinstance(dt, datetime) else dt

        # 判断是否为14:30（转换为分钟数）
        minutes = current_time.hour * 60 + current_time.minute

        # 尾盘时段：14:30 - 14:55（收盘前5分钟）
        if 870 <= minutes <= 895:  # 14:30 = 870分钟
            if not self.position:
                # 计算当日最高价
                today_high = self.datahigh[0]

                # 尾盘买入条件：收盘价接近当日最高价
                if self.dataclose[0] >= today_high * self.params.breakout_threshold:
                    self.order = self.buy()
                    self.buy_date = dt.date()

        # 次日开盘卖出
        elif self.position:
            # 开盘后5分钟内卖出
            if minutes < 570:  # 9:30 = 570分钟
                self.order = self.sell()
                self.buy_date = None


def run_backtest_minute(df, strategy, **kwargs):
    """分钟级数据回测"""
    cerebro = bt.Cerebro()

    # 添加数据
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    # 添加策略
    cerebro.addstrategy(strategy, **kwargs)

    # 设置初始资金
    cerebro.broker.setcash(1000000)

    # 设置手续费
    cerebro.broker.setcommission(commission=0.001)

    # 执行回测
    initial_value = cerebro.broker.getvalue()
    cerebro.run()
    final_value = cerebro.broker.getvalue()

    # 计算收益
    total_return = (final_value - initial_value) / initial_value * 100

    return {
        'initial_value': initial_value,
        'final_value': final_value,
        'total_return': total_return,
    }


def test_tail_minute():
    print("=" * 60)
    print("  尾盘策略测试 - 分钟级数据")
    print("=" * 60)

    sd = StockData()

    # 获取分钟级数据（5分钟频率）
    print("\n【步骤1】获取分钟级数据...")
    df = sd.get_a_stock_minute('600519', '2024-01-01', '2024-06-30', frequency=5)
    print(f"  数据条数: {len(df)}")
    print(f"  时间范围: {df.index[0]} 至 {df.index[-1]}")
    print(f"  示例数据:\n{df.tail(5)}")

    print("\n【步骤2】回测尾盘策略...")

    results = run_backtest_minute(
        df,
        TailBreakoutMinuteStrategy,
        breakout_threshold=0.99,
        min_gain=0.005
    )

    print(f"\n  最终资金:    ¥{results['final_value']:,.0f}")
    print(f"  总收益率:   {results['total_return']:+.2f}%")

    return results


if __name__ == '__main__':
    try:
        result = test_tail_minute()
        print("\n测试完成!")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()