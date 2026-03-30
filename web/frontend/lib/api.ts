import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export const stockApi = {
  // 获取所有策略
  getStrategies: () => api.get('/api/strategies'),

  // 获取股票数据
  getStockData: (stockCode: string, startDate: string, endDate: string) =>
    api.post('/api/stock/data', { stock_code: stockCode, start_date: startDate, end_date: endDate }),

  // 获取 K 线图数据
  getChartData: (stockCode: string, startDate: string, endDate: string) =>
    api.post('/api/stock/chart-data', { stock_code: stockCode, start_date: startDate, end_date: endDate }),

  // 单个策略回测
  runBacktest: (stockCode: string, startDate: string, endDate: string, strategy: string, params = {}) =>
    api.post('/api/backtest', { stock_code: stockCode, start_date: startDate, end_date: endDate, strategy, params }),

  // 所有策略回测
  runAllBacktests: (stockCode: string, startDate: string, endDate: string) =>
    api.post('/api/backtest/all', { stock_code: stockCode, start_date: startDate, end_date: endDate }),

  // 多股票回测
  runMultiStock: (stockCodes: string[], startDate: string, endDate: string, strategy: string, params = {}) =>
    api.post('/api/backtest/multi', { stock_codes: stockCodes, start_date: startDate, end_date: endDate, strategy, params }),

  // ML 预测
  mlPredict: (stockCode: string, startDate: string, endDate: string) =>
    api.post('/api/ml/predict', { stock_code: stockCode, start_date: startDate, end_date: endDate }),
};

export default api;
