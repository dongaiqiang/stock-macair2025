"""
机器学习模型模块
提供股票预测模型
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
import warnings

warnings.filterwarnings('ignore')


class StockPredictor:
    """股票预测器"""

    def __init__(self, model_type: str = 'lgbm'):
        """
        初始化预测器

        Args:
            model_type: 模型类型，'lgbm', 'rf', 'xgb'
        """
        self.model_type = model_type
        self.model = None
        self.feature_columns = None
        self._init_model()

    def _init_model(self):
        """初始化模型"""
        if self.model_type == 'lgbm':
            try:
                import lightgbm as lgb
                self.model = lgb.LGBMClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42,
                    verbose=-1
                )
            except (ImportError, OSError):
                from sklearn.ensemble import RandomForestClassifier
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42,
                    n_jobs=-1
                )
                self.model_type = 'rf'

        elif self.model_type == 'rf':
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )

        elif self.model_type == 'xgb':
            try:
                import xgboost as xgb
                self.model = xgb.XGBClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=5,
                    random_state=42,
                    use_label_encoder=False,
                    eval_metric='logloss'
                )
            except ImportError:
                from sklearn.ensemble import RandomForestClassifier
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42
                )
                self.model_type = 'rf'

        else:
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2
    ) -> Dict[str, Any]:
        """
        训练模型

        Args:
            X: 特征数据
            y: 目标变量
            test_size: 测试集比例

        Returns:
            训练结果字典
        """
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report

        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )

        # 保存特征列名
        self.feature_columns = X.columns.tolist()

        # 训练模型
        self.model.fit(X_train, y_train)

        # 预测
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1] if hasattr(self.model, 'predict_proba') else None

        # 评估
        accuracy = accuracy_score(y_test, y_pred)

        return {
            'accuracy': accuracy,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'y_test': y_test.values,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """预测"""
        if self.model is None:
            raise ValueError("模型未训练，请先调用 train() 方法")

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """预测概率"""
        if self.model is None:
            raise ValueError("模型未训练，请先调用 train() 方法")

        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)[:, 1]
        else:
            return self.predict(X)

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """获取特征重要性"""
        if self.model is None:
            return None

        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            return pd.DataFrame({
                'feature': self.feature_columns,
                'importance': importance
            }).sort_values('importance', ascending=False)

        return None

    def backtest(
        self,
        df: pd.DataFrame,
        initial_capital: float = 1000000,
        position_size: float = 0.1
    ) -> Dict[str, Any]:
        """
        回测策略

        Args:
            df: 带有特征的股票数据
            initial_capital: 初始资金
            position_size: 每次仓位比例

        Returns:
            回测结果
        """
        from sklearn.model_selection import train_test_split

        # 准备数据
        X = df[self.feature_columns]
        y = df['target_class']

        # 删除空值
        valid_idx = ~(X.isna().any(axis=1) | y.isna())
        X = X[valid_idx]
        y = y[valid_idx]
        df_valid = df[valid_idx].copy()

        # 训练测试分割（时间序列，不打乱）
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        df_test = df_valid.iloc[train_size:]

        # 训练
        self.model.fit(X_train, y_train)

        # 预测
        signals = self.model.predict(X_test)

        # 回测
        capital = initial_capital
        position = 0
        trades = []
        portfolio_values = [initial_capital]

        for i in range(len(signals)):
            current_price = df_test.iloc[i]['close']
            next_return = df_test.iloc[i].get('target', 0)
            if pd.isna(next_return):
                next_return = 0

            if signals[i] == 1 and position == 0:
                # 买入
                shares = int(capital * position_size / current_price)
                position = shares * current_price
                capital -= position
                trades.append(('buy', df_test.index[i], current_price))

            elif signals[i] == 0 and position > 0:
                # 卖出
                capital += position * (1 + next_return)
                trades.append(('sell', df_test.index[i], current_price * (1 + next_return)))
                position = 0

            # 记录组合价值
            portfolio_value = capital + position * (1 + next_return)
            portfolio_values.append(portfolio_value)

        # 计算收益
        final_value = portfolio_values[-1]
        total_return = (final_value - initial_capital) / initial_capital * 100

        return {
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_trades': len(trades),
            'trades': trades,
            'portfolio_values': portfolio_values,
        }


def train_model(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: str = 'lgbm'
) -> StockPredictor:
    """
    便捷训练函数

    Args:
        X: 特征
        y: 目标
        model_type: 模型类型

    Returns:
        训练好的模型
    """
    predictor = StockPredictor(model_type=model_type)
    predictor.train(X, y)
    return predictor


if __name__ == '__main__':
    from data.fetcher import StockData
    from ml.features import FeatureEngineer

    print("=" * 50)
    print("机器学习模型测试")
    print("=" * 50)

    # 获取数据
    sd = StockData()
    df = sd.get_a_stock('600519', '2023-01-01', '2024-12-31')

    # 创建特征
    print("\n创建特征...")
    fe = FeatureEngineer()
    df_features = fe.create_features(df)

    # 准备训练数据
    X, y = fe.prepare_train_data(df_features)
    print(f"训练数据: X={X.shape}, y={y.shape}")

    # 训练模型
    print("\n训练模型...")
    predictor = StockPredictor(model_type='lgbm')
    results = predictor.train(X, y)

    print(f"\n模型准确率: {results['accuracy']:.2%}")

    # 特征重要性
    importance = predictor.get_feature_importance()
    if importance is not None:
        print("\nTop 10 特征重要性:")
        print(importance.head(10))

    # 回测
    print("\n回测...")
    backtest_results = predictor.backtest(df_features)
    print(f"回测收益: {backtest_results['total_return']:.2f}%")
    print(f"交易次数: {backtest_results['total_trades']}")
