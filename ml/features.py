"""
特征工程模块
生成机器学习所需的特征
"""

import pandas as pd
import numpy as np
from typing import Optional, List


class FeatureEngineer:
    """特征工程"""

    def __init__(self):
        self.feature_columns = []

    def create_features(
        self,
        df: pd.DataFrame,
        include_technical: bool = True,
        include_price: bool = True,
        include_volume: bool = True,
    ) -> pd.DataFrame:
        """
        创建特征

        Args:
            df: 股票数据
            include_technical: 是否包含技术指标
            include_price: 是否包含价格特征
            include_volume: 是否包含成交量特征

        Returns:
            添加了特征的 DataFrame
        """
        result = df.copy()

        if include_price:
            result = self._add_price_features(result)

        if include_volume:
            result = self._add_volume_features(result)

        if include_technical:
            result = self._add_technical_features(result)

        # 创建目标变量（未来收益）
        result = self._add_target(result)

        # 排除目标变量和非特征列
        exclude_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'target', 'target_class']
        self.feature_columns = [col for col in result.columns if col not in exclude_cols]

        return result

    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """价格相关特征"""
        # 收益率
        df['return'] = df['close'].pct_change()

        # 价格变化
        df['price_change'] = df['close'] - df['close'].shift(1)

        # 价格波动率
        df['volatility'] = df['return'].rolling(window=5).std()

        # 价格动量
        df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_20'] = df['close'] / df['close'].shift(20) - 1

        # 价格相对位置
        df['high_20'] = df['close'].rolling(window=20).max()
        df['low_20'] = df['close'].rolling(window=20).min()
        df['price_position'] = (df['close'] - df['low_20']) / (df['high_20'] - df['low_20'])

        return df

    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """成交量相关特征"""
        # 成交量变化
        df['volume_change'] = df['volume'].pct_change()

        # 成交量均线
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ma20'] = df['volume'].rolling(window=20).mean()

        # 量价关系
        df['volume_price_ratio'] = df['volume'] / df['volume_ma20']

        # 成交额变化
        if 'amount' in df.columns:
            df['amount_change'] = df['amount'].pct_change()

        return df

    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """技术指标特征"""
        # 简单移动平均
        for period in [5, 10, 20, 60]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'close_sma_{period}_ratio'] = df['close'] / df[f'sma_{period}']

        # 指数移动平均
        for period in [12, 26]:
            df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']

        # RSI
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # 布林带
        sma20 = df['close'].rolling(window=20).mean()
        std20 = df['close'].rolling(window=20).std()
        df['bb_upper'] = sma20 + 2 * std20
        df['bb_lower'] = sma20 - 2 * std20
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / sma20
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # KDJ
        low_n = df['low'].rolling(window=9).min()
        high_n = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_n) / (high_n - low_n) * 100
        df['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']

        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()

        return df

    def _add_target(self, df: pd.DataFrame, horizon: int = 1) -> pd.DataFrame:
        """
        创建目标变量

        Args:
            df: 数据
            horizon: 预测周期（天数）

        Returns:
            添加了目标变量的 DataFrame
        """
        # 未来收益率
        df['target'] = df['close'].shift(-horizon) / df['close'] - 1

        # 二分类目标：上涨=1，下跌=0
        df['target_class'] = (df['target'] > 0).astype(int)

        return df

    def prepare_train_data(
        self,
        df: pd.DataFrame,
        drop_na: bool = True,
        target_type: str = 'class'
    ) -> tuple:
        """
        准备训练数据

        Args:
            df: 特征数据
            drop_na: 是否删除空值
            target_type: 'class' 或 'regression'

        Returns:
            (X, y) 元组
        """
        data = df.copy()

        # 删除空值
        if drop_na:
            data = data.dropna()

        # 选择特征和目标
        X = data[self.feature_columns]
        y = data['target_class'] if target_type == 'class' else data['target']

        return X, y

    def get_feature_importance(
        self,
        feature_names: List[str],
        importance: np.ndarray,
        top_n: int = 20
    ) -> pd.DataFrame:
        """获取特征重要性"""
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        return importance_df.head(top_n)


if __name__ == '__main__':
    from data.fetcher import StockData

    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    print("创建特征...")
    fe = FeatureEngineer()
    df_features = fe.create_features(df)

    print(f"\n特征数量: {len(fe.feature_columns)}")
    print(f"特征列表: {fe.feature_columns[:10]}...")

    X, y = fe.prepare_train_data(df_features)
    print(f"\n训练数据形状: X={X.shape}, y={y.shape}")
    print(f"目标分布: 上涨={y.sum()}, 下跌={len(y)-y.sum()}")
