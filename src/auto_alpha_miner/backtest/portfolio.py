"""Portfolio position and cash tracking with commission support."""

from __future__ import annotations

import pandas as pd

from auto_alpha_miner.backtest.trade import Trade


class Portfolio:
    """Single-position portfolio tracker supporting LONG and SHORT."""

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.cash = initial_capital
        self.position_size: float = 0.0
        self.position_side: str = "LONG"
        self.position_entry_price: float = 0.0
        self.position_entry_date: pd.Timestamp | None = None
        self.trades: list[Trade] = []
        self.total_commission: float = 0.0
        self._equity_history: dict[pd.Timestamp, float] = {}

    @property
    def in_position(self) -> bool:
        return self.position_size > 0

    def _apply_slippage(self, price: float, is_buy: bool) -> float:
        """Apply slippage to execution price."""
        if is_buy:
            return price * (1 + self.slippage_rate)
        return price * (1 - self.slippage_rate)

    def record_equity(self, date: pd.Timestamp, price: float) -> None:
        """Record equity value at a given date."""
        if self.position_side == "SHORT" and self.in_position:
            # Short P&L: profit when price goes down
            unrealized = self.position_size * (self.position_entry_price - price)
            equity = self.cash + unrealized
        else:
            equity = self.cash + self.position_size * price
        self._equity_history[date] = equity

    def buy(self, date: pd.Timestamp, price: float, symbol: str, fraction: float = 1.0) -> Trade | None:
        """Open a long position using `fraction` of available cash."""
        if self.in_position:
            return None
        exec_price = self._apply_slippage(price, is_buy=True)
        invest = self.cash * fraction
        commission = invest * self.commission_rate
        net_invest = invest - commission
        size = net_invest / exec_price
        self.cash -= invest
        self.position_size = size
        self.position_side = "LONG"
        self.position_entry_price = exec_price
        self.position_entry_date = date
        self.total_commission += commission
        trade = Trade(
            entry_date=date,
            exit_date=None,
            symbol=symbol,
            side="LONG",
            entry_price=exec_price,
            exit_price=None,
            size=size,
            commission=commission,
        )
        return trade

    def sell(self, date: pd.Timestamp, price: float, symbol: str) -> Trade | None:
        """Close the current long position."""
        if not self.in_position or self.position_side != "LONG":
            return None
        exec_price = self._apply_slippage(price, is_buy=False)
        proceeds = self.position_size * exec_price
        commission = proceeds * self.commission_rate
        net_proceeds = proceeds - commission
        pnl = net_proceeds - self.position_size * self.position_entry_price
        self.total_commission += commission
        trade = Trade(
            entry_date=self.position_entry_date,  # type: ignore[arg-type]
            exit_date=date,
            symbol=symbol,
            side="LONG",
            entry_price=self.position_entry_price,
            exit_price=exec_price,
            size=self.position_size,
            pnl=pnl,
            commission=commission,
        )
        self.cash += net_proceeds
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_date = None
        self.trades.append(trade)
        return trade

    def short(self, date: pd.Timestamp, price: float, symbol: str, fraction: float = 1.0) -> Trade | None:
        """Open a short position using `fraction` of available cash as margin."""
        if self.in_position:
            return None
        exec_price = self._apply_slippage(price, is_buy=False)
        margin = self.cash * fraction
        commission = margin * self.commission_rate
        size = (margin - commission) / exec_price
        self.cash -= commission  # keep cash as collateral, deduct commission
        self.position_size = size
        self.position_side = "SHORT"
        self.position_entry_price = exec_price
        self.position_entry_date = date
        self.total_commission += commission
        trade = Trade(
            entry_date=date,
            exit_date=None,
            symbol=symbol,
            side="SHORT",
            entry_price=exec_price,
            exit_price=None,
            size=size,
            commission=commission,
        )
        return trade

    def cover(self, date: pd.Timestamp, price: float, symbol: str) -> Trade | None:
        """Close the current short position."""
        if not self.in_position or self.position_side != "SHORT":
            return None
        exec_price = self._apply_slippage(price, is_buy=True)
        cost = self.position_size * exec_price
        commission = cost * self.commission_rate
        pnl = self.position_size * (self.position_entry_price - exec_price) - commission
        self.total_commission += commission
        trade = Trade(
            entry_date=self.position_entry_date,  # type: ignore[arg-type]
            exit_date=date,
            symbol=symbol,
            side="SHORT",
            entry_price=self.position_entry_price,
            exit_price=exec_price,
            size=self.position_size,
            pnl=pnl,
            commission=commission,
        )
        self.cash += pnl  # return P&L to cash
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_date = None
        self.trades.append(trade)
        return trade

    @property
    def equity_curve(self) -> pd.Series:
        """Return equity curve as a pandas Series."""
        return pd.Series(self._equity_history, dtype=float).sort_index()
