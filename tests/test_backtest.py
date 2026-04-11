"""Tests for backtest engine with known signals."""

import pandas as pd
import pytest

from auto_alpha_miner.backtest.engine import BacktestEngine, BacktestResult
from auto_alpha_miner.backtest.portfolio import Portfolio
from auto_alpha_miner.backtest.trade import Trade
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


class FixedSignalStrategy(BaseStrategy):
    """Strategy that returns pre-defined signals for testing."""

    name = "fixed"

    def __init__(self, signals: list[Signal]):
        self._signals = signals

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        return self._signals


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


class TestPortfolio:
    def test_buy_and_sell(self):
        portfolio = Portfolio(initial_capital=10_000.0)
        t = portfolio.buy(pd.Timestamp("2020-01-01"), 100.0, "TEST")
        assert t is not None
        assert portfolio.in_position
        assert portfolio.cash == 0.0  # All cash invested

        t = portfolio.sell(pd.Timestamp("2020-01-10"), 110.0, "TEST")
        assert t is not None
        assert not portfolio.in_position
        assert t.pnl == pytest.approx(1000.0)  # 100 shares * $10 gain
        assert portfolio.cash == pytest.approx(11_000.0)

    def test_cannot_double_buy(self):
        portfolio = Portfolio(initial_capital=10_000.0)
        portfolio.buy(pd.Timestamp("2020-01-01"), 100.0, "TEST")
        t = portfolio.buy(pd.Timestamp("2020-01-02"), 105.0, "TEST")
        assert t is None  # Should not open a second position

    def test_cannot_sell_without_position(self):
        portfolio = Portfolio(initial_capital=10_000.0)
        t = portfolio.sell(pd.Timestamp("2020-01-01"), 100.0, "TEST")
        assert t is None

    def test_equity_curve(self):
        portfolio = Portfolio(initial_capital=10_000.0)
        portfolio.record_equity(pd.Timestamp("2020-01-01"), 100.0)
        portfolio.buy(pd.Timestamp("2020-01-01"), 100.0, "TEST")
        portfolio.record_equity(pd.Timestamp("2020-01-02"), 110.0)
        ec = portfolio.equity_curve
        assert len(ec) == 2
        assert ec.iloc[0] == 10_000.0  # Before buy recorded at same time


class TestBacktestEngine:
    def test_simple_profitable_trade(self):
        prices = [100.0, 105.0, 110.0, 115.0, 120.0]
        df = make_ohlcv(prices)
        dates = df.index

        signals = [
            Signal(date=dates[1], action="BUY"),
            Signal(date=dates[3], action="SELL"),
        ]
        strategy = FixedSignalStrategy(signals)
        engine = BacktestEngine(initial_capital=10_000.0)
        result = engine.run(df, strategy, "TEST")

        assert isinstance(result, BacktestResult)
        assert result.strategy_name == "fixed"
        assert len(result.trades) >= 1
        assert result.trades[0].pnl > 0  # Profitable trade

    def test_force_closes_open_position(self):
        prices = [100.0, 105.0, 110.0, 115.0, 120.0]
        df = make_ohlcv(prices)
        dates = df.index

        signals = [Signal(date=dates[1], action="BUY")]  # No sell signal
        strategy = FixedSignalStrategy(signals)
        engine = BacktestEngine(initial_capital=10_000.0)
        result = engine.run(df, strategy, "TEST")

        # Should force-close at end
        assert len(result.trades) == 1
        assert result.trades[0].exit_price == 120.0

    def test_equity_curve_length(self):
        prices = [100.0] * 20
        df = make_ohlcv(prices)
        strategy = FixedSignalStrategy([])
        engine = BacktestEngine(initial_capital=10_000.0)
        result = engine.run(df, strategy, "TEST")
        assert len(result.equity_curve) == len(prices)


class TestTrade:
    def test_return_pct(self):
        trade = Trade(
            entry_date=pd.Timestamp("2020-01-01"),
            exit_date=pd.Timestamp("2020-01-10"),
            symbol="TEST",
            side="LONG",
            entry_price=100.0,
            exit_price=120.0,
            size=10.0,
            pnl=200.0,
        )
        assert trade.return_pct == pytest.approx(0.2)

    def test_return_pct_none_if_open(self):
        trade = Trade(
            entry_date=pd.Timestamp("2020-01-01"),
            exit_date=None,
            symbol="TEST",
            side="LONG",
            entry_price=100.0,
            exit_price=None,
            size=10.0,
        )
        assert trade.return_pct is None
