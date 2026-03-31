#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
量化交易系统 - FastAPI 后端

性能优化:
- 添加请求缓存 (lru_cache)
- 添加响应时间日志
- 支持异步处理
"""

import sys
import os
import traceback
import time
import logging
from functools import lru_cache

# 添加项目根目录到路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
import pandas as pd
import numpy as np

from data.fetcher import StockData
from indicators import add_indicators, clean_data
from backtest import (
    run_backtest, MAStrategy, RSIStrategy, BollStrategy,
    MACDStrategy, TurtleStrategy, MeanReversionStrategy, TailBreakoutStrategy
)
from ml.features import FeatureEngineer
from ml.models import StockPredictor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="量化交易系统 API")

# 允许 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 性能优化：请求计时中间件 ============

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加响应时间头的中间件"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.3f}s")
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response


# ============ 数据模型 ============

class StockRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str


class BacktestRequest(BaseModel):
    stock_code: str
    start_date: str
    end_date: str
    strategy: str
    params: Optional[Dict[str, Any]] = {}


class MultiStockRequest(BaseModel):
    stock_codes: List[str]
    start_date: str
    end_date: str
    strategy: str
    params: Optional[Dict[str, Any]] = {}


# ============ 策略映射 ============

STRATEGY_MAP = {
    'ma': MAStrategy,
    'rsi': RSIStrategy,
    'boll': BollStrategy,
    'macd': MACDStrategy,
    'turtle': TurtleStrategy,
    'mean_reversion': MeanReversionStrategy,
    'tail_breakout': TailBreakoutStrategy,
}


# ============ 缓存配置 ============

# 股票数据缓存 - 缓存最近请求的股票数据
# 注意：实际生产环境应该使用 Redis 或其他分布式缓存
_stock_data_cache: Dict[str, Tuple[pd.DataFrame, float]] = {}
_CACHE_TTL = 300  # 缓存过期时间 (秒)


def get_cached_stock_data(code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """获取缓存的股票数据"""
    cache_key = f"{code}_{start_date}_{end_date}"
    current_time = time.time()

    if cache_key in _stock_data_cache:
        df, cache_time = _stock_data_cache[cache_key]
        if current_time - cache_time < _CACHE_TTL:
            logger.debug(f"Cache hit for {cache_key}")
            return df
        else:
            del _stock_data_cache[cache_key]
    return None


def set_cached_stock_data(code: str, start_date: str, end_date: str, df: pd.DataFrame):
    """设置缓存的股票数据"""
    cache_key = f"{code}_{start_date}_{end_date}"
    _stock_data_cache[cache_key] = (df, time.time())
    logger.debug(f"Cached data for {cache_key}")


def clear_cache():
    """清空缓存"""
    _stock_data_cache.clear()
    logger.info("Cache cleared")


# ============ API 端点 ============

@app.get("/")
def read_root():
    return {"message": "量化交易系统 API", "status": "running"}


@app.get("/api/strategies")
def get_strategies():
    """获取所有可用策略"""
    return {
        "strategies": [
            {"id": "ma", "name": "双均线策略", "description": "MA5/MA20 金叉死叉"},
            {"id": "rsi", "name": "RSI 超买超卖", "description": "RSI 指标策略"},
            {"id": "boll", "name": "布林带突破", "description": "Bollinger Bands"},
            {"id": "macd", "name": "MACD 金叉死叉", "description": "MACD 指标"},
            {"id": "turtle", "name": "海龟交易法", "description": "Turtle Trading"},
            {"id": "mean_reversion", "name": "均值回归", "description": "Mean Reversion"},
            {"id": "tail_breakout", "name": "尾盘突破", "description": "Tail Breakout"},
        ]
    }


@app.post("/api/stock/data")
async def get_stock_data(request: StockRequest):
    """获取股票数据"""
    try:
        # 尝试从缓存获取
        df = get_cached_stock_data(request.stock_code, request.start_date, request.end_date)

        if df is None:
            sd = StockData()
            df = sd.get_a_stock(request.stock_code, request.start_date, request.end_date)
            # 缓存数据
            set_cached_stock_data(request.stock_code, request.start_date, request.end_date, df)
        else:
            logger.info(f"Cache hit for {request.stock_code}")

        # 转换为 JSON 格式
        df_reset = df.reset_index()
        df_reset['date'] = df_reset['date'].dt.strftime('%Y-%m-%d')

        return {
            "stock_code": request.stock_code,
            "count": len(df),
            "data": df_reset.tail(100).to_dict('records')  # 只返回最近 100 条
        }
    except Exception as e:
        logger.error(f"Error getting stock data: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/stock/chart-data")
async def get_chart_data(request: StockRequest):
    """获取 K 线图数据（含技术指标）"""
    try:
        logger.info(f"收到请求：stock_code={request.stock_code}, start_date={request.start_date}, end_date={request.end_date}")

        # 尝试从缓存获取
        df = get_cached_stock_data(request.stock_code, request.start_date, request.end_date)

        if df is None:
            sd = StockData()
            df = sd.get_a_stock(request.stock_code, request.start_date, request.end_date)
            set_cached_stock_data(request.stock_code, request.start_date, request.end_date, df)
            logger.info(f"Fetched new data for {request.stock_code}: {len(df)} rows")
        else:
            logger.info(f"Cache hit for {request.stock_code}")

        # 添加技术指标
        df_with_indicators = add_indicators(df)

        # 转换为 JSON 格式
        df_reset = df_with_indicators.reset_index()
        df_reset['date'] = df_reset['date'].dt.strftime('%Y-%m-%d')

        # 选择关键字段
        columns = ['date', 'open', 'high', 'low', 'close', 'volume',
                   'ma5', 'ma10', 'ma20', 'macd', 'signal', 'rsi']
        available_cols = [c for c in columns if c in df_reset.columns]

        # 处理 nan 和 inf 值 - 使用更健壮的方式
        df_result = df_reset[available_cols].tail(100).copy()

        # 替换 inf/-inf 为 np.nan
        df_result = df_result.replace([np.inf, -np.inf], np.nan)

        # 将所有 NaN 替换为 None (JSON 兼容)
        for col in df_result.columns:
            if df_result[col].dtype == 'object':
                continue
            df_result[col] = df_result[col].where(df_result[col].notna(), None)

        return {
            "stock_code": request.stock_code,
            "data": df_result.to_dict('records')
        }
    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/backtest")
async def run_single_backtest(request: BacktestRequest):
    """运行单个策略回测"""
    try:
        # 尝试从缓存获取
        df = get_cached_stock_data(request.stock_code, request.start_date, request.end_date)

        if df is None:
            sd = StockData()
            df = sd.get_a_stock(request.stock_code, request.start_date, request.end_date)
            set_cached_stock_data(request.stock_code, request.start_date, request.end_date, df)

        strategy_cls = STRATEGY_MAP.get(request.strategy)
        if not strategy_cls:
            raise HTTPException(status_code=400, detail=f"未知策略：{request.strategy}")

        params = request.params or {}
        results = run_backtest(
            df,
            strategy=strategy_cls,
            initial_cash=1000000,
            commission=0.001,
            **params
        )

        logger.info(f"Backtest {request.strategy} for {request.stock_code}: return={results.get('total_return', 0):.2f}%")

        # 处理买卖点数据
        trades_log = results.get('trades_log', [])
        markers = []
        for trade in trades_log:
            markers.append({
                'time': trade['time'],
                'price': trade['price'],
                'type': 'buy'
            })
            if 'sell_time' in trade:
                markers.append({
                    'time': trade['sell_time'],
                    'price': trade['sell_price'],
                    'type': 'sell'
                })

        return {
            "stock_code": request.stock_code,
            "strategy": request.strategy,
            "params": params,
            "results": {
                "final_value": results.get('final_value', 0),
                "total_return": results.get('total_return', 0),
                "max_drawdown": results.get('max_drawdown', 0),
                "total_trades": results.get('total_trades', 0),
                "win_rate": results.get('win_rate', 0),
                "sharpe_ratio": results.get('sharpe_ratio'),
            },
            "markers": markers,
        }
    except Exception as e:
        logger.error(f"Error running backtest: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/backtest/all")
async def run_all_strategies(request: StockRequest):
    """运行所有策略回测"""
    try:
        # 尝试从缓存获取
        df = get_cached_stock_data(request.stock_code, request.start_date, request.end_date)

        if df is None:
            sd = StockData()
            df = sd.get_a_stock(request.stock_code, request.start_date, request.end_date)
            set_cached_stock_data(request.stock_code, request.start_date, request.end_date, df)

        results_list = []
        for strategy_id, strategy_cls in STRATEGY_MAP.items():
            try:
                results = run_backtest(
                    df,
                    strategy=strategy_cls,
                    initial_cash=1000000,
                    commission=0.001,
                )
                results_list.append({
                    "strategy": strategy_id,
                    "total_return": results.get('total_return', 0),
                    "max_drawdown": results.get('max_drawdown', 0),
                    "total_trades": results.get('total_trades', 0),
                    "win_rate": results.get('win_rate', 0),
                    "final_value": results.get('final_value', 0),
                })
                logger.info(f"Strategy {strategy_id}: return={results.get('total_return', 0):.2f}%")
            except Exception as e:
                logger.error(f"Strategy {strategy_id} failed: {e}")
                results_list.append({
                    "strategy": strategy_id,
                    "error": str(e)
                })

        # 按收益率排序
        results_list.sort(key=lambda x: x.get('total_return', 0), reverse=True)

        return {
            "stock_code": request.stock_code,
            "results": results_list
        }
    except Exception as e:
        logger.error(f"Error running all strategies: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/backtest/multi")
async def run_multi_stock_backtest(request: MultiStockRequest):
    """运行多股票回测"""
    try:
        from backtest import run_multi_stock

        strategy_cls = STRATEGY_MAP.get(request.strategy)
        if not strategy_cls:
            raise HTTPException(status_code=400, detail=f"未知策略：{request.strategy}")

        params = request.params or {}
        results = run_multi_stock(
            stocks=request.stock_codes,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy=strategy_cls,
            **params
        )

        formatted_results = {}
        for code, result in results.items():
            formatted_results[code] = {
                "total_return": result.get('total_return', 0),
                "max_drawdown": result.get('max_drawdown', 0),
                "total_trades": result.get('total_trades', 0),
                "win_rate": result.get('win_rate', 0),
            }

        logger.info(f"Multi-stock backtest for {len(request.stock_codes)} stocks completed")

        return {
            "strategy": request.strategy,
            "results": formatted_results
        }
    except Exception as e:
        logger.error(f"Error running multi-stock backtest: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ml/predict")
async def ml_predict(request: StockRequest):
    """机器学习预测"""
    try:
        # 尝试从缓存获取
        df = get_cached_stock_data(request.stock_code, request.start_date, request.end_date)

        if df is None:
            sd = StockData()
            df = sd.get_a_stock(request.stock_code, request.start_date, request.end_date)
            set_cached_stock_data(request.stock_code, request.start_date, request.end_date, df)

        df_with_indicators = add_indicators(df)

        # 特征工程
        fe = FeatureEngineer()
        df_features = fe.create_features(df_with_indicators)

        # 准备数据
        X, y = fe.prepare_train_data(df_features)

        # 训练模型
        predictor = StockPredictor(model_type='lgbm')
        train_results = predictor.train(X, y)

        # ML 策略回测
        ml_backtest = predictor.backtest(df_features, initial_capital=1000000, position_size=0.1)

        logger.info(f"ML prediction for {request.stock_code}: accuracy={train_results.get('accuracy', 0):.4f}")

        return {
            "stock_code": request.stock_code,
            "model_accuracy": train_results.get('accuracy', 0),
            "feature_importance": train_results.get('feature_importance', [])[:10],
            "backtest": {
                "total_return": ml_backtest.get('total_return', 0) if not pd.isna(ml_backtest.get('total_return')) else 0,
                "total_trades": ml_backtest.get('total_trades', 0),
                "win_rate": ml_backtest.get('win_rate', 0) if ml_backtest.get('win_rate') else 0,
            }
        }
    except Exception as e:
        logger.error(f"Error in ML prediction: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
