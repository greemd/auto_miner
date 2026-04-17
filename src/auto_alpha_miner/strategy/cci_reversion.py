"""CCI (Commodity Channel Index) mean-reversion strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class CciReversionStrategy(BaseStrategy):
    """Mean-reversion using CCI: buy when oversold, sell when overbought."""

    name = "cci_reversion"

    def __init__(self, period: int = 20, oversold: float = -100, overbought: float = 100):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df["cci"] = ta.cci(df["High"], df["Low"], df["Close"], length=self.period)
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            cci = df["cci"].iloc[i]
            prev_cci = df["cci"].iloc[i - 1]

            if not in_position and prev_cci <= self.oversold and cci > self.oversold:
                signals.append(Signal(date=date, action="BUY"))
                in_position = True
            elif in_position and cci >= self.overbought:
                signals.append(Signal(date=date, action="SELL"))
                in_position = False

        return signals
