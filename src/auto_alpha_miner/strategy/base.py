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
    size: float = 1.0
    metadata: dict = field(default_factory=dict)


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
