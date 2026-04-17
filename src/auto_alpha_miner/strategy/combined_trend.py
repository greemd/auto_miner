"""Combined trend strategy: EMA trend + RSI confirmation + Volume filter."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class CombinedTrendStrategy(BaseStrategy):
    """Multi-indicator: EMA trend direction + RSI momentum + Volume confirmation."""

    name = "combined_trend"

    def __init__(self, ema_fast: int = 21, ema_slow: int = 55,
                 rsi_period: int = 14, rsi_threshold: float = 50,
                 vol_ma: int = 20):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period
        self.rsi_threshold = rsi_threshold
        self.vol_ma = vol_ma

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df["ema_fast"] = ta.ema(df["Close"], length=self.ema_fast)
        df["ema_slow"] = ta.ema(df["Close"], length=self.ema_slow)
        df["rsi"] = ta.rsi(df["Close"], length=self.rsi_period)
        df["vol_ma"] = ta.sma(df["Volume"], length=self.vol_ma)
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            ema_f = df["ema_fast"].iloc[i]
            ema_s = df["ema_slow"].iloc[i]
            prev_ema_f = df["ema_fast"].iloc[i - 1]
            prev_ema_s = df["ema_slow"].iloc[i - 1]
            rsi = df["rsi"].iloc[i]
            volume = df["Volume"].iloc[i]
            vol_avg = df["vol_ma"].iloc[i]

            # Buy: EMA cross up + RSI above threshold + volume above average
            if not in_position:
                if (prev_ema_f <= prev_ema_s and ema_f > ema_s
                        and rsi > self.rsi_threshold
                        and volume > vol_avg):
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True

            # Sell: EMA cross down or RSI drops below 40
            elif in_position:
                if ema_f < ema_s or rsi < 40:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
