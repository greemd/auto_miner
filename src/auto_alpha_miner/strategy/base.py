"""Base strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal

import pandas as pd


@dataclass
class Signal:
    """A trading signal emitted by a strategy."""

    date: pd.Timestamp
    action: Literal["BUY", "SELL", "HOLD"]
    size: float = 1.0  # fraction of capital (0.0 to 1.0)
    metadata: dict = field(default_factory=dict)


def atr_position_size(
    df: pd.DataFrame,
    index: int,
    risk_pct: float = 0.02,
    atr_period: int = 14,
) -> float:
    """Calculate position size based on ATR risk.

    Returns fraction of capital to risk (capped at 1.0).
    Risk is defined as risk_pct of capital per ATR unit.
    """
    if index < atr_period:
        return 1.0
    high = df["High"].iloc[index - atr_period:index]
    low = df["Low"].iloc[index - atr_period:index]
    close = df["Close"].iloc[index - atr_period:index]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    atr = tr.mean()
    if atr == 0:
        return 1.0
    price = df["Close"].iloc[index]
    # How many units can we buy with risk_pct of capital
    # fraction = risk_pct * capital / (atr * price) * price / capital = risk_pct / (atr / price)
    fraction = risk_pct / (atr / price)
    return min(fraction, 1.0)


class BaseStrategy(ABC):
    """Abstract base class for trading strategies.

    Subclasses must:
    1. Set a `name` class attribute.
    2. Implement `prepare()` to add indicator columns.
    3. Implement `generate_signals()` to produce trading signals.
    """

    name: str = "base"

    @abstractmethod
    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add indicator columns to the OHLCV DataFrame. Returns augmented copy."""
        ...

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        """Generate signals from a prepared DataFrame."""
        ...
