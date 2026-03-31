'use client';

import { useEffect, useRef } from 'react';
import { createChart, type Time } from 'lightweight-charts';

interface PortfolioData {
  date: string;
  value: number;
}

interface StrategyCurve {
  strategy: string;
  color: string;
  data: PortfolioData[];
}

interface StrategyComparisonChartProps {
  curves: StrategyCurve[];
  height?: number;
}

const STRATEGY_COLORS: Record<string, string> = {
  ma: '#ef4444',
  rsi: '#22c55e',
  boll: '#3b82f6',
  macd: '#f59e0b',
  turtle: '#8b5cf6',
  mean_reversion: '#ec4899',
  tail_breakout: '#06b6d4',
};

export default function StrategyComparisonChart({ curves, height = 300 }: StrategyComparisonChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current || curves.length === 0) return;

    // 创建图表
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      timeScale: {
        timeVisible: false,
      },
      rightPriceScale: {
        borderColor: '#e5e7eb',
      },
    });

    // 为每个策略添加一条曲线
    curves.forEach(curve => {
      const color = STRATEGY_COLORS[curve.strategy] || '#999999';
      const areaSeries = chart.addAreaSeries({
        lineColor: color,
        topColor: color + '30',
        bottomColor: color + '00',
        lineWidth: 2,
      });

      // 格式化数据
      const formattedData = curve.data.map(item => ({
        time: new Date(item.date).getTime() / 1000 as Time,
        value: item.value,
      }));

      areaSeries.setData(formattedData);
    });

    chart.timeScale().fitContent();
    chartRef.current = chart;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [curves, height]);

  return <div ref={chartContainerRef} style={{ width: '100%', height: height }} />;
}
