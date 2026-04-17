"""Performance metrics for strategy evaluation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from auto_alpha_miner.backtest.engine import BacktestResult
from auto_alpha_miner.backtest.trade import Trade

# Approximate US 10Y treasury average for 2010-2024
DEFAULT_RISK_FREE_RATE = 0.03


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


def max_drawdown_duration(equity_curve: pd.Series) -> int:
    """Maximum drawdown duration in calendar days."""
    if len(equity_curve) < 2:
        return 0
    cummax = equity_curve.cummax()
    underwater = equity_curve < cummax

    max_duration = 0
    current_start = None

    for i, (date, is_underwater) in enumerate(underwater.items()):
        if is_underwater:
            if current_start is None:
                current_start = date
        else:
            if current_start is not None:
                duration = (date - current_start).days
                max_duration = max(max_duration, duration)
                current_start = None

    # Check if still in drawdown at end
    if current_start is not None:
        duration = (equity_curve.index[-1] - current_start).days
        max_duration = max(max_duration, duration)

    return max_duration


def sharpe_ratio(
    equity_curve: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252,
) -> float:
    """Annualized Sharpe ratio from daily equity curve."""
    if len(equity_curve) < 2:
        return 0.0
    returns = equity_curve.pct_change().dropna()
    if returns.std() == 0:
        return 0.0
    excess = returns.mean() - risk_free_rate / periods_per_year
    return float(excess / returns.std() * np.sqrt(periods_per_year))


def sortino_ratio(
    equity_curve: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252,
) -> float:
    """Annualized Sortino ratio (penalizes only downside volatility)."""
    if len(equity_curve) < 2:
        return 0.0
    returns = equity_curve.pct_change().dropna()
    daily_rf = risk_free_rate / periods_per_year
    excess = returns - daily_rf
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return 0.0
    downside_std = downside.std()
    return float(excess.mean() / downside_std * np.sqrt(periods_per_year))


def calmar_ratio(equity_curve: pd.Series) -> float:
    """Calmar ratio: CAGR / Max Drawdown."""
    mdd = max_drawdown(equity_curve)
    if mdd == 0:
        return 0.0
    return cagr(equity_curve) / mdd


def alpha_beta(
    equity_curve: pd.Series,
    benchmark_curve: pd.Series,
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    periods_per_year: int = 252,
) -> tuple[float, float]:
    """Compute annualized alpha and beta vs benchmark.

    Returns (alpha, beta).
    """
    if len(equity_curve) < 2 or benchmark_curve is None or len(benchmark_curve) < 2:
        return 0.0, 0.0

    # Align indices
    common = equity_curve.index.intersection(benchmark_curve.index)
    if len(common) < 2:
        return 0.0, 0.0

    strat_returns = equity_curve.loc[common].pct_change().dropna()
    bench_returns = benchmark_curve.loc[common].pct_change().dropna()

    # Align after dropna
    common_idx = strat_returns.index.intersection(bench_returns.index)
    strat_returns = strat_returns.loc[common_idx]
    bench_returns = bench_returns.loc[common_idx]

    if len(strat_returns) < 2:
        return 0.0, 0.0

    bench_var = bench_returns.var()
    if bench_var == 0:
        return 0.0, 0.0

    # Beta = Cov(strat, bench) / Var(bench)
    beta = float(strat_returns.cov(bench_returns) / bench_var)

    # Alpha = annualized(strat_mean - rf - beta * (bench_mean - rf))
    daily_rf = risk_free_rate / periods_per_year
    alpha = float((strat_returns.mean() - daily_rf - beta * (bench_returns.mean() - daily_rf)) * periods_per_year)

    return alpha, beta


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
    bench = result.benchmark_equity

    a, b = alpha_beta(ec, bench) if bench is not None else (0.0, 0.0)

    # Benchmark metrics for comparison
    bench_sharpe = sharpe_ratio(bench) if bench is not None and len(bench) > 1 else 0.0
    bench_return = total_return(bench) if bench is not None and len(bench) > 1 else 0.0

    return {
        "total_return": total_return(ec),
        "cagr": cagr(ec),
        "max_drawdown": max_drawdown(ec),
        "max_dd_duration_days": float(max_drawdown_duration(ec)),
        "sharpe_ratio": sharpe_ratio(ec),
        "sortino_ratio": sortino_ratio(ec),
        "calmar_ratio": calmar_ratio(ec),
        "alpha": a,
        "beta": b,
        "win_rate": win_rate(result.trades),
        "profit_factor": profit_factor(result.trades),
        "trade_count": float(trade_count(result.trades)),
        "total_commission": result.total_commission,
        "benchmark_return": bench_return,
        "benchmark_sharpe": bench_sharpe,
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
        "max_dd_duration_days": float(max_drawdown_duration(ec)),
        "sharpe_ratio": sharpe_ratio(ec),
        "sortino_ratio": sortino_ratio(ec),
        "calmar_ratio": calmar_ratio(ec),
        "alpha": 0.0,
        "beta": 0.0,
        "win_rate": win_rate(all_trades),
        "profit_factor": profit_factor(all_trades),
        "trade_count": float(trade_count(all_trades)),
    }
