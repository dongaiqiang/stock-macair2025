#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
量化交易系统 - 完整端到端演示（优化版）
执行完整流程：数据获取 → 技术分析 → 回测 → 机器学习 → 参数优化 → 多股票 → 可视化
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockData
from indicators import add_indicators
from backtest import (
    run_backtest, MAStrategy, RSIStrategy, BollStrategy,
    StrategyOptimizer, quick_optimize, run_multi_stock
)
from ml.features import FeatureEngineer
from ml.models import StockPredictor
from visualization import plot_candle_with_indicators, plot_backtest_results


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step, description):
    print(f"\n【步骤 {step}】{description}")
    print("-" * 40)


def main():
    print_header("量化交易系统 - 完整端到端演示（优化版）")
    print("目标：演示完整的量化投资流程（包含所有优化）")
    print("股票：贵州茅台（600519）")
    print("时间范围：2023-01-01 至 2024-12-31")

    # ========== 步骤1: 获取数据 ==========
    print_step(1, "获取股票数据")

    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    print(f"✓ 成功获取数据")
    print(f"  - 数据条数: {len(df)}")
    print(f"  - 时间范围: {df.index[0].strftime('%Y-%m-%d')} 至 {df.index[-1].strftime('%Y-%m-%d')}")

    # ========== 步骤2: 技术分析 ==========
    print_step(2, "计算技术指标")

    df_with_indicators = add_indicators(df)
    print(f"✓ 成功计算技术指标 (37个特征)")

    # ========== 步骤3: 传统策略回测 ==========
    print_step(3, "传统策略回测（Backtrader）")

    strategies = [
        ('双均线 MA5/20', MAStrategy, {'fast_period': 5, 'slow_period': 20}),
        ('双均线 MA5/20 止损止盈', MAStrategy, {'fast_period': 5, 'slow_period': 20, 'stop_loss': 0.05, 'take_profit': 0.10}),
        ('RSI 超买超卖', RSIStrategy, {}),
        ('布林带突破', BollStrategy, {}),
    ]

    results_list = []
    for name, strategy, params in strategies:
        results = run_backtest(
            df,
            strategy=strategy,
            initial_cash=1000000,
            commission=0.001,
            **params
        )
        results_list.append((name, results))

        sharpe = results.get('sharpe_ratio')
        sharpe_str = f"{sharpe:.4f}" if sharpe is not None else "N/A"

        print(f"\n  【{name}】")
        print(f"    最终资金:    ¥{results['final_value']:,.0f}")
        print(f"    总收益率:   {results['total_return']:+.2f}%")
        print(f"    最大回撤:   {results['max_drawdown']:.2f}%")
        print(f"    交易次数:   {results['total_trades']}")
        print(f"    胜率:       {results['win_rate']:.1f}%")

    best_strategy = max(results_list, key=lambda x: x[1]['total_return'])
    print(f"\n  ★ 传统策略最佳: {best_strategy[0]}, 收益率 {best_strategy[1]['total_return']:+.2f}%")

    # ========== 步骤4: 参数优化 ==========
    print_step(4, "策略参数优化")

    print("\n  优化双均线策略参数...")
    optimizer = StrategyOptimizer()
    opt_results = optimizer.optimize_ma(df, fast_range=(3, 8), slow_range=(10, 25))

    print("\n  Top 5 参数组合:")
    for i, row in opt_results.head(5).iterrows():
        print(f"    {row['params']}: 收益率 {row['total_return']:+.2f}%, 胜率 {row['win_rate']:.1f}%")

    # ========== 步骤5: 机器学习策略 ==========
    print_step(5, "机器学习策略")

    print("\n  5.1 特征工程（修复数据泄露）...")
    fe = FeatureEngineer()
    df_features = fe.create_features(df)
    print(f"      生成特征数量: {len(fe.feature_columns)}")

    print("\n  5.2 准备训练数据...")
    X, y = fe.prepare_train_data(df_features)
    print(f"      训练数据: X={X.shape}, y={y.shape}")

    print("\n  5.3 训练模型...")
    predictor = StockPredictor(model_type='lgbm')
    train_results = predictor.train(X, y)
    print(f"      测试集准确率: {train_results['accuracy']:.2%}")

    print("\n  5.4 ML策略回测...")
    ml_backtest = predictor.backtest(df_features, initial_capital=1000000, position_size=0.1)
    ml_return = ml_backtest['total_return']
    ml_return_str = f"{ml_return:+.2f}%" if not pd.isna(ml_return) else "N/A"
    print(f"      总收益率: {ml_return_str}")
    print(f"      交易次数: {ml_backtest['total_trades']}")

    # ========== 步骤6: 多股票回测 ==========
    print_step(6, "多股票回测")

    stocks = ['600519', '000858', '601318']  # 茅台、五粮液、平安
    print(f"\n  股票列表: {stocks}")
    print(f"  策略: 双均线 MA5/20")

    multi_results = run_multi_stock(
        stocks=stocks,
        start_date='2023-01-01',
        end_date='2024-12-31',
        strategy=MAStrategy,
        fast_period=5,
        slow_period=20
    )

    print("\n  回测汇总:")
    for stock, result in multi_results.items():
        print(f"    {stock}: 收益率 {result['total_return']:+.2f}%")

    # ========== 步骤7: 可视化 ==========
    print_step(7, "生成可视化图表")

    chart_path = os.path.join(os.path.dirname(__file__), 'chart.png')
    plot_candle_with_indicators(
        df_with_indicators.tail(60),
        indicators=['ma5', 'ma20', 'macd'],
        title='贵州茅台 2024 K线图',
        save_path=chart_path,
        show=False
    )
    print(f"  ✓ K线图已保存: {chart_path}")

    result_path = os.path.join(os.path.dirname(__file__), 'backtest_result.png')
    plot_backtest_results(
        best_strategy[1],
        save_path=result_path,
        show=False
    )
    print(f"  ✓ 回测结果图已保存: {result_path}")

    # ========== 完成 ==========
    print_header("演示完成")

    print("""
优化项目:
  ✓ 修复ML数据泄露问题
  ✓ 添加止损止盈功能
  ✓ 添加策略参数优化
  ✓ 添加多股票回测

策略对比:
""")

    print(f"  传统策略最佳: {best_strategy[0]}, 收益率 {best_strategy[1]['total_return']:+.2f}%")
    if not pd.isna(ml_return):
        print(f"  ML策略: 收益率 {ml_return:+.2f}%")

    print("""
生成的文件:
  - chart.png: K线与技术指标图
  - backtest_result.png: 回测结果图
""")

    return 0


if __name__ == '__main__':
    import pandas as pd
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
