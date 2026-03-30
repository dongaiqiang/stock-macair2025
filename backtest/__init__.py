# backtest module
from .engine import BacktestEngine, run_backtest
from .strategies import (
    MAStrategy,
    RSIStrategy,
    BollStrategy,
    MACDStrategy,
    TurtleStrategy,
    MeanReversionStrategy,
    TailBreakoutStrategy,
)
from .optimizer import StrategyOptimizer, quick_optimize
from .multi import MultiStockBacktest, run_multi_stock

__all__ = [
    'BacktestEngine',
    'run_backtest',
    'MAStrategy',
    'RSIStrategy',
    'BollStrategy',
    'MACDStrategy',
    'TurtleStrategy',
    'MeanReversionStrategy',
    'TailBreakoutStrategy',
    'StrategyOptimizer',
    'quick_optimize',
    'MultiStockBacktest',
    'run_multi_stock',
]
