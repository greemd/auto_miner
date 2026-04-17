"""Bollinger Band + Volume mean-reversion strategy."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class BollingerVolStrategy(BaseStrategy):
    """Mean-reversion: buy at lower Bollinger Band with volume confirmation, sell at upper band."""

    name = "bollinger_vol"

    def __init__(self, bb_period: int = 20, bb_std: float = 2.0, vol_ma: int = 20):
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.vol_ma = vol_ma

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        bb = ta.bbands(df["Close"], length=self.bb_period, std=self.bb_std)
        if bb is not None:
            df["bb_lower"] = bb.iloc[:, 0]   # Lower band
            df["bb_mid"] = bb.iloc[:, 1]     # Middle band
            df["bb_upper"] = bb.iloc[:, 2]   # Upper band

        df["vol_ma"] = ta.sma(df["Volume"], length=self.vol_ma)
        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            close = df["Close"].iloc[i]
            bb_lower = df["bb_lower"].iloc[i]
            bb_upper = df["bb_upper"].iloc[i]
            bb_mid = df["bb_mid"].iloc[i]
            volume = df["Volume"].iloc[i]
            vol_avg = df["vol_ma"].iloc[i]

            # Buy: price touches lower band with above-average volume (capitulation)
            if not in_position and close <= bb_lower and volume > vol_avg:
                signals.append(Signal(date=date, action="BUY"))
                in_position = True

            # Sell: price touches upper band
            elif in_position and close >= bb_upper:
                signals.append(Signal(date=date, action="SELL"))
                in_position = False

        return signals
