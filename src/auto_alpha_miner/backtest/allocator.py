"""Portfolio allocation strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from auto_alpha_miner.backtest.engine import BacktestResult


class BaseAllocator(ABC):
    """Abstract base for capital allocation across symbols."""

    name: str = "base"

    @abstractmethod
    def allocate(
        self,
        results: dict[str, BacktestResult],
        as_of: pd.Timestamp | None = None,
    ) -> dict[str, float]:
        """Return weight per symbol (should sum to ~1.0)."""
        ...


class EqualWeightAllocator(BaseAllocator):
    """Allocate capital equally across all symbols."""

    name = "equal"

    def allocate(
        self,
        results: dict[str, BacktestResult],
        as_of: pd.Timestamp | None = None,
    ) -> dict[str, float]:
        n = len(results)
        if n == 0:
            return {}
        weight = 1.0 / n
        return {symbol: weight for symbol in results}


class MomentumAllocator(BaseAllocator):
    """Allocate based on recent momentum (trailing return).

    Higher recent return = higher weight. Symbols with negative
    momentum get zero weight.
    """

    name = "momentum"

    def __init__(self, lookback_days: int = 63):
        self.lookback_days = lookback_days

    def allocate(
        self,
        results: dict[str, BacktestResult],
        as_of: pd.Timestamp | None = None,
    ) -> dict[str, float]:
        if not results:
            return {}

        scores: dict[str, float] = {}
        for symbol, result in results.items():
            ec = result.equity_curve
            if as_of is not None:
                ec = ec[ec.index <= as_of]
            if len(ec) < 2:
                scores[symbol] = 0.0
                continue
            lookback = min(self.lookback_days, len(ec) - 1)
            momentum = ec.iloc[-1] / ec.iloc[-lookback - 1] - 1.0
            scores[symbol] = max(momentum, 0.0)  # zero out negative momentum

        total = sum(scores.values())
        if total == 0:
            # Fall back to equal weight if all negative
            n = len(results)
            return {s: 1.0 / n for s in results}

        return {s: v / total for s, v in scores.items()}


class RiskParityAllocator(BaseAllocator):
    """Allocate inversely proportional to volatility (risk parity).

    Lower volatility = higher weight, so each position contributes
    roughly equal risk.
    """

    name = "risk_parity"

    def __init__(self, lookback_days: int = 63):
        self.lookback_days = lookback_days

    def allocate(
        self,
        results: dict[str, BacktestResult],
        as_of: pd.Timestamp | None = None,
    ) -> dict[str, float]:
        if not results:
            return {}

        inv_vols: dict[str, float] = {}
        for symbol, result in results.items():
            ec = result.equity_curve
            if as_of is not None:
                ec = ec[ec.index <= as_of]
            if len(ec) < 2:
                inv_vols[symbol] = 0.0
                continue
            lookback = min(self.lookback_days, len(ec) - 1)
            returns = ec.iloc[-lookback:].pct_change().dropna()
            vol = returns.std()
            inv_vols[symbol] = 1.0 / vol if vol > 0 else 0.0

        total = sum(inv_vols.values())
        if total == 0:
            n = len(results)
            return {s: 1.0 / n for s in results}

        return {s: v / total for s, v in inv_vols.items()}


ALLOCATOR_REGISTRY: dict[str, type[BaseAllocator]] = {
    "equal": EqualWeightAllocator,
    "momentum": MomentumAllocator,
    "risk_parity": RiskParityAllocator,
}
