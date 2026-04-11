"""Portfolio allocation strategy: Equal Weight."""

from __future__ import annotations

from abc import ABC, abstractmethod

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
        """Return weight per symbol (should sum to ~1.0).

        Args:
            results: Per-symbol backtest results.
            as_of: If provided, only use data up to this date for calculation.
        """
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


ALLOCATOR_REGISTRY: dict[str, type[BaseAllocator]] = {
    "equal": EqualWeightAllocator,
}
