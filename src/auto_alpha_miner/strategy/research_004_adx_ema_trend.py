"""ADX + EMA trend-following strategy.

Only enters longs when the EMA crossover fires inside a strong trending
regime (ADX > 25).  Exits when the EMA cross reverses OR the trend
weakens (ADX < 20), whichever comes first.
"""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class AdxEmaTrendStrategy(BaseStrategy):
    """EMA crossover filtered by ADX trend strength."""

    name = "research_004_adx_ema_trend"

    def __init__(
        self,
        fast_period: int = 20,
        slow_period: int = 50,
        adx_period: int = 14,
        adx_entry: float = 25.0,
        adx_exit: float = 20.0,
    ):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.adx_period = adx_period
        self.adx_entry = adx_entry
        self.adx_exit = adx_exit

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        fast = ta.ema(df["Close"], length=self.fast_period)
        slow = ta.ema(df["Close"], length=self.slow_period)
        adx_df = ta.adx(df["High"], df["Low"], df["Close"], length=self.adx_period)

        if fast is not None:
            df["ema_fast"] = fast
        if slow is not None:
            df["ema_slow"] = slow
        if adx_df is not None:
            adx_col = f"ADX_{self.adx_period}"
            if adx_col in adx_df.columns:
                df["adx"] = adx_df[adx_col]

        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            fast = df["ema_fast"].iloc[i]
            slow = df["ema_slow"].iloc[i]
            prev_fast = df["ema_fast"].iloc[i - 1]
            prev_slow = df["ema_slow"].iloc[i - 1]
            adx = df["adx"].iloc[i]

            # Entry: bullish EMA cross with strong trend
            if not in_position:
                if prev_fast <= prev_slow and fast > slow and adx >= self.adx_entry:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True
            else:
                # Exit: bearish EMA cross OR trend fades
                bearish_cross = prev_fast >= prev_slow and fast < slow
                trend_faded = adx < self.adx_exit
                if bearish_cross or trend_faded:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
