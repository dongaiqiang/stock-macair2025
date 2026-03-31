'use client';

import { useState } from 'react';
import { stockApi } from '@/lib/api';
import CandlestickChart from '@/components/CandlestickChart';
import StrategyCard from '@/components/StrategyCard';
import StrategyParamsForm, { strategyNames } from '@/components/StrategyParamsForm';
import StrategyComparisonChart from '@/components/StrategyComparisonChart';

interface BacktestResult {
  strategy: string;
  total_return: number;
  max_drawdown: number;
  total_trades: number;
  win_rate: number;
  final_value: number;
}

interface ChartData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface TradeMarker {
  time: string;
  price: number;
  type: 'buy' | 'sell';
}

export default function Home() {
  const [stockCode, setStockCode] = useState('600519');
  const [startDate, setStartDate] = useState('2023-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [backtestResults, setBacktestResults] = useState<BacktestResult[]>([]);
  const [activeTab, setActiveTab] = useState<'chart' | 'backtest'>('chart');
  const [selectedStrategy, setSelectedStrategy] = useState('ma');
  const [strategyParams, setStrategyParams] = useState<Record<string, any>>({});
  const [singleResult, setSingleResult] = useState<BacktestResult | null>(null);
  const [markers, setMarkers] = useState<TradeMarker[]>([]);
  const [showSingleChart, setShowSingleChart] = useState(false);
  const [portfolioCurves, setPortfolioCurves] = useState<any[]>([]);

  const handleGetChartData = async () => {
    setLoading(true);
    try {
      const res = await stockApi.getChartData(stockCode, startDate, endDate);
      const data = res.data.data.map((item: any) => ({
        time: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      }));
      setChartData(data);
      setActiveTab('chart');
    } catch (error) {
      alert('获取数据失败：' + (error as any).response?.data?.detail || (error as any).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRunBacktest = async () => {
    setLoading(true);
    try {
      const res = await stockApi.runAllBacktests(stockCode, startDate, endDate);
      setBacktestResults(res.data.results);
      // 处理组合价值曲线
      if (res.data.portfolio_curves) {
        const curves = Object.entries(res.data.portfolio_curves).map(([strategy, values]: [string, any]) => ({
          strategy,
          color: getStrategyColor(strategy),
          data: values.map((v: any) => ({ date: v.date, value: v.value })),
        }));
        setPortfolioCurves(curves);
      }
      setActiveTab('backtest');
    } catch (error) {
      alert('回测失败：' + (error as any).response?.data?.detail || (error as any).message);
    } finally {
      setLoading(false);
    }
  };

  const getStrategyColor = (strategy: string): string => {
    const colors: Record<string, string> = {
      ma: '#ef4444',
      rsi: '#22c55e',
      boll: '#3b82f6',
      macd: '#f59e0b',
      turtle: '#8b5cf6',
      mean_reversion: '#ec4899',
      tail_breakout: '#06b6d4',
    };
    return colors[strategy] || '#999999';
  };

  const handleRunSingleBacktest = async () => {
    setLoading(true);
    setSingleResult(null);
    setMarkers([]);
    try {
      const res = await stockApi.runBacktest(stockCode, startDate, endDate, selectedStrategy, strategyParams);
      setSingleResult(res.data.results);
      setMarkers(res.data.markers || []);
      setShowSingleChart(true);
      setActiveTab('chart');
    } catch (error) {
      alert('回测失败：' + (error as any).response?.data?.detail || (error as any).message);
    } finally {
      setLoading(false);
    }
  };

  const handleParamsChange = (newParams: Record<string, any>) => {
    setStrategyParams(newParams);
  };

  const popularStocks = [
    { code: '600519', name: '贵州茅台' },
    { code: '000858', name: '五粮液' },
    { code: '601318', name: '中国平安' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-xl font-bold">量化交易系统</h1>
          <p className="text-sm text-blue-100 mt-1">股票策略回测与分析平台</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto p-4">
        {/* Input Form */}
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">股票代码</label>
              <input
                type="text"
                value={stockCode}
                onChange={(e) => setStockCode(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="如：600519"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">开始日期</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">结束日期</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex items-end space-x-2">
              <button
                onClick={handleGetChartData}
                disabled={loading}
                className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-600 disabled:opacity-50"
              >
                {loading ? '加载中...' : '获取数据'}
              </button>
              <button
                onClick={handleRunBacktest}
                disabled={loading}
                className="flex-1 bg-green-500 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-600 disabled:opacity-50"
              >
                {loading ? '加载中...' : '全部回测'}
              </button>
            </div>
          </div>

          {/* Popular Stocks */}
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">热门股票:</span>
            {popularStocks.map((stock) => (
              <button
                key={stock.code}
                onClick={() => setStockCode(stock.code)}
                className="text-xs bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded transition"
              >
                {stock.code} {stock.name}
              </button>
            ))}
          </div>
        </div>

        {/* Single Strategy Backtest Section */}
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <h2 className="text-lg font-semibold mb-3">单策略回测</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">选择策略</label>
              <select
                value={selectedStrategy}
                onChange={(e) => setSelectedStrategy(e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {Object.entries(strategyNames).map(([key, name]) => (
                  <option key={key} value={key}>{name}</option>
                ))}
              </select>
            </div>
            <div className="md:col-span-2 flex items-end">
              <button
                onClick={handleRunSingleBacktest}
                disabled={loading}
                className="w-full bg-purple-500 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-purple-600 disabled:opacity-50"
              >
                {loading ? '回测中...' : '运行单策略回测'}
              </button>
            </div>
          </div>

          {/* Strategy Params Form */}
          <StrategyParamsForm
            selectedStrategy={selectedStrategy}
            params={strategyParams}
            onParamsChange={handleParamsChange}
          />

          {/* Single Result Display */}
          {singleResult && (
            <div className="mt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">回测结果</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <StrategyCard result={singleResult} rank={1} />
              </div>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-4">
          <button
            onClick={() => setActiveTab('chart')}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === 'chart'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500'
            }`}
          >
            K 线图
          </button>
          <button
            onClick={() => setActiveTab('backtest')}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === 'backtest'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500'
            }`}
          >
            策略回测结果
          </button>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-lg shadow p-4">
          {activeTab === 'chart' && (
            <div>
              <h2 className="text-lg font-semibold mb-4">
                {stockCode} K 线图 {showSingleChart && markers.length > 0 && `(含 ${selectedStrategy} 策略买卖点)`}
              </h2>
              {chartData.length > 0 ? (
                <CandlestickChart data={chartData} height={400} markers={showSingleChart ? markers : []} />
              ) : (
                <div className="text-center py-20 text-gray-400">
                  <p>点击「获取数据」查看 K 线图</p>
                </div>
              )}
              {showSingleChart && (
                <button
                  onClick={() => { setShowSingleChart(false); setMarkers([]); }}
                  className="mt-4 text-sm text-blue-500 hover:underline"
                >
                  清除买卖点标记
                </button>
              )}
            </div>
          )}

          {activeTab === 'backtest' && (
            <div>
              <h2 className="text-lg font-semibold mb-4">策略回测对比</h2>
              {/* 策略收益曲线对比图 */}
              {portfolioCurves.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">策略收益曲线对比</h3>
                  <StrategyComparisonChart curves={portfolioCurves} height={300} />
                  <div className="mt-2 flex flex-wrap gap-3">
                    {portfolioCurves.map(curve => (
                      <div key={curve.strategy} className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded" style={{ backgroundColor: curve.color }}></div>
                        <span className="text-xs text-gray-600">{curve.strategy}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {/* 策略结果卡片 */}
              {backtestResults.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {backtestResults.map((result, index) => (
                    <StrategyCard key={result.strategy} result={result} rank={index + 1} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-20 text-gray-400">
                  <p>点击「全部回测」运行策略对比</p>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-8 py-4 text-center text-sm text-gray-500">
        <p>量化交易系统 © 2024 | 支持移动端访问</p>
      </footer>
    </div>
  );
}
