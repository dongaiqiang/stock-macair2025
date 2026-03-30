# 量化交易系统 - 使用手册

## 📖 目录

1. [快速开始](#快速开始)
2. [项目结构](#项目结构)
3. [功能模块](#功能模块)
4. [常见问题](#常见问题)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/mac2025/stock

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Web 后端依赖
pip install -r web/backend/requirements.txt

# 安装前端依赖
cd web/frontend
npm install
```

### 2. 三种使用方式

#### 方式一：命令行演示（推荐新手）

```bash
python demo.py
```

运行后将执行完整流程：
- 获取贵州茅台 (600519) 2023-2024 年数据
- 计算 37 个技术指标
- 回测 4 种传统策略
- 参数优化
- 机器学习预测
- 生成可视化图表

#### 方式二：Web 界面

```bash
# 终端 1 - 启动后端
cd web/backend
python main.py  # 运行在 http://localhost:8000

# 终端 2 - 启动前端
cd web/frontend
npm run dev  # 运行在 http://localhost:3000
```

然后访问 http://localhost:3000

#### 方式三：Python 脚本

```python
from data.fetcher import StockData
from backtest import run_backtest, MAStrategy

# 获取数据
sd = StockData()
df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

# 回测
result = run_backtest(df, MAStrategy, fast_period=5, slow_period=20)
print(f"收益率：{result['total_return']:+.2f}%")
```

---

## 📁 项目结构

```
stock/
├── data/               # 数据获取模块
│   ├── fetcher.py      # 股票数据获取（A 股/美股）
│   └── fundamental.py  # 基本面数据
├── indicators/         # 技术指标模块
│   └── indicators.py   # 10+ 种技术分析指标
├── backtest/           # 回测引擎
│   ├── engine.py       # Backtrader 封装
│   ├── strategies.py   # 7 种交易策略
│   ├── optimizer.py    # 参数优化
│   └── multi.py        # 多股票回测
├── ml/                 # 机器学习模块
│   ├── features.py     # 特征工程
│   ├── models.py       # 预测模型
│   └── trainer.py      # 模型训练
├── visualization/      # 可视化模块
│   └── charts.py       # K 线图/回测结果图
├── web/                # Web 应用
│   ├── backend/        # FastAPI 后端
│   └── frontend/       # Next.js 前端
├── demo.py             # 端到端演示脚本
└── requirements.txt    # Python 依赖
```

---

## 🔧 功能模块

### 1. 数据获取 (data/fetcher.py)

支持 A 股和美股数据：

```python
from data.fetcher import StockData

sd = StockData()

# A 股日线数据
df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

# A 股分钟线数据（5/15/30/60 分钟）
df_minute = sd.get_a_stock_minute('600519', '2024-01-01', '2024-01-31', frequency=5)

# 美股数据
df_us = sd.get_us_stock('AAPL', '2023-01-01', '2024-12-31')

# 自动识别市场
df = sd.get_stock('600519', '2023-01-01', '2024-12-31')  # A 股
df = sd.get_stock('AAPL', '2023-01-01', '2024-12-31')    # 美股
```

**数据列说明**：
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `amount`: 成交额

### 2. 技术指标 (indicators/indicators.py)

提供 10+ 种常用技术指标：

| 指标 | 函数 | 说明 |
|------|------|------|
| 移动平均 | `MA()`, `EMA()`, `WMA()` | 简单/指数/加权移动平均 |
| MACD | `MACD()` | 异同移动平均线 |
| RSI | `RSI()` | 相对强弱指标 |
| KDJ | `KDJ()` | 随机指标 |
| 布林带 | `BOLL()` | 布林带通道 |
| OBV | `OBV()` | 能量潮 |
| ATR | `ATR()` | 平均真实波幅 |
| ADX | `ADX()` | 平均趋向指数 |

**一键添加所有指标**：

```python
from indicators import add_indicators

df_with_indicators = add_indicators(df)
# 添加的列：ma5, ma10, ma20, ma60, ema12, ema26,
#          macd, macd_signal, macd_hist, rsi,
#          kdj_k, kdj_d, kdj_j,
#          boll_upper, boll_middle, boll_lower,
#          obv, atr, adx
```

### 3. 回测引擎 (backtest/)

#### 运行单个策略

```python
from backtest import run_backtest, MAStrategy

result = run_backtest(
    df,
    strategy=MAStrategy,
    fast_period=5,      # 快线周期
    slow_period=20,     # 慢线周期
    stop_loss=0.05,     # 止损 5%（可选）
    take_profit=0.10,   # 止盈 10%（可选）
    initial_cash=1000000,  # 初始资金 100 万
    commission=0.001    # 手续费千分之一
)

print(result)
# {
#     'final_value': 1234567,
#     'total_return': 23.45,
#     'max_drawdown': -8.32,
#     'total_trades': 45,
#     'win_rate': 62.2,
#     'sharpe_ratio': 1.35
# }
```

#### 多股票回测

```python
from backtest import run_multi_stock, MAStrategy

results = run_multi_stock(
    stocks=['600519', '000858', '601318'],
    start_date='2023-01-01',
    end_date='2024-12-31',
    strategy=MAStrategy,
    fast_period=5,
    slow_period=20
)

for stock, result in results.items():
    print(f"{stock}: {result['total_return']:+.2f}%")
```

### 4. 机器学习 (ml/)

```python
from ml.features import FeatureEngineer
from ml.models import StockPredictor

# 特征工程
fe = FeatureEngineer()
df_features = fe.create_features(df)

# 准备训练数据
X, y = fe.prepare_train_data(df_features)

# 训练模型
predictor = StockPredictor(model_type='lgbm')
train_result = predictor.train(X, y)
print(f"准确率：{train_result['accuracy']:.2%}")

# 获取特征重要性
importance = predictor.get_feature_importance()
print(importance.head(10))

# 回测 ML 策略
ml_result = predictor.backtest(df_features, initial_capital=1000000)
print(f"ML 策略收益率：{ml_result['total_return']:+.2f}%")
```

### 5. 可视化 (visualization/)

```python
from visualization import plot_candle_with_indicators, plot_backtest_results

# K 线图（含技术指标）
plot_candle_with_indicators(
    df.tail(60),
    indicators=['ma5', 'ma20', 'macd'],
    title='贵州茅台 K 线图',
    save_path='chart.png'
)

# 回测结果图
plot_backtest_results(result, save_path='backtest_result.png')
```

---

## ❓ 常见问题

### Q1: 获取数据失败？

**可能原因**：
- baostock 需要登录，确保网络畅通
- 股票代码格式不正确（A 股需 6 位数字）
- 日期范围超出数据可用范围

**解决方法**：
```python
# 检查股票代码格式
sd.get_a_stock('600519', ...)  # 正确，6 位数字
sd.get_a_stock('sh.600519', ...)  # 也可

# 检查日期范围
from datetime import datetime
print(datetime.now())  # 确保结束日期不超过今天
```

### Q2: 回测结果为空或交易次数为 0？

**可能原因**：
- 策略参数不适合该股票
- 数据时间范围太短
- 信号条件过于严格

**解决方法**：
```python
# 调整策略参数
result = run_backtest(df, MAStrategy, fast_period=3, slow_period=15)

# 延长数据时间
df = sd.get_a_stock('600519', '2022-01-01', '2024-12-31')
```

### Q3: Web 前端无法连接后端？

**可能原因**：
- 后端未启动
- 端口被占用
- CORS 问题

**解决方法**：
```bash
# 检查后端是否运行
curl http://localhost:8000

# 查看后端日志
cd web/backend
python main.py

# 检查前端配置
cat web/frontend/.env.example
# 确保 NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Q4: 机器学习准确率低？

**可能原因**：
- 特征不够丰富
- 模型参数需要调优
- 市场本身难以预测

**建议**：
```python
# 尝试不同模型
predictor = StockPredictor(model_type='rf')  # 随机森林
predictor = StockPredictor(model_type='lgbm')  # LightGBM（默认）

# 调整特征
fe = FeatureEngineer()
df_features = fe.create_features(df)  # 可自定义特征
```

---

## 📞 获取帮助

- API 文档：http://localhost:8000/docs
- 运行测试：`python demo.py`
- 查看日志：后端启动时会打印详细日志
