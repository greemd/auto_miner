"""ATR volatility breakout strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class AtrBreakoutStrategy(BaseStrategy):
    """Volatility breakout: buy when price breaks above SMA + ATR multiplier."""

    name = "atr_breakout"

    def __init__(self, sma_period: int = 20, atr_period: int = 14, multiplier: float = 1.5):
        self.sma_period = sma_period
        self.atr_period = atr_period
        self.multiplier = multiplier

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df["sma"] = ta.sma(df["Close"], length=self.sma_period)
        atr = ta.atr(df["High"], df["Low"], df["Close"], length=self.atr_period)
        df["atr"] = atr
        df["upper_band"] = df["sma"] + self.multiplier * df["atr"]
        df["lower_band"] = df["sma"] - self.multiplier * df["atr"]
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            close = df["Close"].iloc[i]
            upper = df["upper_band"].iloc[i]
            lower = df["lower_band"].iloc[i]
            sma = df["sma"].iloc[i]

            # Buy: price breaks above upper band (volatility breakout)
            if not in_position and close > upper:
                signals.append(Signal(date=date, action="BUY"))
                in_position = True

            # Sell: price drops below SMA (trend reversal)
            elif in_position and close < sma:
                signals.append(Signal(date=date, action="SELL"))
                in_position = False

        return signals
