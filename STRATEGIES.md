# 交易策略说明文档

本文档详细介绍系统支持的 7 种交易策略，包括策略原理、适用场景、参数说明和实战建议。

---

## 📊 策略总览

| 策略 | 类型 | 风险 | 收益潜力 | 适合市场 |
|------|------|------|----------|----------|
| 双均线 MA | 趋势跟踪 | 中 | 中 | 趋势市 |
| RSI 超买超卖 | 均值回归 | 低 | 低 | 震荡市 |
| 布林带突破 | 均值回归 | 中 | 中 | 震荡市 |
| MACD | 趋势跟踪 | 中 | 中 | 趋势市 |
| 海龟交易法 | 趋势跟踪 | 高 | 高 | 强趋势 |
| 均值回归 | 均值回归 | 低 | 低 | 震荡市 |
| 尾盘突破 | 短线套利 | 中 | 中 | 任意 |

---

## 1. 双均线策略 (MAStrategy)

### 策略原理

使用两条不同周期的移动平均线：
- **快线**（如 5 日）：对价格变化更敏感
- **慢线**（如 20 日）：反映长期趋势

**买入信号**：快线上穿慢线（金叉）
**卖出信号**：快线下穿慢线（死叉）

### 代码示例

```python
from backtest import run_backtest, MAStrategy

result = run_backtest(
    df,
    strategy=MAStrategy,
    fast_period=5,      # 快线周期
    slow_period=20,     # 慢线周期
    stop_loss=0.05,     # 止损 5%（可选）
    take_profit=0.10,   # 止盈 10%（可选）
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `fast_period` | 5 | 快线周期 | 3-10，越小越敏感 |
| `slow_period` | 20 | 慢线周期 | 10-60，越大越稳定 |
| `stop_loss` | 0 | 止损比例 | 0.03-0.08 |
| `take_profit` | 0 | 止盈比例 | 0.08-0.20 |

### 适用场景

✅ **适合**：趋势明显的股票（如成长股、周期股）
❌ **不适合**：横盘震荡的股票

### 实战建议

1. **参数优化**：不同股票适合的周期不同，建议用 `StrategyOptimizer` 优化
2. **配合止损**：趋势策略容易出现大回撤，建议设置止损
3. **结合大盘**：大盘向上时成功率更高

---

## 2. RSI 超买超卖策略 (RSIStrategy)

### 策略原理

RSI（相对强弱指标）衡量价格变动速度和幅度：
- **RSI < 30**：超卖区，可能反弹 → **买入**
- **RSI > 70**：超买区，可能回调 → **卖出**

### 代码示例

```python
from backtest import run_backtest, RSIStrategy

result = run_backtest(
    df,
    strategy=RSIStrategy,
    rsi_period=14,      # RSI 计算周期
    rsi_upper=70,       # 超买阈值
    rsi_lower=30,       # 超卖阈值
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `rsi_period` | 14 | RSI 周期 | 7-21，越小越敏感 |
| `rsi_upper` | 70 | 超买阈值 | 65-80 |
| `rsi_lower` | 30 | 超卖阈值 | 20-35 |

### 适用场景

✅ **适合**：震荡市、波动稳定的股票
❌ **不适合**：单边上涨或下跌的极端行情

### 实战建议

1. **阈值调整**：强势股可调高阈值（如 80/20）
2. **配合趋势**：只在上升趋势中做超卖买入
3. **快进快出**：该策略适合短线，不宜久持

---

## 3. 布林带突破策略 (BollStrategy)

### 策略原理

布林带由三条线组成：
- **上轨**：中轨 + 2 倍标准差
- **中轨**：20 日简单移动平均
- **下轨**：中轨 - 2 倍标准差

**买入信号**：价格跌破下轨（超卖）
**卖出信号**：价格突破上轨（超买）

### 代码示例

```python
from backtest import run_backtest, BollStrategy

result = run_backtest(
    df,
    strategy=BollStrategy,
    period=20,          # 布林带周期
    devfactor=2.0,      # 标准差倍数
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `period` | 20 | 计算周期 | 15-30 |
| `devfactor` | 2.0 | 标准差倍数 | 1.5-2.5，越小信号越多 |

### 适用场景

✅ **适合**：震荡行情、波动率稳定的股票
❌ **不适合**：趋势性极强的行情（容易持续贴轨）

### 实战建议

1. **带宽判断**：布林带收窄后突破，往往是趋势起点
2. **配合成交量**：突破时放量更可靠
3. **注意假突破**：可结合其他指标确认

---

## 4. MACD 策略 (MACDStrategy)

### 策略原理

MACD 由三部分组成：
- **MACD 线**：快 EMA(12) - 慢 EMA(26)
- **信号线**：MACD 的 9 日 EMA
- **柱状图**：MACD 线 - 信号线

**买入信号**：MACD 线上穿信号线（金叉）
**卖出信号**：MACD 线下穿信号线（死叉）

### 代码示例

```python
from backtest import run_backtest, MACDStrategy

result = run_backtest(
    df,
    strategy=MACDStrategy,
    fast=12,            # 快线周期
    slow=26,            # 慢线周期
    signal=9,           # 信号线周期
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `fast` | 12 | 快 EMA 周期 | 8-16 |
| `slow` | 26 | 慢 EMA 周期 | 20-40 |
| `signal` | 9 | 信号线周期 | 7-12 |

### 适用场景

✅ **适合**：趋势行情、中大周期
❌ **不适合**：短线高频交易

### 实战建议

1. **背离信号**：价格新高但 MACD 不新高，可能见顶
2. **零轴判断**：零轴上方金叉更可靠
3. **配合大盘**：与大盘同向时成功率更高

---

## 5. 海龟交易法 (TurtleStrategy)

### 策略原理

经典的趋势跟踪策略：
- **买入**：价格突破过去 N 日最高价
- **卖出**：价格跌破过去 M 日最低价

核心思想：让利润奔跑，截断亏损

### 代码示例

```python
from backtest import run_backtest, TurtleStrategy

result = run_backtest(
    df,
    strategy=TurtleStrategy,
    entry_period=20,    # 突破买入周期
    exit_period=10,     # 跌破卖出周期
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `entry_period` | 20 | 突破周期 | 15-55，经典值为 20/55 |
| `exit_period` | 10 | 退出周期 | 5-20 |

### 适用场景

✅ **适合**：强趋势行情、期货、高波动品种
❌ **不适合**：震荡市（会频繁止损）

### 实战建议

1. **严格止损**：该策略胜率不高，需要严格止损
2. **仓位管理**：建议配合 ATR 动态仓位
3. **耐心持有**：趋势来了要拿得住

---

## 6. 均值回归策略 (MeanReversionStrategy)

### 策略原理

基于统计学均值回归理论：
- 价格偏离均值过远时，倾向于回归
- **买入**：价格跌破布林带下轨
- **卖出**：价格回升至布林带上轨

### 代码示例

```python
from backtest import run_backtest, MeanReversionStrategy

result = run_backtest(
    df,
    strategy=MeanReversionStrategy,
    period=20,          # 均值周期
    std_dev=2.0,        # 标准差阈值
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `period` | 20 | 计算周期 | 15-30 |
| `std_dev` | 2.0 | 标准差阈值 | 1.5-3.0 |

### 适用场景

✅ **适合**：震荡市、蓝筹股
❌ **不适合**：趋势股、问题股

### 实战建议

1. **选股重要**：选择基本面稳定、波动有规律的股票
2. **及时止盈**：回归后及时离场
3. **避开黑天鹅**：基本面恶化的股票不适用

---

## 7. 尾盘突破策略 (TailBreakoutStrategy)

### 策略原理

短线套利策略：
- **买入条件**：收盘价突破 N 日最高价的一定比例
- **卖出条件**：次日开盘卖出（持有 1 天）

核心逻辑：尾盘强势突破，次日惯性冲高

### 代码示例

```python
from backtest import run_backtest, TailBreakoutStrategy

result = run_backtest(
    df,
    strategy=TailBreakoutStrategy,
    lookback=20,        # 回顾天数
    breakout_rate=0.98, # 突破阈值
)
```

### 参数说明

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `lookback` | 20 | 回顾周期 | 10-30 |
| `breakout_rate` | 0.98 | 突破阈值 | 0.95-1.00 |

### 适用场景

✅ **适合**：T+1 市场、短线交易
❌ **不适合**：T+0 市场（需调整逻辑）

### 实战建议

1. **成功率**：该策略胜率约 50-60%，需要配合盈亏比
2. **选股**：选择活跃、有题材的股票
3. **大盘配合**：大盘向上时成功率更高

---

## 🎯 策略选择指南

### 根据市场行情选择

| 市场环境 | 推荐策略 | 仓位建议 |
|----------|----------|----------|
| 牛市上涨 | 双均线、MACD、海龟 | 70-100% |
| 熊市下跌 | 空仓或轻仓 RSI | 0-30% |
| 震荡市 | RSI、布林带、均值回归 | 50-70% |
| 趋势不明 | 尾盘突破（短线） | 30-50% |

### 根据股票类型选择

| 股票类型 | 特征 | 推荐策略 |
|----------|------|----------|
| 成长股 | 趋势性强 | 双均线、MACD、海龟 |
| 蓝筹股 | 波动稳定 | RSI、布林带、均值回归 |
| 题材股 | 波动大 | 尾盘突破、双均线 |
| 周期股 | 周期明显 | 双均线、MACD |

### 根据风险偏好选择

| 风险偏好 | 推荐策略 | 预期年化 | 最大回撤 |
|----------|----------|----------|----------|
| 保守型 | RSI、均值回归 | 10-20% | <15% |
| 稳健型 | 双均线、布林带 | 20-40% | <25% |
| 激进型 | 海龟、尾盘突破 | 40%+ | <40% |

---

## 🔧 策略优化技巧

### 1. 参数优化

```python
from backtest import StrategyOptimizer

optimizer = StrategyOptimizer()

# 优化双均线参数
results = optimizer.optimize_ma(
    df,
    fast_range=(3, 8),      # 快线 3-8 日
    slow_range=(10, 25)     # 慢线 10-25 日
)

print(results.head(5))  # 显示 Top5 参数组合
```

### 2. 多策略组合

```python
# 同时运行多个策略
strategies = ['ma', 'rsi', 'boll', 'macd']
results = {}

for strat_name in strategies:
    result = run_backtest(df, STRATEGY_MAP[strat_name])
    results[strat_name] = result['total_return']

# 选择最佳策略
best = max(results, key=results.get)
print(f"最佳策略：{best}, 收益率：{results[best]}")
```

### 3. 机器学习增强

```python
from ml.features import FeatureEngineer
from ml.models import StockPredictor

# 用 ML 预测信号辅助决策
fe = FeatureEngineer()
df_features = fe.create_features(df)

predictor = StockPredictor(model_type='lgbm')
# ML 预测 + 传统策略信号 = 综合判断
```

---

## ⚠️ 风险提示

1. **历史回测 ≠ 未来收益**：回测结果仅供参考
2. **过拟合风险**：参数过度优化可能导致实盘失效
3. **交易成本**：实盘需考虑冲击成本、滑点等
4. **黑天鹅事件**：极端行情下所有策略可能失效

**建议**：小资金实盘验证后再逐步加大投入
