"""Turtle Trading strategy — Donchian channel breakout."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class TurtleStrategy(BaseStrategy):
    """Donchian channel breakout (20-period)."""

    name = "turtle"

    def __init__(self, entry_period: int = 20, exit_period: int = 10):
        self.entry_period = entry_period
        self.exit_period = exit_period

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        donchian = ta.donchian(df["High"], df["Low"], lower_length=self.entry_period, upper_length=self.entry_period)
        if donchian is not None:
            df["dc_upper"] = donchian.iloc[:, 2]  # Upper band
            df["dc_lower"] = donchian.iloc[:, 0]  # Lower band

        exit_donchian = ta.donchian(df["High"], df["Low"], lower_length=self.exit_period, upper_length=self.exit_period)
        if exit_donchian is not None:
            df["dc_exit_lower"] = exit_donchian.iloc[:, 0]

        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            close = df["Close"].iloc[i]
            prev_upper = df["dc_upper"].iloc[i - 1]
            prev_exit_lower = df["dc_exit_lower"].iloc[i - 1]

            if not in_position and close > prev_upper:
                signals.append(Signal(date=date, action="BUY"))
                in_position = True
            elif in_position and close < prev_exit_lower:
                signals.append(Signal(date=date, action="SELL"))
                in_position = False

        return signals
