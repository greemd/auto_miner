"""Multi-symbol portfolio backtesting with periodic rebalancing."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from auto_alpha_miner.backtest.allocator import BaseAllocator
from auto_alpha_miner.backtest.engine import BacktestEngine, BacktestResult


@dataclass
class PortfolioResult:
    """Result of a multi-symbol portfolio backtest."""

    strategy_name: str
    allocator_name: str
    weights: dict[str, float]
    symbol_results: dict[str, BacktestResult]
    combined_equity: pd.Series
    rebalance_frequency: str | None = None
    weight_history: list[tuple[pd.Timestamp, dict[str, float]]] = field(default_factory=list)


class MultiSymbolEngine:
    """Run a strategy across multiple symbols and combine with an allocator."""

    def __init__(self, initial_capital: float = 100_000.0):
        self.initial_capital = initial_capital

    def run(
        self,
        data: dict[str, pd.DataFrame],
        strategy_cls: type,
        allocator: BaseAllocator,
        rebalance: str | None = None,
    ) -> PortfolioResult:
        """Run backtest on all symbols, then combine with allocation weights.

        Args:
            data: Dict of symbol -> OHLCV DataFrame.
            strategy_cls: Strategy class to instantiate per symbol.
            allocator: Allocator instance to determine weights.
            rebalance: Rebalancing frequency — None (fixed), "M" (monthly),
                       "Q" (quarterly), "W" (weekly). Uses pandas offset aliases.

        Returns:
            PortfolioResult with per-symbol results and combined equity.
        """
        engine = BacktestEngine(initial_capital=self.initial_capital)

        # Run individual backtests
        symbol_results: dict[str, BacktestResult] = {}
        for symbol, df in data.items():
            strat = strategy_cls()
            result = engine.run(df, strat, symbol)
            symbol_results[symbol] = result

        if rebalance is None:
            # Fixed weights (original behavior)
            weights = allocator.allocate(symbol_results)
            combined_equity = self._combine_equity_fixed(symbol_results, weights)
            weight_history = [(combined_equity.index[0], weights)]
        else:
            # Periodic rebalancing
            combined_equity, weights, weight_history = self._combine_equity_rebalanced(
                symbol_results, allocator, rebalance
            )

        return PortfolioResult(
            strategy_name=strategy_cls.name,
            allocator_name=allocator.name,
            weights=weights,
            symbol_results=symbol_results,
            combined_equity=combined_equity,
            rebalance_frequency=rebalance,
            weight_history=weight_history,
        )

    def _combine_equity_fixed(
        self,
        results: dict[str, BacktestResult],
        weights: dict[str, float],
    ) -> pd.Series:
        """Combine per-symbol equity curves with fixed weights."""
        returns_df = self._build_returns_df(results)

        weighted_returns = pd.Series(0.0, index=returns_df.index)
        for symbol in results:
            w = weights.get(symbol, 0.0)
            weighted_returns += returns_df[symbol] * w

        equity = self.initial_capital * (1 + weighted_returns).cumprod()
        return equity

    def _combine_equity_rebalanced(
        self,
        results: dict[str, BacktestResult],
        allocator: BaseAllocator,
        frequency: str,
    ) -> tuple[pd.Series, dict[str, float], list[tuple[pd.Timestamp, dict[str, float]]]]:
        """Combine per-symbol equity curves with periodic rebalancing.

        At each rebalancing date, recalculate weights using the allocator
        based on equity history up to that point.
        """
        returns_df = self._build_returns_df(results)

        # Determine rebalancing dates
        rebal_dates_set = self._get_rebalance_dates(returns_df.index, frequency)

        # Walk through time, applying weights per period
        equity_values = []
        current_equity = self.initial_capital
        weight_history: list[tuple[pd.Timestamp, dict[str, float]]] = []
        current_weights: dict[str, float] = {}

        # Start with initial weights from first rebalance date
        first_rebal = min(rebal_dates_set) if rebal_dates_set else returns_df.index[0]
        current_weights = allocator.allocate(results, as_of=first_rebal)
        weight_history.append((first_rebal, current_weights.copy()))

        for date in returns_df.index:
            # Check if we should rebalance
            if date in rebal_dates_set and date != first_rebal:
                current_weights = allocator.allocate(results, as_of=date)
                weight_history.append((date, current_weights.copy()))

            # Compute weighted return for this day
            day_return = 0.0
            for symbol in results:
                w = current_weights.get(symbol, 0.0)
                day_return += returns_df.at[date, symbol] * w

            current_equity *= (1 + day_return)
            equity_values.append(current_equity)

        equity = pd.Series(equity_values, index=returns_df.index)

        # Final weights are the last computed weights
        final_weights = current_weights

        return equity, final_weights, weight_history

    def _build_returns_df(self, results: dict[str, BacktestResult]) -> pd.DataFrame:
        """Build aligned daily returns DataFrame from per-symbol equity curves."""
        all_returns: dict[str, pd.Series] = {}
        for symbol, result in results.items():
            ec = result.equity_curve
            returns = ec.pct_change().fillna(0.0)
            all_returns[symbol] = returns

        returns_df = pd.DataFrame(all_returns)
        returns_df = returns_df.fillna(0.0)
        return returns_df

    def _get_rebalance_dates(
        self, index: pd.DatetimeIndex, frequency: str
    ) -> set[pd.Timestamp]:
        """Get set of rebalancing dates from a DatetimeIndex.

        Each rebalancing happens on the last trading day of the period.
        """
        # Group by period, take the last date in each group
        if frequency == "W":
            groups = index.to_series().groupby(index.to_period("W"))
        elif frequency == "M":
            groups = index.to_series().groupby(index.to_period("M"))
        elif frequency == "Q":
            groups = index.to_series().groupby(index.to_period("Q"))
        else:
            raise ValueError(f"Unknown rebalance frequency: {frequency}. Use W, M, or Q.")

        rebal_dates = set()
        for _, group in groups:
            rebal_dates.add(group.iloc[-1])

        return rebal_dates
