"""Text and chart reporting for backtest results."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from auto_alpha_miner.backtest.engine import BacktestResult
from auto_alpha_miner.backtest.multi_engine import PortfolioResult


def print_report(result: BacktestResult, metrics: dict[str, float]) -> None:
    """Print a formatted text report to stdout."""
    print(f"\n{'=' * 60}")
    print(f"  Strategy: {result.strategy_name}")
    print(f"  Symbol:   {result.symbol}")
    print(f"  Period:   {result.equity_curve.index[0].date()} ~ {result.equity_curve.index[-1].date()}")
    print(f"{'=' * 60}")
    print(f"  Total Return:   {metrics['total_return']:>10.2%}")
    print(f"  CAGR:           {metrics['cagr']:>10.2%}")
    print(f"  Max Drawdown:   {metrics['max_drawdown']:>10.2%}")
    print(f"  Sharpe Ratio:   {metrics['sharpe_ratio']:>10.2f}")
    print(f"  Win Rate:       {metrics['win_rate']:>10.2%}")
    print(f"  Profit Factor:  {metrics['profit_factor']:>10.2f}")
    print(f"  Trade Count:    {metrics['trade_count']:>10.0f}")
    print(f"{'=' * 60}\n")


def plot_report(
    result: BacktestResult,
    metrics: dict[str, float],
    save_path: str | None = None,
) -> None:
    """Generate matplotlib figure with equity curve and drawdown."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True, gridspec_kw={"height_ratios": [3, 1]})

    # Equity curve
    ax1 = axes[0]
    result.equity_curve.plot(ax=ax1, color="steelblue", linewidth=1.5)
    ax1.set_title(f"{result.strategy_name} | {result.symbol}", fontsize=14)
    ax1.set_ylabel("Equity")
    ax1.grid(True, alpha=0.3)

    # Mark trades
    for trade in result.trades:
        ax1.axvline(trade.entry_date, color="green", alpha=0.3, linestyle="--", linewidth=0.8)
        if trade.exit_date:
            ax1.axvline(trade.exit_date, color="red", alpha=0.3, linestyle="--", linewidth=0.8)

    # Drawdown
    ax2 = axes[1]
    cummax = result.equity_curve.cummax()
    drawdown = (result.equity_curve - cummax) / cummax
    drawdown.plot(ax=ax2, color="crimson", linewidth=1.0)
    ax2.fill_between(drawdown.index, drawdown.values, 0, color="crimson", alpha=0.2)
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    # Add metrics text box
    text = (
        f"Return: {metrics['total_return']:.2%}  |  "
        f"CAGR: {metrics['cagr']:.2%}  |  "
        f"MDD: {metrics['max_drawdown']:.2%}  |  "
        f"Sharpe: {metrics['sharpe_ratio']:.2f}  |  "
        f"Trades: {metrics['trade_count']:.0f}"
    )
    fig.text(0.5, 0.01, text, ha="center", fontsize=10, style="italic")

    plt.tight_layout(rect=[0, 0.03, 1, 1])

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Chart saved to {save_path}")
    else:
        plt.show()


def print_portfolio_report(result: PortfolioResult, metrics: dict[str, float]) -> None:
    """Print a formatted portfolio report to stdout."""
    ec = result.combined_equity
    rebal_label = {"W": "weekly", "M": "monthly", "Q": "quarterly"}.get(result.rebalance_frequency, "fixed")
    print(f"\n{'=' * 60}")
    print(f"  Strategy:    {result.strategy_name}")
    print(f"  Allocation:  {result.allocator_name} ({rebal_label} rebalancing)")
    print(f"  Symbols:     {', '.join(result.symbol_results.keys())}")
    print(f"  Period:      {ec.index[0].date()} ~ {ec.index[-1].date()}")
    print(f"{'=' * 60}")
    print(f"  Total Return:   {metrics['total_return']:>10.2%}")
    print(f"  CAGR:           {metrics['cagr']:>10.2%}")
    print(f"  Max Drawdown:   {metrics['max_drawdown']:>10.2%}")
    print(f"  Sharpe Ratio:   {metrics['sharpe_ratio']:>10.2f}")
    print(f"  Win Rate:       {metrics['win_rate']:>10.2%}")
    print(f"  Profit Factor:  {metrics['profit_factor']:>10.2f}")
    print(f"  Trade Count:    {metrics['trade_count']:>10.0f}")
    print(f"{'=' * 60}")
    print(f"  Final Weights:")
    for sym, w in result.weights.items():
        print(f"    {sym:12s}  {w:>6.1%}")
    if result.weight_history and len(result.weight_history) > 1:
        print(f"  Rebalances:  {len(result.weight_history)} times")
    print(f"{'=' * 60}\n")


def plot_portfolio_report(
    result: PortfolioResult,
    metrics: dict[str, float],
    save_path: str | None = None,
) -> None:
    """Generate matplotlib figure for portfolio: combined + per-symbol equity."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True, gridspec_kw={"height_ratios": [3, 1]})

    ax1 = axes[0]
    # Combined equity
    result.combined_equity.plot(ax=ax1, color="black", linewidth=2.0, label="Portfolio")
    # Per-symbol equity (normalized to same start)
    for sym, sr in result.symbol_results.items():
        normalized = sr.equity_curve / sr.equity_curve.iloc[0] * result.combined_equity.iloc[0]
        normalized.plot(ax=ax1, linewidth=0.8, alpha=0.5, label=sym)

    ax1.set_title(f"Portfolio: {result.strategy_name} | {result.allocator_name} allocation", fontsize=14)
    ax1.set_ylabel("Equity")
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.3)

    # Drawdown
    ax2 = axes[1]
    cummax = result.combined_equity.cummax()
    drawdown = (result.combined_equity - cummax) / cummax
    drawdown.plot(ax=ax2, color="crimson", linewidth=1.0)
    ax2.fill_between(drawdown.index, drawdown.values, 0, color="crimson", alpha=0.2)
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Date")
    ax2.grid(True, alpha=0.3)

    text = (
        f"Return: {metrics['total_return']:.2%}  |  "
        f"CAGR: {metrics['cagr']:.2%}  |  "
        f"MDD: {metrics['max_drawdown']:.2%}  |  "
        f"Sharpe: {metrics['sharpe_ratio']:.2f}  |  "
        f"Trades: {metrics['trade_count']:.0f}"
    )
    fig.text(0.5, 0.01, text, ha="center", fontsize=10, style="italic")

    plt.tight_layout(rect=[0, 0.03, 1, 1])

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Chart saved to {save_path}")
    else:
        plt.show()
