"""RSI mean-reversion strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class RSIDivergenceStrategy(BaseStrategy):
    """Buy on RSI oversold bounce, sell on overbought reversal."""

    name = "rsi"

    def __init__(self, period: int = 14, oversold: float = 30.0, overbought: float = 70.0):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        rsi = ta.rsi(df["Close"], length=self.period)
        if rsi is not None:
            df["rsi"] = rsi
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            rsi = df["rsi"].iloc[i]
            prev_rsi = df["rsi"].iloc[i - 1]

            if not in_position and prev_rsi <= self.oversold and rsi > self.oversold:
                signals.append(Signal(date=date, action="BUY"))
                in_position = True
            elif in_position and prev_rsi >= self.overbought and rsi < self.overbought:
                signals.append(Signal(date=date, action="SELL"))
                in_position = False

        return signals
