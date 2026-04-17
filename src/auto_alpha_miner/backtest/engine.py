"""Backtest engine with next-bar execution to avoid look-ahead bias."""

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
    benchmark_equity: pd.Series | None = None
    total_commission: float = 0.0


class BacktestEngine:
    """Event-driven backtester with next-bar execution.

    Signals generated on bar[i] are executed at bar[i+1]'s Open price
    to avoid look-ahead bias.
    """

    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

    def run(self, df: pd.DataFrame, strategy: BaseStrategy, symbol: str) -> BacktestResult:
        """Run a backtest with next-bar execution.

        Signals are generated from the prepared data, but execution
        happens at the next bar's Open price to prevent look-ahead bias.
        """
        prepared = strategy.prepare(df.copy())
        signals = strategy.generate_signals(prepared)

        portfolio = Portfolio(
            self.initial_capital,
            commission_rate=self.commission_rate,
            slippage_rate=self.slippage_rate,
        )

        # Build signal lookup by date
        signal_map = {s.date: s for s in signals}

        # Track pending signal for next-bar execution
        pending_signal = None

        for date, row in prepared.iterrows():
            price = float(row["Close"])
            open_price = float(row["Open"]) if "Open" in row.index else price

            # Execute pending signal at this bar's Open
            if pending_signal is not None:
                if pending_signal.action == "BUY" and not portfolio.in_position:
                    portfolio.buy(date, open_price, symbol, fraction=pending_signal.size)
                elif pending_signal.action == "SELL" and portfolio.in_position:
                    if portfolio.position_side == "SHORT":
                        portfolio.cover(date, open_price, symbol)
                    else:
                        portfolio.sell(date, open_price, symbol)
                elif pending_signal.action == "SHORT" and not portfolio.in_position:
                    portfolio.short(date, open_price, symbol, fraction=pending_signal.size)
                pending_signal = None

            # Check for new signal (will execute next bar)
            sig = signal_map.get(date)
            if sig is not None:
                pending_signal = sig

            portfolio.record_equity(date, price)

        # Force close any open position at the end
        if portfolio.in_position:
            last_date = prepared.index[-1]
            last_price = float(prepared["Close"].iloc[-1])
            if portfolio.position_side == "SHORT":
                portfolio.cover(last_date, last_price, symbol)
            else:
                portfolio.sell(last_date, last_price, symbol)

        # Compute buy-and-hold benchmark
        benchmark_equity = self._compute_benchmark(prepared, self.initial_capital)

        return BacktestResult(
            symbol=symbol,
            strategy_name=strategy.name,
            equity_curve=portfolio.equity_curve,
            trades=portfolio.trades,
            prepared_df=prepared,
            benchmark_equity=benchmark_equity,
            total_commission=portfolio.total_commission,
        )

    @staticmethod
    def _compute_benchmark(df: pd.DataFrame, capital: float) -> pd.Series:
        """Compute buy-and-hold equity curve for benchmarking."""
        close = df["Close"]
        returns = close.pct_change().fillna(0.0)
        equity = capital * (1 + returns).cumprod()
        return equity
