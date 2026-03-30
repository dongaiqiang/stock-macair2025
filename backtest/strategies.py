"""
回测策略模块
"""

import backtrader as bt
import pandas as pd


class MAStrategy(bt.Strategy):
    """双均线策略（支持止损止盈）"""

    params = (
        ('fast_period', 5),
        ('slow_period', 20),
        ('printlog', False),
        ('stop_loss', 0.0),      # 止损比例，如 0.05 表示 5%
        ('take_profit', 0.0),    # 止盈比例，如 0.10 表示 10%
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.stop_price = None   # 止损价格
        self.profit_price = None  # 止盈价格

        # 均线指标
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period
        )
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period
        )

        # 交叉信号
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                if self.params.printlog:
                    self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            if self.params.printlog:
                self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        if self.order:
            return

        current_price = self.dataclose[0]

        # 检查止损止盈
        if self.position:
            # 止损
            if self.params.stop_loss > 0 and current_price <= self.stop_price:
                if self.params.printlog:
                    self.log(f'STOP LOSS: Price {current_price:.2f} <= {self.stop_price:.2f}')
                self.order = self.sell()
                return

            # 止盈
            if self.params.take_profit > 0 and current_price >= self.profit_price:
                if self.params.printlog:
                    self.log(f'TAKE PROFIT: Price {current_price:.2f} >= {self.profit_price:.2f}')
                self.order = self.sell()
                return

            # 死叉卖出
            if self.crossover < 0:
                self.order = self.sell()
                return

        # 金叉买入
        if not self.position and self.crossover > 0:
            self.order = self.buy()
            # 设置止损止盈价格（用当前价格）
            current = self.dataclose[0]
            if self.params.stop_loss > 0:
                self.stop_price = current * (1 - self.params.stop_loss)
            if self.params.take_profit > 0:
                self.profit_price = current * (1 + self.params.take_profit)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def stop(self):
        if self.params.printlog:
            self.log(f'(Fast: {self.params.fast_period} Slow: {self.params.slow_period}) '
                     f'Ending Value: {self.broker.getvalue():.2f}')


class RSIStrategy(bt.Strategy):
    """RSI 策略"""

    params = (
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # RSI 指标
        self.rsi = bt.indicators.RSI(
            self.datas[0].close, period=self.params.rsi_period
        )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        # RSI < 30 买入
        if not self.position:
            if self.rsi < self.params.rsi_lower:
                self.order = self.buy()
        # RSI > 70 卖出
        else:
            if self.rsi > self.params.rsi_upper:
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')


class BollStrategy(bt.Strategy):
    """布林带策略"""

    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # 布林带指标
        self.boll = bt.indicators.BollingerBands(
            self.datas[0].close, period=self.params.period, devfactor=self.params.devfactor
        )
        self.boll_top = self.boll.lines.top
        self.boll_bot = self.boll.lines.bot
        self.boll_mid = self.boll.lines.mid

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        # 价格突破布林带下轨买入
        if not self.position:
            if self.dataclose < self.boll_bot:
                self.order = self.buy()
        # 价格突破布林带上轨卖出
        else:
            if self.dataclose > self.boll_top:
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')


class MACDStrategy(bt.Strategy):
    """MACD 策略"""

    params = (
        ('fast', 12),
        ('slow', 26),
        ('signal', 9),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None

        # MACD 指标
        self.macd = bt.indicators.MACD(
            self.datas[0].close,
            period_me1=self.params.fast,
            period_me2=self.params.slow,
            period_signal=self.params.signal
        )
        self.macd_line = self.macd.lines.macd
        self.signal_line = self.macd.lines.signal

        # 交叉信号
        self.crossover = bt.indicators.CrossOver(self.macd_line, self.signal_line)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.printlog:
                    self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            else:
                if self.params.printlog:
                    self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

        self.order = None

    def next(self):
        if self.order:
            return

        # MACD 金叉买入
        if not self.position:
            if self.crossover > 0:
                self.order = self.buy()
        # MACD 死叉卖出
        else:
            if self.crossover < 0:
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')


# ========== 新增策略 ==========

class TurtleStrategy(bt.Strategy):
    """海龟交易法策略"""

    params = (
        ('entry_period', 20),
        ('exit_period', 10),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.highest = bt.indicators.Highest(self.datas[0], period=self.params.entry_period)
        self.lowest = bt.indicators.Lowest(self.datas[0], period=self.params.entry_period)
        self.exit_highest = bt.indicators.Highest(self.datas[0], period=self.params.exit_period)
        self.exit_lowest = bt.indicators.Lowest(self.datas[0], period=self.params.exit_period)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy() and self.params.printlog:
                self.log(f'BUY: {order.executed.price:.2f}')
            elif self.params.printlog:
                self.log(f'SELL: {order.executed.price:.2f}')
        self.order = None

    def next(self):
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] > self.highest[-1]:
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.exit_lowest[-1]:
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')


class MeanReversionStrategy(bt.Strategy):
    """均值回归策略"""

    params = (
        ('period', 20),
        ('std_dev', 2.0),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.period)
        self.std = bt.indicators.StandardDeviation(self.datas[0], period=self.params.period)
        self.boll = bt.indicators.BollingerBands(self.datas[0], period=self.params.period, devfactor=self.params.std_dev)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy() and self.params.printlog:
                self.log(f'BUY: {order.executed.price:.2f}')
            elif self.params.printlog:
                self.log(f'SELL: {order.executed.price:.2f}')
        self.order = None

    def next(self):
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] < self.boll.lines.bot[0]:
                self.order = self.buy()
        else:
            if self.dataclose[0] > self.boll.lines.top[0]:
                self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')


class TailBreakoutStrategy(bt.Strategy):
    """尾盘突破策略 - 尾盘买入，次日卖出（适用于日K数据）

    策略逻辑：
    - 每日收盘时判断是否买入（收盘价突破N日最高价）
    - 次日开盘卖出（持有1天）
    """

    params = (
        ('lookback', 20),        # 回顾天数
        ('breakout_rate', 0.98), # 突破阈值（收盘价/最高价）
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.order = None
        self.buy_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_price = order.executed.price
                if self.params.printlog:
                    self.log(f'尾盘买入: {order.executed.price:.2f}')
            elif self.params.printlog:
                self.log(f'次日卖出: {order.executed.price:.2f}')
        self.order = None

    def next(self):
        if self.order:
            return

        # 计算过去N日的最高价
        lookback = min(self.params.lookback, len(self.datahigh))
        highest = max([self.datahigh[-i] for i in range(lookback)])

        # 尾盘买入条件：收盘价突破N日最高价的一定比例
        if not self.position:
            if self.dataclose[0] >= highest * self.params.breakout_rate:
                self.order = self.buy()

        # 次日卖出：持有1天后卖出
        elif self.position:
            self.order = self.sell()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')
