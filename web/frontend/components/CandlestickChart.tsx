'use client';

import { useEffect, useRef } from 'react';
import { createChart, type Time } from 'lightweight-charts';

interface ChartData {
  time: string | number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface TradePoint {
  time: string;
  price: number;
  type: 'buy' | 'sell';
  date: string;
}

interface CandlestickChartProps {
  data: ChartData[];
  height?: number;
  markers?: TradePoint[];
}

export default function CandlestickChart({ data, height = 400, markers = [] }: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<any>(null);
  const seriesRef = useRef<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return;

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
    });

    // lightweight-charts v4 使用 addCandlestickSeries 方法
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#ef4444',
      downColor: '#22c55e',
      borderVisible: false,
      wickUpColor: '#ef4444',
      wickDownColor: '#22c55e',
    });

    // 格式化数据
    const formattedData = data.map(item => {
      // 将日期字符串转换为时间戳（lightweight-charts 需要）
      const timestamp = new Date(item.time as string).getTime() / 1000;
      return {
        time: timestamp as Time,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
      };
    });

    candlestickSeries.setData(formattedData);

    // 添加买卖点标记
    if (markers && markers.length > 0) {
      const seriesMarkers = markers.map(m => ({
        time: new Date(m.time).getTime() / 1000 as Time,
        position: m.type === 'buy' ? 'belowBar' : 'aboveBar',
        color: m.type === 'buy' ? '#22c55e' : '#ef4444',
        shape: m.type === 'buy' ? 'arrowUp' : 'arrowDown',
        text: m.type === 'buy' ? 'B' : 'S',
        size: 2,
      }));
      candlestickSeries.setMarkers(seriesMarkers);
    }

    chart.timeScale().fitContent();

    chartRef.current = chart;
    seriesRef.current = candlestickSeries;

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
        seriesRef.current = null;
      }
    };
  }, [data, height]);

  return <div ref={chartContainerRef} style={{ width: '100%', height: height }} />;
}
