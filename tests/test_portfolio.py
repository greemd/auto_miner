"""Tests for multi-symbol portfolio backtesting and allocation."""

import pandas as pd
import numpy as np
import pytest

from auto_alpha_miner.backtest.allocator import EqualWeightAllocator
from auto_alpha_miner.backtest.engine import BacktestEngine, BacktestResult
from auto_alpha_miner.backtest.multi_engine import MultiSymbolEngine, PortfolioResult
from auto_alpha_miner.backtest.trade import Trade
from auto_alpha_miner.evaluation.metrics import evaluate_portfolio
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


class FixedSignalStrategy(BaseStrategy):
    name = "fixed_portfolio_test"

    def __init__(self, buy_idx: int = 1, sell_idx: int = 3):
        self.buy_idx = buy_idx
        self.sell_idx = sell_idx

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals = []
        if len(df) > self.buy_idx:
            signals.append(Signal(date=df.index[self.buy_idx], action="BUY"))
        if len(df) > self.sell_idx:
            signals.append(Signal(date=df.index[self.sell_idx], action="SELL"))
        return signals


def make_ohlcv(prices: list[float], start: str = "2020-01-01") -> pd.DataFrame:
    dates = pd.bdate_range(start, periods=len(prices))
    return pd.DataFrame(
        {
            "Open": prices,
            "High": prices,
            "Low": prices,
            "Close": prices,
            "Volume": [1_000_000] * len(prices),
        },
        index=dates,
    )


def make_result(prices: list[float], symbol: str) -> BacktestResult:
    df = make_ohlcv(prices)
    engine = BacktestEngine(initial_capital=10_000.0)
    strat = FixedSignalStrategy()
    return engine.run(df, strat, symbol)


class TestEqualWeightAllocator:
    def test_equal_weights(self):
        r1 = make_result([100, 105, 110, 115, 120], "A")
        r2 = make_result([100, 95, 90, 85, 80], "B")
        allocator = EqualWeightAllocator()
        weights = allocator.allocate({"A": r1, "B": r2})
        assert weights["A"] == pytest.approx(0.5)
        assert weights["B"] == pytest.approx(0.5)

    def test_three_symbols(self):
        results = {f"S{i}": make_result([100 + i] * 5, f"S{i}") for i in range(3)}
        allocator = EqualWeightAllocator()
        weights = allocator.allocate(results)
        for w in weights.values():
            assert w == pytest.approx(1.0 / 3.0)

    def test_empty(self):
        assert EqualWeightAllocator().allocate({}) == {}


class TestMultiSymbolEngine:
    def test_portfolio_result_structure(self):
        data = {
            "A": make_ohlcv([100, 105, 110, 115, 120]),
            "B": make_ohlcv([100, 95, 105, 110, 108]),
        }
        engine = MultiSymbolEngine(initial_capital=10_000.0)
        allocator = EqualWeightAllocator()
        result = engine.run(data, FixedSignalStrategy, allocator)

        assert isinstance(result, PortfolioResult)
        assert result.strategy_name == "fixed_portfolio_test"
        assert result.allocator_name == "equal"
        assert len(result.symbol_results) == 2
        assert "A" in result.weights
        assert "B" in result.weights
        assert len(result.combined_equity) > 0

    def test_combined_equity_length(self):
        data = {
            "A": make_ohlcv([100, 105, 110, 115, 120]),
            "B": make_ohlcv([100, 95, 105, 110, 108]),
        }
        engine = MultiSymbolEngine(initial_capital=10_000.0)
        result = engine.run(data, FixedSignalStrategy, EqualWeightAllocator())
        assert len(result.combined_equity) == 5


class TestRebalancing:
    def test_monthly_rebalancing_produces_weight_history(self):
        # ~6 months of data = should produce multiple rebalancing events
        prices_a = list(np.linspace(100, 150, 130))
        prices_b = list(np.linspace(100, 90, 130))
        data = {
            "A": make_ohlcv(prices_a),
            "B": make_ohlcv(prices_b),
        }
        engine = MultiSymbolEngine(initial_capital=10_000.0)
        result = engine.run(data, FixedSignalStrategy, EqualWeightAllocator(), rebalance="M")
        assert result.rebalance_frequency == "M"
        assert len(result.weight_history) > 1  # Multiple rebalances
        assert len(result.combined_equity) == 130

    def test_weekly_rebalancing(self):
        prices = list(np.linspace(100, 150, 60))
        data = {"A": make_ohlcv(prices), "B": make_ohlcv(prices)}
        engine = MultiSymbolEngine(initial_capital=10_000.0)
        result = engine.run(data, FixedSignalStrategy, EqualWeightAllocator(), rebalance="W")
        assert result.rebalance_frequency == "W"
        assert len(result.weight_history) > 4  # Multiple weekly rebalances

    def test_quarterly_rebalancing(self):
        prices = list(np.linspace(100, 200, 252))
        data = {"A": make_ohlcv(prices), "B": make_ohlcv(prices)}
        engine = MultiSymbolEngine(initial_capital=10_000.0)
        result = engine.run(data, FixedSignalStrategy, EqualWeightAllocator(), rebalance="Q")
        assert result.rebalance_frequency == "Q"
        assert len(result.weight_history) >= 3  # ~4 quarters in a year


class TestEvaluatePortfolio:
    def test_returns_all_keys(self):
        data = {
            "A": make_ohlcv(list(np.linspace(100, 150, 30))),
            "B": make_ohlcv(list(np.linspace(100, 120, 30))),
        }
        engine = MultiSymbolEngine(initial_capital=10_000.0)
        result = engine.run(data, FixedSignalStrategy, EqualWeightAllocator())
        metrics = evaluate_portfolio(result)
        expected_keys = {"total_return", "cagr", "max_drawdown", "sharpe_ratio", "win_rate", "profit_factor", "trade_count"}
        assert set(metrics.keys()) == expected_keys


class TestConfigYAML:
    def test_symbols_loaded_from_yaml(self):
        from auto_alpha_miner.config import SYMBOL_MAP, UNIVERSES
        assert len(SYMBOL_MAP) > 0
        assert "SP500" in SYMBOL_MAP
        assert "BTC" in SYMBOL_MAP

    def test_universes_loaded(self):
        from auto_alpha_miner.config import UNIVERSES
        assert len(UNIVERSES) > 0
        assert "global" in UNIVERSES
        assert "crypto" in UNIVERSES
        assert "BTC" in UNIVERSES["crypto"]
