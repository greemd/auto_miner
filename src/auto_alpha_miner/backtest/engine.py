"""Backtest engine."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from auto_alpha_miner.backtest.portfolio import Portfolio
from auto_alpha_miner.backtest.trade import Trade
from auto_alpha_miner.strategy.base import BaseStrategy


@dataclass
class BacktestResult:
    """Result of a backtest run."""

    symbol: str
    strategy_name: str
    equity_curve: pd.Series
    trades: list[Trade]
    prepared_df: pd.DataFrame


class BacktestEngine:
    """Simple event-driven backtester."""

    def __init__(self, initial_capital: float = 100_000.0):
        self.initial_capital = initial_capital

    def run(self, df: pd.DataFrame, strategy: BaseStrategy, symbol: str) -> BacktestResult:
        """Run a backtest.

        Args:
            df: OHLCV DataFrame (must have Close column, DatetimeIndex).
            strategy: A BaseStrategy instance.
            symbol: Symbol name for labeling trades.

        Returns:
            BacktestResult with equity curve, trades, and prepared DataFrame.
        """
        prepared = strategy.prepare(df.copy())
        signals = strategy.generate_signals(prepared)

        portfolio = Portfolio(self.initial_capital)

        # Build signal lookup by date
        signal_map = {s.date: s for s in signals}

        for date, row in prepared.iterrows():
            price = float(row["Close"])
            sig = signal_map.get(date)

            if sig is not None:
                if sig.action == "BUY" and not portfolio.in_position:
                    portfolio.buy(date, price, symbol, fraction=sig.size)
                elif sig.action == "SELL" and portfolio.in_position:
                    portfolio.sell(date, price, symbol)

            portfolio.record_equity(date, price)

        # Force close any open position at the end
        if portfolio.in_position:
            last_date = prepared.index[-1]
            last_price = float(prepared["Close"].iloc[-1])
            portfolio.sell(last_date, last_price, symbol)

        return BacktestResult(
            symbol=symbol,
            strategy_name=strategy.name,
            equity_curve=portfolio.equity_curve,
            trades=portfolio.trades,
            prepared_df=prepared,
        )
