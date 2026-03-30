# API 使用示例

本文档提供量化交易系统 API 的完整使用示例，包括 Python 和 cURL 调用方式。

---

## 📡 API 概览

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/api/strategies` | GET | 获取策略列表 |
| `/api/stock/data` | POST | 获取股票数据 |
| `/api/stock/chart-data` | POST | 获取 K 线图数据 |
| `/api/backtest` | POST | 单策略回测 |
| `/api/backtest/all` | POST | 全部策略回测 |
| `/api/backtest/multi` | POST | 多股票回测 |
| `/api/ml/predict` | POST | ML 预测 |

**基础地址**：`http://localhost:8000`

---

## 1. 健康检查

### cURL

```bash
curl http://localhost:8000
```

### 响应

```json
{
  "message": "量化交易系统 API",
  "status": "running"
}
```

---

## 2. 获取策略列表

### cURL

```bash
curl http://localhost:8000/api/strategies
```

### Python

```python
import requests

response = requests.get('http://localhost:8000/api/strategies')
print(response.json())
```

### 响应

```json
{
  "strategies": [
    {"id": "ma", "name": "双均线策略", "description": "MA5/MA20 金叉死叉"},
    {"id": "rsi", "name": "RSI 超买超卖", "description": "RSI 指标策略"},
    {"id": "boll", "name": "布林带突破", "description": "Bollinger Bands"},
    {"id": "macd", "name": "MACD 金叉死叉", "description": "MACD 指标"},
    {"id": "turtle", "name": "海龟交易法", "description": "Turtle Trading"},
    {"id": "mean_reversion", "name": "均值回归", "description": "Mean Reversion"},
    {"id": "tail_breakout", "name": "尾盘突破", "description": "Tail Breakout"}
  ]
}
```

---

## 3. 获取股票数据

### cURL

```bash
curl -X POST http://localhost:8000/api/stock/data \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### Python

```python
import requests

data = {
    'stock_code': '600519',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31'
}

response = requests.post('http://localhost:8000/api/stock/data', json=data)
result = response.json()

# 打印前 5 条数据
for row in result['data'][:5]:
    print(f"{row['date']}: 开={row['open']}, 收={row['close']}, 高={row['high']}, 低={row['low']}")
```

### 响应

```json
{
  "stock_code": "600519",
  "count": 245,
  "data": [
    {
      "date": "2024-01-02",
      "open": 1650.00,
      "high": 1680.50,
      "low": 1645.00,
      "close": 1675.20,
      "volume": 1234567
    },
    ...
  ]
}
```

---

## 4. 获取 K 线图数据（含技术指标）

### cURL

```bash
curl -X POST http://localhost:8000/api/stock/chart-data \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### Python

```python
import requests

data = {
    'stock_code': '600519',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31'
}

response = requests.post('http://localhost:8000/api/stock/chart-data', json=data)
result = response.json()

# 提取 K 线和均线数据
for row in result['data']:
    print(f"{row['date']}: 收盘={row['close']}, MA5={row.get('ma5', 'N/A')}")
```

### 响应

```json
{
  "stock_code": "600519",
  "data": [
    {
      "date": "2024-01-02",
      "open": 1650.00,
      "high": 1680.50,
      "low": 1645.00,
      "close": 1675.20,
      "volume": 1234567,
      "ma5": 1660.50,
      "ma10": 1655.30,
      "ma20": 1640.80,
      "macd": 12.5,
      "rsi": 55.3
    },
    ...
  ]
}
```

---

## 5. 单个策略回测

### cURL

```bash
curl -X POST http://localhost:8000/api/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "strategy": "ma",
    "params": {
      "fast_period": 5,
      "slow_period": 20
    }
  }'
```

### Python

```python
import requests

data = {
    'stock_code': '600519',
    'start_date': '2023-01-01',
    'end_date': '2024-12-31',
    'strategy': 'ma',
    'params': {
        'fast_period': 5,
        'slow_period': 20
    }
}

response = requests.post('http://localhost:8000/api/backtest', json=data)
result = response.json()

print(f"策略：{result['strategy']}")
print(f"最终资金：¥{result['results']['final_value']:,.0f}")
print(f"收益率：{result['results']['total_return']:+.2f}%")
print(f"最大回撤：{result['results']['max_drawdown']:.2f}%")
print(f"交易次数：{result['results']['total_trades']}")
print(f"胜率：{result['results']['win_rate']:.1f}%")
```

### 响应

```json
{
  "stock_code": "600519",
  "strategy": "ma",
  "params": {"fast_period": 5, "slow_period": 20},
  "results": {
    "final_value": 1234567.89,
    "total_return": 23.45,
    "max_drawdown": -8.32,
    "total_trades": 45,
    "win_rate": 62.2,
    "sharpe_ratio": 1.35
  }
}
```

---

## 6. 全部策略回测对比

### cURL

```bash
curl -X POST http://localhost:8000/api/backtest/all \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "start_date": "2023-01-01",
    "end_date": "2024-12-31"
  }'
```

### Python

```python
import requests

data = {
    'stock_code': '600519',
    'start_date': '2023-01-01',
    'end_date': '2024-12-31'
}

response = requests.post('http://localhost:8000/api/backtest/all', json=data)
result = response.json()

print("策略回测对比（按收益率排序）:")
print("-" * 60)
for r in result['results']:
    if 'error' in r:
        print(f"{r['strategy']}: 错误 - {r['error']}")
    else:
        print(f"{r['strategy']:15} 收益率:{r['total_return']:7.2f}%  "
              f"回撤:{r['max_drawdown']:7.2f}%  "
              f"交易:{r['total_trades']:3}次  "
              f"胜率:{r['win_rate']:5.1f}%")
```

### 响应

```json
{
  "stock_code": "600519",
  "results": [
    {
      "strategy": "ma",
      "total_return": 23.45,
      "max_drawdown": -8.32,
      "total_trades": 45,
      "win_rate": 62.2,
      "final_value": 1234567
    },
    {
      "strategy": "rsi",
      "total_return": 15.30,
      "max_drawdown": -5.20,
      "total_trades": 68,
      "win_rate": 58.8,
      "final_value": 1153000
    },
    ...
  ]
}
```

---

## 7. 多股票回测

### cURL

```bash
curl -X POST http://localhost:8000/api/backtest/multi \
  -H "Content-Type: application/json" \
  -d '{
    "stock_codes": ["600519", "000858", "601318"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "strategy": "ma",
    "params": {
      "fast_period": 5,
      "slow_period": 20
    }
  }'
```

### Python

```python
import requests

data = {
    'stock_codes': ['600519', '000858', '601318'],
    'start_date': '2023-01-01',
    'end_date': '2024-12-31',
    'strategy': 'ma',
    'params': {'fast_period': 5, 'slow_period': 20}
}

response = requests.post('http://localhost:8000/api/backtest/multi', json=data)
result = response.json()

print(f"策略：{result['strategy']}")
print("多股票回测结果:")
for code, res in result['results'].items():
    print(f"  {code}: 收益率 {res['total_return']:+.2f}%, "
          f"回撤 {res['max_drawdown']:.2f}%, "
          f"胜率 {res['win_rate']:.1f}%")
```

### 响应

```json
{
  "strategy": "ma",
  "results": {
    "600519": {
      "total_return": 23.45,
      "max_drawdown": -8.32,
      "total_trades": 45,
      "win_rate": 62.2
    },
    "000858": {
      "total_return": 18.20,
      "max_drawdown": -10.50,
      "total_trades": 38,
      "win_rate": 55.3
    },
    "601318": {
      "total_return": 12.80,
      "max_drawdown": -6.40,
      "total_trades": 52,
      "win_rate": 59.6
    }
  }
}
```

---

## 8. 机器学习预测

### cURL

```bash
curl -X POST http://localhost:8000/api/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "600519",
    "start_date": "2023-01-01",
    "end_date": "2024-12-31"
  }'
```

### Python

```python
import requests

data = {
    'stock_code': '600519',
    'start_date': '2023-01-01',
    'end_date': '2024-12-31'
}

response = requests.post('http://localhost:8000/api/ml/predict', json=data)
result = response.json()

print(f"股票：{result['stock_code']}")
print(f"模型准确率：{result['model_accuracy']:.2%}")
print(f"ML 策略收益率：{result['backtest']['total_return']:+.2f}%")
print(f"交易次数：{result['backtest']['total_trades']}")
print(f"胜率：{result['backtest']['win_rate']:.1f}%")
```

### 响应

```json
{
  "stock_code": "600519",
  "model_accuracy": 0.58,
  "feature_importance": [
    {"feature": "rsi", "importance": 0.15},
    {"feature": "macd_hist", "importance": 0.12},
    ...
  ],
  "backtest": {
    "total_return": 28.50,
    "total_trades": 35,
    "win_rate": 65.7
  }
}
```

---

## 🧩 完整示例：Python 脚本

### 策略对比分析脚本

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
策略对比分析脚本
"""

import requests
import json

API_BASE = 'http://localhost:8000'

def analyze_stock(stock_code: str, start_date: str, end_date: str):
    """分析单只股票"""
    print(f"\n{'='*60}")
    print(f"分析股票：{stock_code} ({start_date} 至 {end_date})")
    print('='*60)

    # 1. 获取股票数据
    print("\n[1] 获取股票数据...")
    resp = requests.post(f'{API_BASE}/api/stock/data', json={
        'stock_code': stock_code,
        'start_date': start_date,
        'end_date': end_date
    })
    if resp.status_code == 200:
        data = resp.json()
        print(f"    数据条数：{data['count']}")
    else:
        print(f"    获取失败：{resp.text}")
        return

    # 2. 全部策略回测
    print("\n[2] 运行全部策略回测...")
    resp = requests.post(f'{API_BASE}/api/backtest/all', json={
        'stock_code': stock_code,
        'start_date': start_date,
        'end_date': end_date
    })
    if resp.status_code == 200:
        results = resp.json()['results']

        print("\n    策略排名（按收益率）:")
        print("-" * 70)
        print(f"{'排名':<4} {'策略':<15} {'收益率':<10} {'回撤':<10} {'胜率':<8} {'交易次数'}")
        print("-" * 70)

        for i, r in enumerate(results, 1):
            if 'error' not in r:
                print(f"{i:<4} {r['strategy']:<15} {r['total_return']:>8.2f}%  "
                      f"{r['max_drawdown']:>8.2f}%  "
                      f"{r['win_rate']:>6.1f}%  "
                      f"{r['total_trades']:>6}")

        # 找出最佳策略
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            best = max(valid_results, key=lambda x: x['total_return'])
            print(f"\n    ⭐ 最佳策略：{best['strategy']} "
                  f"(收益率 {best['total_return']:+.2f}%)")
    else:
        print(f"    回测失败：{resp.text}")

    # 3. 机器学习预测
    print("\n[3] 机器学习预测...")
    resp = requests.post(f'{API_BASE}/api/ml/predict', json={
        'stock_code': stock_code,
        'start_date': start_date,
        'end_date': end_date
    })
    if resp.status_code == 200:
        result = resp.json()
        print(f"    模型准确率：{result['model_accuracy']:.2%}")
        print(f"    ML 策略收益：{result['backtest']['total_return']:+.2f}%")
    else:
        print(f"    预测失败：{resp.text}")

def main():
    """主函数"""
    stocks = [
        ('600519', '贵州茅台'),
        ('000858', '五粮液'),
        ('601318', '中国平安'),
    ]

    for code, name in stocks:
        analyze_stock(code, '2023-01-01', '2024-12-31')

    print(f"\n{'='*60}")
    print("分析完成!")

if __name__ == '__main__':
    main()
```

---

## 🔧 错误处理

### 常见错误码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |

### Python 错误处理示例

```python
import requests

try:
    response = requests.post('http://localhost:8000/api/backtest', json=data)
    response.raise_for_status()  # 检查 HTTP 错误
    result = response.json()

    if 'error' in result:
        print(f"API 返回错误：{result['error']}")
    else:
        print(f"回测成功：{result['results']}")

except requests.exceptions.ConnectionError:
    print("错误：无法连接到服务器，请确保后端已启动")
except requests.exceptions.Timeout:
    print("错误：请求超时")
except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误：{e}")
    print(f"详情：{response.text}")
except Exception as e:
    print(f"未知错误：{e}")
```

---

## 📚 相关文档

- [使用手册](USAGE.md) - 系统安装和使用方法
- [策略说明](STRATEGIES.md) - 各策略详细原理
