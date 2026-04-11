"""Moving average crossover strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class MovingAverageCrossStrategy(BaseStrategy):
    """Golden cross (buy) / Death cross (sell) using SMA."""

    name = "ma_cross"

    def __init__(self, fast_period: int = 50, slow_period: int = 200):
        self.fast_period = fast_period
        self.slow_period = slow_period

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = ta.sma(df["Close"], length=self.fast_period)
        slow = ta.sma(df["Close"], length=self.slow_period)
        if fast is not None:
            df["sma_fast"] = fast
        if slow is not None:
            df["sma_slow"] = slow
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            fast = df["sma_fast"].iloc[i]
            slow = df["sma_slow"].iloc[i]
            prev_fast = df["sma_fast"].iloc[i - 1]
            prev_slow = df["sma_slow"].iloc[i - 1]

            if not in_position and prev_fast <= prev_slow and fast > slow:
                signals.append(Signal(date=date, action="BUY"))
                in_position = True
            elif in_position and prev_fast >= prev_slow and fast < slow:
                signals.append(Signal(date=date, action="SELL"))
                in_position = False

        return signals
