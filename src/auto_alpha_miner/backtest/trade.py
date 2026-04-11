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
    side: Literal["LONG"]
    entry_price: float
    exit_price: float | None
    size: float
    pnl: float | None = None

    @property
    def return_pct(self) -> float | None:
        if self.exit_price is None:
            return None
        return (self.exit_price - self.entry_price) / self.entry_price
