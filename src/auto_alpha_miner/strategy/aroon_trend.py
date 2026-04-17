"""Aroon trend-following strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class AroonTrendStrategy(BaseStrategy):
    """Trend-following using Aroon indicator crossover."""

    name = "aroon_trend"

    def __init__(self, period: int = 25, threshold: float = 70):
        self.period = period
        self.threshold = threshold

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        aroon = ta.aroon(df["High"], df["Low"], length=self.period)
        if aroon is not None:
            df["aroon_up"] = aroon.iloc[:, 0]
            df["aroon_down"] = aroon.iloc[:, 1]
            df["aroon_osc"] = aroon.iloc[:, 2] if aroon.shape[1] > 2 else df["aroon_up"] - df["aroon_down"]
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            aroon_up = df["aroon_up"].iloc[i]
            aroon_down = df["aroon_down"].iloc[i]
            prev_up = df["aroon_up"].iloc[i - 1]
            prev_down = df["aroon_down"].iloc[i - 1]

            # Buy: Aroon Up crosses above threshold and above Aroon Down
            if not in_position:
                if aroon_up > self.threshold and prev_up <= prev_down and aroon_up > aroon_down:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True

            # Sell: Aroon Down crosses above threshold and above Aroon Up
            elif in_position:
                if aroon_down > self.threshold and aroon_down > aroon_up:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
