"""Tests for evaluation metrics with known equity curves."""

import pandas as pd
import numpy as np
import pytest

from auto_alpha_miner.evaluation.metrics import (
    total_return,
    cagr,
    max_drawdown,
    sharpe_ratio,
    win_rate,
    profit_factor,
    trade_count,
    evaluate,
)
from auto_alpha_miner.backtest.trade import Trade
from auto_alpha_miner.backtest.engine import BacktestResult


def make_equity_curve(values: list[float], start: str = "2020-01-01") -> pd.Series:
    dates = pd.bdate_range(start, periods=len(values))
    return pd.Series(values, index=dates, dtype=float)


def make_trade(pnl: float) -> Trade:
    return Trade(
        entry_date=pd.Timestamp("2020-01-01"),
        exit_date=pd.Timestamp("2020-01-10"),
        symbol="TEST",
        side="LONG",
        entry_price=100.0,
        exit_price=100.0 + pnl,
        size=1.0,
        pnl=pnl,
    )


class TestTotalReturn:
    def test_positive_return(self):
        ec = make_equity_curve([100.0, 110.0, 120.0, 150.0])
        assert total_return(ec) == pytest.approx(0.5)

    def test_negative_return(self):
        ec = make_equity_curve([100.0, 90.0, 80.0])
        assert total_return(ec) == pytest.approx(-0.2)

    def test_empty_curve(self):
        ec = make_equity_curve([100.0])
        assert total_return(ec) == 0.0


class TestCAGR:
    def test_one_year_double(self):
        # 100 -> 200 over ~1 year (252 business days)
        values = np.linspace(100, 200, 252).tolist()
        ec = make_equity_curve(values)
        result = cagr(ec)
        assert result == pytest.approx(1.0, rel=0.1)  # ~100% CAGR


class TestMaxDrawdown:
    def test_known_drawdown(self):
        ec = make_equity_curve([100.0, 120.0, 90.0, 110.0])
        # Peak at 120, trough at 90 => dd = 30/120 = 25%
        assert max_drawdown(ec) == pytest.approx(0.25)

    def test_no_drawdown(self):
        ec = make_equity_curve([100.0, 110.0, 120.0, 130.0])
        assert max_drawdown(ec) == pytest.approx(0.0)


class TestSharpeRatio:
    def test_positive_sharpe(self):
        # Steadily increasing equity => positive Sharpe
        ec = make_equity_curve(list(np.linspace(100, 150, 252)))
        assert sharpe_ratio(ec) > 0

    def test_flat_equity(self):
        ec = make_equity_curve([100.0] * 10)
        assert sharpe_ratio(ec) == 0.0


class TestWinRate:
    def test_all_winners(self):
        trades = [make_trade(10.0), make_trade(20.0)]
        assert win_rate(trades) == pytest.approx(1.0)

    def test_mixed(self):
        trades = [make_trade(10.0), make_trade(-5.0)]
        assert win_rate(trades) == pytest.approx(0.5)

    def test_empty(self):
        assert win_rate([]) == 0.0


class TestProfitFactor:
    def test_two_to_one(self):
        trades = [make_trade(20.0), make_trade(-10.0)]
        assert profit_factor(trades) == pytest.approx(2.0)

    def test_no_losses(self):
        trades = [make_trade(10.0)]
        assert profit_factor(trades) == float("inf")


class TestEvaluate:
    def test_returns_all_keys(self):
        ec = make_equity_curve(list(np.linspace(100, 150, 50)))
        trades = [make_trade(10.0), make_trade(-5.0)]
        result = BacktestResult(
            symbol="TEST",
            strategy_name="test",
            equity_curve=ec,
            trades=trades,
            prepared_df=pd.DataFrame(),
        )
        metrics = evaluate(result)
        expected_keys = {"total_return", "cagr", "max_drawdown", "sharpe_ratio", "win_rate", "profit_factor", "trade_count"}
        assert set(metrics.keys()) == expected_keys
