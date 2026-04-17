"""Trade data class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class Trade:
    """A single executed trade."""

    entry_date: pd.Timestamp
    exit_date: pd.Timestamp | None
    symbol: str
    side: Literal["LONG", "SHORT"]
    entry_price: float
    exit_price: float | None
    size: float
    pnl: float | None = None
    commission: float = 0.0

    @property
    def return_pct(self) -> float | None:
        if self.exit_price is None:
            return None
        if self.side == "SHORT":
            return (self.entry_price - self.exit_price) / self.entry_price
        return (self.exit_price - self.entry_price) / self.entry_price
