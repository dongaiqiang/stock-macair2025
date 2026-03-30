'use client';

interface StrategyParam {
  name: string;
  label: string;
  type: 'number' | 'select';
  default: number;
  min?: number;
  max?: number;
  step?: number;
  options?: { value: number; label: string }[];
}

interface StrategyParams {
  [key: string]: StrategyParam[];
}

const strategyParams: StrategyParams = {
  ma: [
    { name: 'fast_period', label: '快线周期', type: 'number', default: 5, min: 1, max: 60 },
    { name: 'slow_period', label: '慢线周期', type: 'number', default: 20, min: 1, max: 120 },
    { name: 'stop_loss', label: '止损比例 (%)', type: 'number', default: 0, min: 0, max: 100, step: 0.5 },
    { name: 'take_profit', label: '止盈比例 (%)', type: 'number', default: 0, min: 0, max: 200, step: 0.5 },
  ],
  rsi: [
    { name: 'rsi_period', label: 'RSI 周期', type: 'number', default: 14, min: 2, max: 50 },
    { name: 'rsi_upper', label: '超买线', type: 'number', default: 70, min: 50, max: 95 },
    { name: 'rsi_lower', label: '超卖线', type: 'number', default: 30, min: 5, max: 50 },
  ],
  boll: [
    { name: 'period', label: '周期', type: 'number', default: 20, min: 5, max: 60 },
    { name: 'devfactor', label: '标准差倍数', type: 'number', default: 2.0, min: 0.5, max: 4, step: 0.1 },
  ],
  macd: [
    { name: 'fast', label: '快线周期', type: 'number', default: 12, min: 2, max: 50 },
    { name: 'slow', label: '慢线周期', type: 'number', default: 26, min: 10, max: 100 },
    { name: 'signal', label: '信号线周期', type: 'number', default: 9, min: 2, max: 30 },
  ],
  turtle: [
    { name: 'entry_period', label: '入场周期', type: 'number', default: 20, min: 5, max: 60 },
    { name: 'exit_period', label: '出场周期', type: 'number', default: 10, min: 3, max: 30 },
  ],
  mean_reversion: [
    { name: 'period', label: '周期', type: 'number', default: 20, min: 5, max: 60 },
    { name: 'std_dev', label: '标准差倍数', type: 'number', default: 2.0, min: 0.5, max: 4, step: 0.1 },
  ],
  tail_breakout: [
    { name: 'lookback', label: '回顾周期', type: 'number', default: 20, min: 5, max: 60 },
    { name: 'breakout_rate', label: '突破阈值 (%)', type: 'number', default: 98, min: 90, max: 100, step: 0.5 },
  ],
};

const strategyNames: Record<string, string> = {
  ma: '双均线策略',
  rsi: 'RSI 超买超卖',
  boll: '布林带突破',
  macd: 'MACD',
  turtle: '海龟交易',
  mean_reversion: '均值回归',
  tail_breakout: '尾盘突破',
};

interface StrategyParamsFormProps {
  selectedStrategy: string;
  params: Record<string, any>;
  onParamsChange: (params: Record<string, any>) => void;
}

export default function StrategyParamsForm({ selectedStrategy, params, onParamsChange }: StrategyParamsFormProps) {
  const currentParams = strategyParams[selectedStrategy] || [];

  const handleParamChange = (paramName: string, value: string) => {
    const param = currentParams.find(p => p.name === paramName);
    let newValue: number | string = value;

    if (param?.type === 'number') {
      newValue = parseFloat(value);
      if (isNaN(newValue)) return;
    }

    // 对于百分比类型的参数，需要转换为小数
    if (paramName === 'stop_loss' || paramName === 'take_profit') {
      newValue = (newValue as number) / 100;
    }

    // 对于 breakout_rate，98% 转换为 0.98
    if (paramName === 'breakout_rate') {
      newValue = (newValue as number) / 100;
    }

    onParamsChange({ ...params, [paramName]: newValue });
  };

  const getDisplayValue = (paramName: string, value: any): string => {
    // 对于百分比类型的参数，从小数转换为百分比显示
    if (paramName === 'stop_loss' || paramName === 'take_profit') {
      return ((value || 0) * 100).toString();
    }
    if (paramName === 'breakout_rate') {
      return ((value || 0.98) * 100).toString();
    }
    return value?.toString() || '';
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 mt-4">
      <h3 className="font-semibold text-gray-700 mb-3">
        {strategyNames[selectedStrategy] || selectedStrategy} - 参数配置
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {currentParams.map((param) => (
          <div key={param.name}>
            <label className="block text-xs text-gray-600 mb-1">{param.label}</label>
            {param.type === 'select' ? (
              <select
                value={params[param.name]?.toString() || param.default.toString()}
                onChange={(e) => handleParamChange(param.name, e.target.value)}
                className="w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {param.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="number"
                value={getDisplayValue(param.name, params[param.name])}
                onChange={(e) => handleParamChange(param.name, e.target.value)}
                min={param.min}
                max={param.max}
                step={param.step || 1}
                className="w-full border border-gray-300 rounded-md px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export { strategyParams, strategyNames };
