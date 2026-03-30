"""
可视化模块
提供 K 线图、技术指标图表、回测结果可视化
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from typing import Optional, List
import warnings

warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def plot_candle(
    df: pd.DataFrame,
    title: str = "Stock Price",
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    绘制 K 线图

    Args:
        df: 股票数据，需要包含 open, high, low, close 列
        title: 图表标题
        save_path: 保存路径
        show: 是否显示图表
    """
    plot_df = df.copy()
    if isinstance(plot_df.index, pd.DatetimeIndex):
        plot_df.index = pd.to_datetime(plot_df.index)

    mpf_data = plot_df[['open', 'high', 'low', 'close', 'volume']].copy()
    mpf_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    mc = mpf.make_marketcolors(
        up='#ff0000',
        down='#00ff00',
        edge='inherit',
        wick='inherit',
    )
    style = mpf.make_mpf_style(marketcolors=mc)

    mpf.plot(
        mpf_data,
        type='candle',
        style=style,
        title=title,
        volume=True,
        savefig=dict(fname=save_path, dpi=150) if save_path else None,
    )


def plot_candle_with_indicators(
    df: pd.DataFrame,
    indicators: Optional[List[str]] = None,
    title: str = "Stock Price with Indicators",
    save_path: Optional[str] = None,
    show: bool = True
):
    """
    绘制带技术指标的 K 线图

    Args:
        df: 股票数据
        indicators: 要显示的技术指标列表，如 ['ma5', 'ma20', 'rsi', 'boll']
        title: 图表标题
        save_path: 保存路径
        show: 是否显示图表
    """
    plot_df = df.copy()
    if isinstance(plot_df.index, pd.DatetimeIndex):
        plot_df.index = pd.to_datetime(plot_df.index)

    mpf_data = plot_df[['open', 'high', 'low', 'close', 'volume']].copy()
    mpf_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    mc = mpf.make_marketcolors(
        up='#ff0000',
        down='#00ff00',
        edge='inherit',
        wick='inherit',
    )
    style = mpf.make_mpf_style(marketcolors=mc)

    apds = []

    if indicators:
        if 'ma5' in indicators and 'ma5' in plot_df.columns:
            apds.append(mpf.make_addplot(plot_df['ma5'], color='blue', width=0.8))
        if 'ma10' in indicators and 'ma10' in plot_df.columns:
            apds.append(mpf.make_addplot(plot_df['ma10'], color='orange', width=0.8))
        if 'ma20' in indicators and 'ma20' in plot_df.columns:
            apds.append(mpf.make_addplot(plot_df['ma20'], color='purple', width=0.8))
        if 'ma60' in indicators and 'ma60' in plot_df.columns:
            apds.append(mpf.make_addplot(plot_df['ma60'], color='brown', width=0.8))

        if 'macd' in indicators and 'macd' in plot_df.columns:
            apds.append(mpf.make_addplot(plot_df['macd'], panel=2, color='blue', width=0.8))
            apds.append(mpf.make_addplot(plot_df['macd_signal'], panel=2, color='orange', width=0.8))

        if 'rsi' in indicators and 'rsi' in plot_df.columns:
            apds.append(mpf.make_addplot(plot_df['rsi'], panel=3, color='purple', width=0.8, ylabel='RSI'))

    mpf.plot(
        mpf_data,
        type='candle',
        style=style,
        title=title,
        volume=True,
        addplot=apds if apds else None,
        savefig=dict(fname=save_path, dpi=150) if save_path else None,
    )


def plot_backtest_results(
    results: dict,
    save_path: Optional[str] = None,
    show: bool = True
):
    """绘制回测结果"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle('Backtest Results', fontsize=16)

    ax1 = axes[0, 0]
    metrics = ['Total Return', 'Max Drawdown']
    values = [results.get('total_return', 0), -results.get('max_drawdown', 0)]
    colors = ['green' if v > 0 else 'red' for v in values]
    ax1.bar(metrics, values, color=colors)
    ax1.set_ylabel('Percentage (%)')
    ax1.set_title('Returns & Drawdown')
    for i, v in enumerate(values):
        ax1.text(i, v + 0.5, f'{v:.2f}%', ha='center')

    ax2 = axes[0, 1]
    won = results.get('won_trades', 0)
    lost = results.get('lost_trades', 0)
    if won + lost > 0:
        ax2.pie([won, lost], labels=['Won', 'Lost'], autopct='%1.1f%%',
                colors=['green', 'red'], explode=[0.05, 0])
        ax2.set_title(f'Win Rate: {results.get("win_rate", 0):.1f}%')
    else:
        ax2.text(0.5, 0.5, 'No Trades', ha='center', va='center')
        ax2.set_title('Trade Statistics')

    ax3 = axes[1, 0]
    sharpe = results.get('sharpe_ratio') or 0
    ax3.bar(['Sharpe Ratio'], [sharpe], color='steelblue')
    ax3.set_ylabel('Value')
    ax3.set_title('Risk-Adjusted Return')
    ax3.text(0, 0.01, f'{sharpe:.4f}' if sharpe else 'N/A', ha='center')

    ax4 = axes[1, 1]
    ax4.axis('off')
    info_text = f"""
    Initial Cash:    ¥{results.get('initial_cash', 0):,.0f}
    Final Value:     ¥{results.get('final_value', 0):,.0f}
    Total Trades:    {results.get('total_trades', 0)}
    Won Trades:      {results.get('won_trades', 0)}
    Lost Trades:     {results.get('lost_trades', 0)}
    """
    ax4.text(0.1, 0.5, info_text, fontsize=12, family='monospace',
              verticalalignment='center')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_portfolio(
    portfolio_values: List[float],
    dates: List[pd.Timestamp],
    title: str = "Portfolio Value",
    benchmark: Optional[pd.Series] = None,
    save_path: Optional[str] = None,
    show: bool = True
):
    """绘制投资组合价值曲线"""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(dates, portfolio_values, label='Portfolio', linewidth=2, color='blue')

    if benchmark is not None:
        benchmark_norm = benchmark / benchmark.iloc[0] * portfolio_values[0]
        ax.plot(dates, benchmark_norm, label='Benchmark', linewidth=1.5,
                color='gray', alpha=0.7)

    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Date')
    ax.set_ylabel('Value (¥)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    from data.fetcher import StockData
    from indicators import add_indicators

    sd = StockData()
    df = sd.get_a_stock('600519', '2024-01-01', '2024-12-31')
    df = add_indicators(df)

    print("绘制 K 线图...")
    plot_candle(df, title='Moutai 2024', save_path='/Users/mac2025/stock/chart.png')

    print("绘制带指标的 K 线图...")
    plot_candle_with_indicators(
        df.tail(60),
        indicators=['ma5', 'ma20'],
        title='Moutai with Indicators',
        save_path='/Users/mac2025/stock/chart2.png'
    )
    print("完成！")
