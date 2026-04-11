"""Performance metrics for strategy evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from auto_alpha_miner.backtest.engine import BacktestResult
from auto_alpha_miner.backtest.trade import Trade


def total_return(equity_curve: pd.Series) -> float:
    """Total return as a ratio (e.g., 0.5 = 50%)."""
    if len(equity_curve) < 2:
        return 0.0
    return (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1.0


def cagr(equity_curve: pd.Series) -> float:
    """Compound annual growth rate."""
    if len(equity_curve) < 2:
        return 0.0
    days = (equity_curve.index[-1] - equity_curve.index[0]).days
    if days <= 0:
        return 0.0
    total = equity_curve.iloc[-1] / equity_curve.iloc[0]
    return float(total ** (365.0 / days) - 1.0)


def max_drawdown(equity_curve: pd.Series) -> float:
    """Maximum drawdown as a positive ratio (e.g., 0.2 = 20% drawdown)."""
    if len(equity_curve) < 2:
        return 0.0
    cummax = equity_curve.cummax()
    drawdown = (cummax - equity_curve) / cummax
    return float(drawdown.max())


def sharpe_ratio(equity_curve: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """Annualized Sharpe ratio from daily equity curve."""
    if len(equity_curve) < 2:
        return 0.0
    returns = equity_curve.pct_change().dropna()
    if returns.std() == 0:
        return 0.0
    excess = returns.mean() - risk_free_rate / periods_per_year
    return float(excess / returns.std() * np.sqrt(periods_per_year))


def win_rate(trades: list[Trade]) -> float:
    """Fraction of profitable trades."""
    closed = [t for t in trades if t.pnl is not None]
    if not closed:
        return 0.0
    winners = sum(1 for t in closed if t.pnl > 0)  # type: ignore[operator]
    return winners / len(closed)


def profit_factor(trades: list[Trade]) -> float:
    """Gross profit / gross loss. Returns inf if no losing trades."""
    closed = [t for t in trades if t.pnl is not None]
    gross_profit = sum(t.pnl for t in closed if t.pnl > 0)  # type: ignore[operator]
    gross_loss = abs(sum(t.pnl for t in closed if t.pnl < 0))  # type: ignore[operator]
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def trade_count(trades: list[Trade]) -> int:
    """Number of closed trades."""
    return len([t for t in trades if t.pnl is not None])


def evaluate(result: BacktestResult) -> dict[str, float]:
    """Compute all metrics for a backtest result."""
    ec = result.equity_curve
    return {
        "total_return": total_return(ec),
        "cagr": cagr(ec),
        "max_drawdown": max_drawdown(ec),
        "sharpe_ratio": sharpe_ratio(ec),
        "win_rate": win_rate(result.trades),
        "profit_factor": profit_factor(result.trades),
        "trade_count": float(trade_count(result.trades)),
    }


def evaluate_portfolio(result) -> dict[str, float]:
    """Compute metrics for a multi-symbol PortfolioResult."""
    from auto_alpha_miner.backtest.multi_engine import PortfolioResult

    pr: PortfolioResult = result
    ec = pr.combined_equity

    # Aggregate all trades across symbols
    all_trades: list[Trade] = []
    for sr in pr.symbol_results.values():
        all_trades.extend(sr.trades)

    return {
        "total_return": total_return(ec),
        "cagr": cagr(ec),
        "max_drawdown": max_drawdown(ec),
        "sharpe_ratio": sharpe_ratio(ec),
        "win_rate": win_rate(all_trades),
        "profit_factor": profit_factor(all_trades),
        "trade_count": float(trade_count(all_trades)),
    }
