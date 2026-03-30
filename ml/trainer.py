"""
模型训练器
提供完整的训练流程
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import warnings

warnings.filterwarnings('ignore')


class ModelTrainer:
    """模型训练器"""

    def __init__(self, model_type: str = 'lgbm'):
        """
        初始化训练器

        Args:
            model_type: 模型类型
        """
        self.model_type = model_type
        self.predictor = None
        self.feature_engineer = None

    def prepare_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> tuple:
        """
        准备训练数据

        Args:
            df: 原始股票数据
            test_size: 测试集比例

        Returns:
            (X_train, X_test, y_train, y_test)
        """
        from sklearn.model_selection import train_test_split
        from ml.features import FeatureEngineer

        # 特征工程
        self.feature_engineer = FeatureEngineer()
        df_features = self.feature_engineer.create_features(df)

        # 准备数据
        X, y = self.feature_engineer.prepare_train_data(df_features)

        # 划分数据集（时间序列，不打乱）
        split_idx = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        return X_train, X_test, y_train, y_test

    def train(
        self,
        df: pd.DataFrame,
        model_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        训练模型

        Args:
            df: 股票数据
            model_type: 模型类型

        Returns:
            训练结果
        """
        from ml.models import StockPredictor
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        if model_type:
            self.model_type = model_type

        # 准备数据
        X_train, X_test, y_train, y_test = self.prepare_data(df)

        # 创建模型
        self.predictor = StockPredictor(model_type=self.model_type)

        # 训练
        self.predictor.feature_columns = self.feature_engineer.feature_columns
        self.predictor.model.fit(X_train, y_train)

        # 预测
        y_pred = self.predictor.predict(X_test)

        # 评估指标
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        # 特征重要性
        importance = self.predictor.get_feature_importance()

        return {
            'model_type': self.model_type,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'feature_importance': importance,
            'y_test': y_test.values,
            'y_pred': y_pred,
        }

    def optimize_params(
        self,
        df: pd.DataFrame,
        param_grid: Dict[str, List]
    ) -> Dict[str, Any]:
        """
        参数优化

        Args:
            df: 股票数据
            param_grid: 参数网格

        Returns:
            最优参数和结果
        """
        from sklearn.model_selection import GridSearchCV
        from ml.models import StockPredictor
        from sklearn.ensemble import RandomForestClassifier

        X_train, X_test, y_train, y_test = self.prepare_data(df)

        # 使用随机森林进行快速优化
        model = RandomForestClassifier(random_state=42)

        # 简化参数网格以加快搜索
        grid = {
            'n_estimators': [50, 100],
            'max_depth': [3, 5, 7],
        }

        grid_search = GridSearchCV(
            model, grid, cv=3, scoring='accuracy', n_jobs=-1
        )
        grid_search.fit(X_train, y_train)

        best_params = grid_search.best_params_
        best_score = grid_search.score(X_test, y_test)

        return {
            'best_params': best_params,
            'best_cv_score': grid_search.best_score_,
            'test_score': best_score,
        }

    def evaluate_signals(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        评估交易信号

        Args:
            df: 股票数据

        Returns:
            带有预测信号的 DataFrame
        """
        if self.predictor is None:
            raise ValueError("模型未训练")

        # 特征工程
        df_features = self.feature_engineer.create_features(df)

        # 获取特征
        X = df_features[self.feature_engineer.feature_columns]

        # 预测
        signals = self.predictor.predict(X)
        probabilities = self.predictor.predict_proba(X)

        # 添加到 DataFrame
        df_result = df_features.copy()
        df_result['signal'] = signals
        df_result['probability'] = probabilities

        return df_result

    def get_latest_signal(
        self,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        获取最新交易信号

        Args:
            df: 股票数据

        Returns:
            信号字典
        """
        df_signals = self.evaluate_signals(df)

        latest = df_signals.iloc[-1]

        signal_map = {1: '买入', 0: '卖出'}
        signal = int(latest['signal'])
        probability = latest['probability']

        return {
            'signal': signal,
            'signal_name': signal_map[signal],
            'probability': probability,
            'price': latest['close'],
            'date': df_signals.index[-1],
        }


def quick_train(
    df: pd.DataFrame,
    model_type: str = 'lgbm'
) -> tuple:
    """
    快速训练函数

    Args:
        df: 股票数据
        model_type: 模型类型

    Returns:
        (训练器, 训练结果)
    """
    trainer = ModelTrainer(model_type=model_type)
    results = trainer.train(df)
    return trainer, results


if __name__ == '__main__':
    from data.fetcher import StockData

    print("=" * 50)
    print("模型训练器测试")
    print("=" * 50)

    # 获取数据
    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    # 训练
    trainer = ModelTrainer(model_type='lgbm')
    results = trainer.train(df)

    print(f"\n模型类型: {results['model_type']}")
    print(f"准确率: {results['accuracy']:.2%}")
    print(f"精确率: {results['precision']:.2%}")
    print(f"召回率: {results['recall']:.2%}")
    print(f"F1分数: {results['f1_score']:.2%}")

    # 获取最新信号
    signal = trainer.get_latest_signal(df)
    print(f"\n最新信号:")
    print(f"  信号: {signal['signal_name']}")
    print(f"  概率: {signal['probability']:.2%}")
    print(f"  价格: ¥{signal['price']:.2f}")
