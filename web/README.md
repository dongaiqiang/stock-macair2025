# 量化交易系统 Web 应用

## 📚 文档导航

- [**使用手册**](../USAGE.md) - 系统安装和使用方法
- [**策略说明**](../STRATEGIES.md) - 7 种交易策略详细原理
- [**API 示例**](../API_EXAMPLES.md) - API 调用完整示例

## 项目结构

```
web/
├── backend/          # FastAPI 后端
│   ├── main.py       # API 服务
│   └── requirements.txt
└── frontend/         # Next.js 前端
    ├── app/
    ├── components/
    ├── lib/
    └── package.json
```

## 启动方法

### 1. 启动后端

```bash
cd /Users/mac2025/stock/web/backend
pip install -r requirements.txt
python main.py
```

后端将运行在 http://localhost:8000

### 2. 启动前端

```bash
cd /Users/mac2025/stock/web/frontend
npm install
npm run dev
```

前端将运行在 http://localhost:3000

## 功能

- 📈 K 线图展示（支持移动端触摸）
- 📊 7 种策略回测对比
- 📱 响应式设计，手机/平板/电脑适配
- 🤖 机器学习预测

## API 端点

- `GET /api/strategies` - 获取所有策略
- `POST /api/stock/data` - 获取股票数据
- `POST /api/stock/chart-data` - 获取 K 线图数据
- `POST /api/backtest` - 单个策略回测
- `POST /api/backtest/all` - 所有策略回测
- `POST /api/backtest/multi` - 多股票回测
- `POST /api/ml/predict` - 机器学习预测
