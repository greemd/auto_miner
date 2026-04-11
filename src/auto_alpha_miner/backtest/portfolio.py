"""Portfolio position and cash tracking."""

from __future__ import annotations

import pandas as pd

from auto_alpha_miner.backtest.trade import Trade


class Portfolio:
    """Single-position long-only portfolio tracker."""

    def __init__(self, initial_capital: float = 100_000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position_size: float = 0.0
        self.position_entry_price: float = 0.0
        self.position_entry_date: pd.Timestamp | None = None
        self.trades: list[Trade] = []
        self._equity_history: dict[pd.Timestamp, float] = {}

    @property
    def in_position(self) -> bool:
        return self.position_size > 0

    def record_equity(self, date: pd.Timestamp, price: float) -> None:
        """Record equity value at a given date."""
        equity = self.cash + self.position_size * price
        self._equity_history[date] = equity

    def buy(self, date: pd.Timestamp, price: float, symbol: str, fraction: float = 1.0) -> Trade | None:
        """Open a long position using `fraction` of available cash."""
        if self.in_position:
            return None
        invest = self.cash * fraction
        size = invest / price
        self.cash -= invest
        self.position_size = size
        self.position_entry_price = price
        self.position_entry_date = date
        trade = Trade(
            entry_date=date,
            exit_date=None,
            symbol=symbol,
            side="LONG",
            entry_price=price,
            exit_price=None,
            size=size,
        )
        return trade

    def sell(self, date: pd.Timestamp, price: float, symbol: str) -> Trade | None:
        """Close the current position."""
        if not self.in_position:
            return None
        proceeds = self.position_size * price
        pnl = proceeds - self.position_size * self.position_entry_price
        trade = Trade(
            entry_date=self.position_entry_date,  # type: ignore[arg-type]
            exit_date=date,
            symbol=symbol,
            side="LONG",
            entry_price=self.position_entry_price,
            exit_price=price,
            size=self.position_size,
            pnl=pnl,
        )
        self.cash += proceeds
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_date = None
        self.trades.append(trade)
        return trade

    @property
    def equity_curve(self) -> pd.Series:
        """Return equity curve as a pandas Series."""
        return pd.Series(self._equity_history, dtype=float).sort_index()
