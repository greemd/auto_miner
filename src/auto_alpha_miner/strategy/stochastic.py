"""Stochastic oscillator strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class StochasticStrategy(BaseStrategy):
    """Mean-reversion using Stochastic %K/%D crossover in oversold/overbought zones."""

    name = "stochastic"

    def __init__(self, k_period: int = 14, d_period: int = 3,
                 oversold: float = 20, overbought: float = 80):
        self.k_period = k_period
        self.d_period = d_period
        self.oversold = oversold
        self.overbought = overbought

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        stoch = ta.stoch(df["High"], df["Low"], df["Close"],
                         k=self.k_period, d=self.d_period)
        if stoch is not None:
            df["stoch_k"] = stoch.iloc[:, 0]
            df["stoch_d"] = stoch.iloc[:, 1]
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            k = df["stoch_k"].iloc[i]
            d = df["stoch_d"].iloc[i]
            prev_k = df["stoch_k"].iloc[i - 1]
            prev_d = df["stoch_d"].iloc[i - 1]

            # Buy: %K crosses above %D in oversold zone
            if not in_position:
                if prev_k <= prev_d and k > d and k < self.oversold:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True

            # Sell: %K crosses below %D in overbought zone
            elif in_position:
                if prev_k >= prev_d and k < d and k > self.overbought:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
