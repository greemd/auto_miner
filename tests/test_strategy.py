"""Tests for strategy signal generation using synthetic data."""

import pandas as pd
import numpy as np
import pytest

from auto_alpha_miner.strategy.base import BaseStrategy, Signal
from auto_alpha_miner.strategy.turtle import TurtleStrategy
from auto_alpha_miner.strategy.rsi_divergence import RSIDivergenceStrategy
from auto_alpha_miner.strategy.ma_cross import MovingAverageCrossStrategy


def make_ohlcv(prices: list[float], start: str = "2020-01-01") -> pd.DataFrame:
    """Create synthetic OHLCV DataFrame from a list of close prices."""
    dates = pd.bdate_range(start, periods=len(prices))
    return pd.DataFrame(
        {
            "Open": prices,
            "High": [p * 1.02 for p in prices],
            "Low": [p * 0.98 for p in prices],
            "Close": prices,
            "Volume": [1_000_000] * len(prices),
        },
        index=dates,
    )


class TestBaseStrategy:
    def test_signal_dataclass(self):
        sig = Signal(date=pd.Timestamp("2020-01-01"), action="BUY", size=0.5)
        assert sig.action == "BUY"
        assert sig.size == 0.5

    def test_cannot_instantiate_base(self):
        with pytest.raises(TypeError):
            BaseStrategy()  # type: ignore[abstract]


class TestTurtleStrategy:
    def test_prepare_adds_columns(self):
        prices = list(range(100, 150)) + list(range(150, 100, -1))
        df = make_ohlcv(prices)
        strat = TurtleStrategy(entry_period=10, exit_period=5)
        prepared = strat.prepare(df)
        assert "dc_upper" in prepared.columns
        assert "dc_lower" in prepared.columns
        assert "dc_exit_lower" in prepared.columns

    def test_generates_signals(self):
        # Flat, then sharp breakout up, then sharp breakdown
        flat = [100.0] * 15
        up = list(np.linspace(100, 200, 30))
        down = list(np.linspace(200, 60, 30))
        prices = flat + up + down
        df = make_ohlcv(prices)
        strat = TurtleStrategy(entry_period=10, exit_period=5)
        prepared = strat.prepare(df)
        signals = strat.generate_signals(prepared)
        actions = [s.action for s in signals]
        assert "BUY" in actions
        assert "SELL" in actions


class TestRSIStrategy:
    def test_prepare_adds_rsi(self):
        prices = list(np.linspace(100, 150, 50)) + list(np.linspace(150, 90, 50))
        df = make_ohlcv(prices)
        strat = RSIDivergenceStrategy(period=14)
        prepared = strat.prepare(df)
        assert "rsi" in prepared.columns

    def test_generates_signals_on_oscillation(self):
        # Create oscillating prices to trigger RSI signals
        np.random.seed(42)
        cycle = np.sin(np.linspace(0, 6 * np.pi, 200)) * 30 + 100
        prices = list(cycle)
        df = make_ohlcv(prices)
        strat = RSIDivergenceStrategy(period=14, oversold=30, overbought=70)
        prepared = strat.prepare(df)
        signals = strat.generate_signals(prepared)
        assert len(signals) > 0


class TestMACrossStrategy:
    def test_prepare_adds_sma_columns(self):
        prices = list(np.linspace(100, 200, 250))
        df = make_ohlcv(prices)
        strat = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
        prepared = strat.prepare(df)
        assert "sma_fast" in prepared.columns
        assert "sma_slow" in prepared.columns

    def test_generates_signals_on_crossover(self):
        # Start flat, go up sharply — should trigger golden cross
        flat = [100.0] * 50
        up = list(np.linspace(100, 200, 100))
        down = list(np.linspace(200, 80, 100))
        prices = flat + up + down
        df = make_ohlcv(prices)
        strat = MovingAverageCrossStrategy(fast_period=10, slow_period=30)
        prepared = strat.prepare(df)
        signals = strat.generate_signals(prepared)
        actions = [s.action for s in signals]
        assert "BUY" in actions
