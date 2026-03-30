"""
测试策略模块
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backtrader as bt
from backtest.strategies import (
    MAStrategy, RSIStrategy, BollStrategy, MACDStrategy,
    TurtleStrategy, MeanReversionStrategy, TailBreakoutStrategy
)
from backtest.engine import BacktestEngine, run_backtest


@pytest.fixture
def sample_df():
    """创建示例股票数据"""
    np.random.seed(42)
    n = 200  # 足够的数据点用于回测
    dates = pd.date_range('2024-01-01', periods=n, freq='D')

    # 生成合理的股票价格数据
    close = 100 + np.cumsum(np.random.randn(n) * 2)
    high = close + np.abs(np.random.randn(n))
    low = close - np.abs(np.random.randn(n))
    open_price = close + np.random.randn(n)
    volume = np.random.randint(1000, 10000, n)

    df = pd.DataFrame({
        'date': dates,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })
    df = df.set_index('date')

    # 确保 high >= close >= low
    df['high'] = df[['high', 'close', 'open']].max(axis=1)
    df['low'] = df[['low', 'close', 'open']].min(axis=1)

    return df


@pytest.fixture
def cerebro():
    """创建 Cerebro 引擎"""
    return bt.Cerebro()


class TestMAStrategy:
    """测试双均线策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(MAStrategy, fast_period=5, slow_period=20)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)
        cerebro.broker.setcommission(commission=0.001)

        results = cerebro.run()
        assert results is not None
        assert len(results) == 1

    def test_with_stop_loss(self, cerebro, sample_df):
        """测试带止损的策略"""
        cerebro.addstrategy(MAStrategy, fast_period=5, slow_period=20, stop_loss=0.05)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None

    def test_with_take_profit(self, cerebro, sample_df):
        """测试带止盈的策略"""
        cerebro.addstrategy(MAStrategy, fast_period=5, slow_period=20, take_profit=0.10)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestRSIStrategy:
    """测试 RSI 策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(RSIStrategy, rsi_period=14, rsi_upper=70, rsi_lower=30)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None

    def test_custom_rsi_params(self, cerebro, sample_df):
        """测试自定义 RSI 参数"""
        cerebro.addstrategy(RSIStrategy, rsi_period=21, rsi_upper=80, rsi_lower=20)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestBollStrategy:
    """测试布林带策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(BollStrategy, period=20, devfactor=2.0)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None

    def test_custom_boll_params(self, cerebro, sample_df):
        """测试自定义布林带参数"""
        cerebro.addstrategy(BollStrategy, period=26, devfactor=2.5)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestMACDStrategy:
    """测试 MACD 策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(MACDStrategy, fast=12, slow=26, signal=9)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None

    def test_custom_macd_params(self, cerebro, sample_df):
        """测试自定义 MACD 参数"""
        cerebro.addstrategy(MACDStrategy, fast=6, slow=13, signal=5)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestTurtleStrategy:
    """测试海龟交易策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(TurtleStrategy, entry_period=20, exit_period=10)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestMeanReversionStrategy:
    """测试均值回归策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(MeanReversionStrategy, period=20, std_dev=2.0)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestTailBreakoutStrategy:
    """测试尾盘突破策略"""

    def test_init(self, cerebro, sample_df):
        """测试策略初始化"""
        cerebro.addstrategy(TailBreakoutStrategy, lookback=20, breakout_rate=0.98)
        data = bt.feeds.PandasData(dataname=sample_df)
        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)

        results = cerebro.run()
        assert results is not None


class TestBacktestEngine:
    """测试回测引擎"""

    def test_engine_init(self):
        """测试引擎初始化"""
        engine = BacktestEngine(initial_cash=1000000, commission=0.001)
        assert engine.initial_cash == 1000000
        assert engine.commission == 0.001

    def test_run_backtest(self, sample_df):
        """测试运行回测"""
        results = run_backtest(
            sample_df,
            strategy=MAStrategy,
            fast_period=5,
            slow_period=20,
            initial_cash=1000000,
            commission=0.001
        )

        assert 'initial_cash' in results
        assert 'final_value' in results
        assert 'total_return' in results
        assert 'max_drawdown' in results
        assert 'total_trades' in results
        assert 'win_rate' in results

    def test_backtest_results_values(self, sample_df):
        """测试回测结果值合理性"""
        results = run_backtest(
            sample_df,
            strategy=MAStrategy,
            initial_cash=100000,
            commission=0.001
        )

        # 初始资金应该正确
        assert results['initial_cash'] == 100000
        # 最终资金应该为正
        assert results['final_value'] > 0
        # 夏普比率应该是数字或 None (在某些情况下可能无法计算)
        assert results['sharpe_ratio'] is None or isinstance(results['sharpe_ratio'], (int, float))

    def test_multiple_strategies(self, sample_df):
        """测试多个策略回测"""
        strategies = [
            (MAStrategy, {'fast_period': 5, 'slow_period': 20}),
            (RSIStrategy, {'rsi_period': 14}),
            (BollStrategy, {'period': 20}),
        ]

        for strategy, params in strategies:
            results = run_backtest(sample_df, strategy=strategy, **params)
            assert results is not None
            assert 'total_return' in results


class TestStrategyIntegration:
    """测试策略集成"""

    def test_all_strategies_run(self, sample_df):
        """测试所有策略都能运行"""
        strategies = [
            MAStrategy,
            RSIStrategy,
            BollStrategy,
            MACDStrategy,
            TurtleStrategy,
            MeanReversionStrategy,
            TailBreakoutStrategy,
        ]

        for strategy in strategies:
            try:
                results = run_backtest(sample_df, strategy=strategy)
                assert results is not None, f"{strategy.__name__} returned None"
            except Exception as e:
                pytest.fail(f"{strategy.__name__} failed with error: {e}")
