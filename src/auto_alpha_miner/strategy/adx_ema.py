"""ADX + EMA momentum strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class AdxEmaStrategy(BaseStrategy):
    """Trend-following using ADX for trend strength and EMA crossover for direction."""

    name = "adx_ema"

    def __init__(self, adx_period: int = 14, adx_threshold: float = 25.0,
                 fast_ema: int = 12, slow_ema: int = 26):
        self.adx_period = adx_period
        self.adx_threshold = adx_threshold
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        adx_df = ta.adx(df["High"], df["Low"], df["Close"], length=self.adx_period)
        if adx_df is not None:
            df["adx"] = adx_df.iloc[:, 0]  # ADX value
            df["plus_di"] = adx_df.iloc[:, 1]  # +DI
            df["minus_di"] = adx_df.iloc[:, 2]  # -DI

        df["ema_fast"] = ta.ema(df["Close"], length=self.fast_ema)
        df["ema_slow"] = ta.ema(df["Close"], length=self.slow_ema)
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            adx = df["adx"].iloc[i]
            ema_fast = df["ema_fast"].iloc[i]
            ema_slow = df["ema_slow"].iloc[i]
            prev_ema_fast = df["ema_fast"].iloc[i - 1]
            prev_ema_slow = df["ema_slow"].iloc[i - 1]

            # Buy: ADX > threshold (strong trend) and fast EMA crosses above slow EMA
            if not in_position and adx > self.adx_threshold:
                if prev_ema_fast <= prev_ema_slow and ema_fast > ema_slow:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True

            # Sell: fast EMA crosses below slow EMA or ADX drops below threshold
            elif in_position:
                if ema_fast < ema_slow:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
