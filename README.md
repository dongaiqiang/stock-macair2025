# 量化交易系统

> 一站式股票策略回测与交易平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.1+-black.svg)](https://nextjs.org/)

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [**使用手册**](USAGE.md) | 系统安装、模块介绍、常见问题 |
| [**策略说明**](STRATEGIES.md) | 7 种交易策略的原理和使用 |
| [**API 示例**](API_EXAMPLES.md) | API 调用的完整示例代码 |

---

## 🚀 快速开始

### 30 秒体验

```bash
# 安装依赖
pip install -r requirements.txt

# 运行演示
python demo.py
```

运行后将生成：
- 回测结果（收益率、夏普比率、最大回撤）
- K 线图表（`chart.png`）
- 回测结果图（`backtest_result.png`）

---

## 🌐 Web 界面

### 启动服务

```bash
# 终端 1 - 后端
cd web/backend
pip install -r requirements.txt
python main.py
# 访问 http://localhost:8000/docs

# 终端 2 - 前端
cd web/frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

### 功能特性

- 📈 **K 线图**：交互式蜡烛图，支持缩放
- 📊 **策略对比**：7 种策略收益率排名
- 📱 **响应式**：手机/平板/电脑自适应
- 🤖 **ML 预测**：LightGBM 机器学习

---

## 📦 核心模块

| 模块 | 功能 |
|------|------|
| `data/` | A 股/美股数据获取（baostock、yfinance） |
| `indicators/` | 10+ 技术指标（MACD、RSI、KDJ、布林带等） |
| `backtest/` | 基于 Backtrader 的回测引擎 |
| `ml/` | LightGBM 机器学习预测 |
| `visualization/` | Plotly/matplotlib 可视化 |

---

## 📈 支持的策略

| 策略 | 类型 | 适合市场 |
|------|------|----------|
| 双均线 MA | 趋势跟踪 | 趋势市 |
| RSI 超买超卖 | 均值回归 | 震荡市 |
| 布林带突破 | 均值回归 | 震荡市 |
| MACD | 趋势跟踪 | 趋势市 |
| 海龟交易法 | 趋势跟踪 | 强趋势 |
| 均值回归 | 均值回归 | 震荡市 |
| 尾盘突破 | 短线套利 | 任意 |

详细策略说明见 [STRATEGIES.md](STRATEGIES.md)

---

## 🧪 使用示例

### Python 调用

```python
from data.fetcher import StockData
from backtest import run_backtest, MAStrategy

# 获取数据
sd = StockData()
df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

# 回测
result = run_backtest(
    df, MAStrategy,
    fast_period=5, slow_period=20,
    initial_cash=1000000
)

print(f"收益率：{result['total_return']:+.2f}%")
```

### API 调用

```bash
curl -X POST http://localhost:8000/api/backtest/all \
  -H "Content-Type: application/json" \
  -d '{"stock_code":"600519","start_date":"2023-01-01","end_date":"2024-12-31"}'
```

更多示例见 [API_EXAMPLES.md](API_EXAMPLES.md)

---

## 🛠️ 技术栈

**后端**
- Python 3.8+
- pandas / numpy
- Backtrader（回测）
- LightGBM / scikit-learn（ML）
- FastAPI（Web 后端）

**前端**
- Next.js 14
- React 18
- TypeScript
- lightweight-charts
- TailwindCSS

---

## 📁 项目结构

```
stock/
├── data/               # 数据获取
├── indicators/         # 技术指标
├── backtest/           # 回测引擎
├── ml/                 # 机器学习
├── visualization/      # 可视化
├── web/                # Web 应用
├── demo.py             # 演示脚本
├── USAGE.md            # 使用手册
├── STRATEGIES.md       # 策略说明
└── API_EXAMPLES.md     # API 示例
```

---

## ⚠️ 风险提示

1. **历史回测 ≠ 未来收益**：回测结果仅供参考
2. **过拟合风险**：参数过度优化可能导致实盘失效
3. **实盘差异**：实盘需考虑滑点、冲击成本等
4. **投资风险**：股市有风险，入市需谨慎

---

## 📝 更新日志

- ✅ 添加完整文档（使用手册、策略说明、API 示例）
- ✅ 7 种交易策略支持
- ✅ 机器学习预测功能
- ✅ Web 界面（前后端分离）
- ✅ 多股票回测
- ✅ 参数优化

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

**祝投资顺利！** 📈
