"""MACD signal crossover strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class MacdSignalStrategy(BaseStrategy):
    """MACD histogram crossover with signal line confirmation."""

    name = "macd_signal"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        macd_df = ta.macd(df["Close"], fast=self.fast, slow=self.slow, signal=self.signal)
        if macd_df is not None:
            df["macd"] = macd_df.iloc[:, 0]       # MACD line
            df["macd_hist"] = macd_df.iloc[:, 1]   # Histogram
            df["macd_signal"] = macd_df.iloc[:, 2]  # Signal line
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            macd = df["macd"].iloc[i]
            signal = df["macd_signal"].iloc[i]
            prev_macd = df["macd"].iloc[i - 1]
            prev_signal = df["macd_signal"].iloc[i - 1]
            hist = df["macd_hist"].iloc[i]

            # Buy: MACD crosses above signal line and histogram is positive
            if not in_position:
                if prev_macd <= prev_signal and macd > signal and hist > 0:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True

            # Sell: MACD crosses below signal line
            elif in_position:
                if prev_macd >= prev_signal and macd < signal:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
