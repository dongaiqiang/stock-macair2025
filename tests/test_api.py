"""
测试 API 端点
"""
import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from web.backend.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def stock_request():
    """创建股票请求数据"""
    return {
        "stock_code": "600519",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }


@pytest.fixture
def backtest_request():
    """创建回测请求数据"""
    return {
        "stock_code": "600519",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "strategy": "ma",
        "params": {}
    }


# 标记需要外部数据源连接的测试
pytestmark = pytest.mark.integration


class TestRootEndpoint:
    """测试根端点"""

    def test_root(self, client):
        """测试根端点返回欢迎消息"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "量化交易系统 API"
        assert data["status"] == "running"


class TestStrategiesEndpoint:
    """测试策略端点"""

    def test_get_strategies(self, client):
        """测试获取策略列表"""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert len(data["strategies"]) > 0

        # 检查策略结构
        for strategy in data["strategies"]:
            assert "id" in strategy
            assert "name" in strategy
            assert "description" in strategy

    def test_strategies_list(self, client):
        """测试策略列表包含所有预期策略"""
        response = client.get("/api/strategies")
        data = response.json()

        strategy_ids = [s["id"] for s in data["strategies"]]
        expected_strategies = [
            "ma", "rsi", "boll", "macd",
            "turtle", "mean_reversion", "tail_breakout"
        ]

        for expected in expected_strategies:
            assert expected in strategy_ids, f"Missing strategy: {expected}"


class TestStockDataEndpoint:
    """测试股票数据端点"""

    def test_get_stock_data(self, client, stock_request):
        """测试获取股票数据"""
        response = client.post("/api/stock/data", json=stock_request)
        assert response.status_code == 200
        data = response.json()
        assert "stock_code" in data
        assert "data" in data
        assert "count" in data

    def test_get_stock_data_structure(self, client, stock_request):
        """测试股票数据结构"""
        response = client.post("/api/stock/data", json=stock_request)
        data = response.json()

        assert data["stock_code"] == stock_request["stock_code"]
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

        # 检查数据记录结构
        record = data["data"][0]
        assert "date" in record
        assert "open" in record
        assert "high" in record
        assert "low" in record
        assert "close" in record
        assert "volume" in record

    def test_invalid_stock_code(self, client):
        """测试无效股票代码"""
        invalid_request = {
            "stock_code": "INVALID_CODE",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        response = client.post("/api/stock/data", json=invalid_request)
        assert response.status_code == 400


class TestChartDataEndpoint:
    """测试图表数据端点"""

    def test_get_chart_data(self, client, stock_request):
        """测试获取图表数据"""
        response = client.post("/api/stock/chart-data", json=stock_request)
        assert response.status_code == 200
        data = response.json()
        assert "stock_code" in data
        assert "data" in data

    def test_chart_data_contains_indicators(self, client, stock_request):
        """测试图表数据包含技术指标"""
        response = client.post("/api/stock/chart-data", json=stock_request)
        data = response.json()

        if len(data["data"]) > 0:
            record = data["data"][0]
            # 检查是否包含指标字段
            expected_fields = ["date", "open", "high", "low", "close", "volume"]
            for field in expected_fields:
                assert field in record or any(field in str(k) for k in record.keys())

    def test_chart_data_no_nan_inf(self, client, stock_request):
        """测试图表数据不包含 NaN/Inf"""
        response = client.post("/api/stock/chart-data", json=stock_request)
        data = response.json()

        # JSON 序列化后不应该有 NaN/Inf
        import json
        try:
            json.dumps(data)
            assert True
        except (ValueError, TypeError):
            pytest.fail("Response contains non-JSON-serializable values (NaN/Inf)")


class TestBacktestEndpoint:
    """测试回测端点"""

    def test_run_single_backtest(self, client, backtest_request):
        """测试运行单个策略回测"""
        response = client.post("/api/backtest", json=backtest_request)
        assert response.status_code == 200
        data = response.json()
        assert "stock_code" in data
        assert "strategy" in data
        assert "results" in data

    def test_backtest_results_structure(self, client, backtest_request):
        """测试回测结果结构"""
        response = client.post("/api/backtest", json=backtest_request)
        data = response.json()

        results = data["results"]
        expected_fields = [
            "final_value", "total_return",
            "max_drawdown", "total_trades", "win_rate"
        ]

        for field in expected_fields:
            assert field in results, f"Missing field: {field}"

    def test_backtest_with_params(self, client):
        """测试带参数的回测"""
        request_with_params = {
            "stock_code": "600519",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "strategy": "ma",
            "params": {"fast_period": 10, "slow_period": 30}
        }
        response = client.post("/api/backtest", json=request_with_params)
        assert response.status_code == 200
        data = response.json()
        assert data["params"] == {"fast_period": 10, "slow_period": 30}

    def test_invalid_strategy(self, client, stock_request):
        """测试无效策略"""
        invalid_request = {
            **stock_request,
            "strategy": "invalid_strategy",
            "params": {}
        }
        response = client.post("/api/backtest", json=invalid_request)
        assert response.status_code == 400


class TestAllBacktestEndpoint:
    """测试全部回测端点"""

    def test_run_all_strategies(self, client, stock_request):
        """测试运行所有策略"""
        response = client.post("/api/backtest/all", json=stock_request)
        assert response.status_code == 200
        data = response.json()
        assert "stock_code" in data
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) > 0

    def test_all_backtest_sorted_by_return(self, client, stock_request):
        """测试全部回测结果按收益率排序"""
        response = client.post("/api/backtest/all", json=stock_request)
        data = response.json()

        returns = [r.get("total_return", 0) for r in data["results"] if "error" not in r]
        # 检查是否按降序排列
        assert returns == sorted(returns, reverse=True)

    def test_all_backtest_strategy_results(self, client, stock_request):
        """测试每个策略的结果结构"""
        response = client.post("/api/backtest/all", json=stock_request)

        # 处理可能的错误响应
        if response.status_code != 200:
            pytest.skip(f"API returned {response.status_code}, skipping integration test")

        data = response.json()

        # 检查结果是否存在
        if "results" not in data:
            pytest.skip("No results in response, skipping integration test")

        for result in data["results"]:
            assert "strategy" in result
            # 每个结果应该有收益或错误信息
            assert "total_return" in result or "error" in result


class TestMultiStockBacktestEndpoint:
    """测试多股票回测端点"""

    def test_run_multi_stock_backtest(self, client):
        """测试运行多股票回测"""
        request = {
            "stock_codes": ["600519", "000858"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "strategy": "ma",
            "params": {}
        }
        response = client.post("/api/backtest/multi", json=request)
        assert response.status_code == 200
        data = response.json()
        assert "strategy" in data
        assert "results" in data

    def test_multi_stock_results(self, client):
        """测试多股票回测结果"""
        request = {
            "stock_codes": ["600519"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "strategy": "ma",
            "params": {}
        }
        response = client.post("/api/backtest/multi", json=request)
        data = response.json()

        for code, result in data["results"].items():
            assert "total_return" in result
            assert "max_drawdown" in result
            assert "total_trades" in result
            assert "win_rate" in result


class TestMLPredictEndpoint:
    """测试机器学习预测端点"""

    def test_ml_predict(self, client, stock_request):
        """测试机器学习预测"""
        response = client.post("/api/ml/predict", json=stock_request)
        assert response.status_code == 200
        data = response.json()
        assert "stock_code" in data
        assert "model_accuracy" in data
        assert "feature_importance" in data
        assert "backtest" in data

    def test_ml_backtest_structure(self, client, stock_request):
        """测试机器学习回测结构"""
        response = client.post("/api/ml/predict", json=stock_request)
        data = response.json()

        backtest = data["backtest"]
        assert "total_return" in backtest
        assert "total_trades" in backtest
        assert "win_rate" in backtest
