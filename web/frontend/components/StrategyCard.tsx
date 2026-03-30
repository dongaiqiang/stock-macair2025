'use client';

interface BacktestResult {
  strategy: string;
  total_return: number;
  max_drawdown: number;
  total_trades: number;
  win_rate: number;
  final_value: number;
}

interface StrategyCardProps {
  result: BacktestResult;
  rank: number;
}

const strategyNames: Record<string, string> = {
  ma: '双均线',
  rsi: 'RSI 超买超卖',
  boll: '布林带突破',
  macd: 'MACD',
  turtle: '海龟交易',
  mean_reversion: '均值回归',
  tail_breakout: '尾盘突破',
};

export default function StrategyCard({ result, rank }: StrategyCardProps) {
  const isPositive = result.total_return >= 0;
  // 后端返回的是小数格式 (0.001 = 0.1%)，转换为百分比显示
  const safeReturn = (result.total_return ?? 0) * 100;
  const safeWinRate = result.win_rate ?? 0;
  const safeDrawdown = (result.max_drawdown ?? 0) * 100;
  const safeFinalValue = result.final_value ?? 0;
  const safeTrades = result.total_trades ?? 0;

  // 根据收益率大小决定小数位数
  const returnPrecision = Math.abs(safeReturn) < 0.1 ? 4 : 2;
  const drawdownPrecision = Math.abs(safeDrawdown) < 0.1 ? 4 : 2;

  return (
    <div className="bg-white rounded-lg shadow p-4 border-l-4" style={{ borderLeftColor: isPositive ? '#22c55e' : '#ef4444' }}>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-gray-800">
            #{rank} {strategyNames[result.strategy] || result.strategy}
          </h3>
          <p className="text-sm text-gray-500 mt-1">交易 {safeTrades} 笔</p>
        </div>
        <div className="text-right">
          <p className={`text-lg font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? '+' : ''}{safeReturn.toFixed(returnPrecision)}%
          </p>
          <p className="text-xs text-gray-400">胜率 {safeWinRate.toFixed(1)}%</p>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
        <div>
          <span className="text-gray-400">最大回撤</span>
          <p className="text-red-500 font-medium">{safeDrawdown.toFixed(drawdownPrecision)}%</p>
        </div>
        <div>
          <span className="text-gray-400">最终资金</span>
          <p className="text-gray-700 font-medium">¥{(safeFinalValue / 10000).toFixed(0)}万</p>
        </div>
      </div>
    </div>
  );
}
