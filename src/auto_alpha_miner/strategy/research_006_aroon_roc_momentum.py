"""Aroon crossover + ROC momentum strategy.

Entry: Aroon Up crosses above Aroon Down (trend direction change to bullish)
       AND Rate-of-Change (ROC) > 0 (positive price momentum confirmation).
Exit:  Aroon Down crosses above Aroon Up (trend flips bearish)
       OR ROC turns negative (momentum fades).

Aroon detects nascent trend direction changes with low lag; ROC filters out
weak or counter-trend entries, aiming to capture sustained momentum moves
while staying out of choppy, directionless markets.
"""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class AroonRocMomentumStrategy(BaseStrategy):
    """Aroon crossover filtered by ROC momentum."""

    name = "research_006_aroon_roc_momentum"

    def __init__(
        self,
        aroon_period: int = 25,
        roc_period: int = 20,
    ):
        self.aroon_period = aroon_period
        self.roc_period = roc_period

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        aroon = ta.aroon(df["High"], df["Low"], length=self.aroon_period)
        roc = ta.roc(df["Close"], length=self.roc_period)

        if aroon is not None:
            up_col = f"AROONU_{self.aroon_period}"
            dn_col = f"AROOND_{self.aroon_period}"
            if up_col in aroon.columns:
                df["aroon_up"] = aroon[up_col]
            if dn_col in aroon.columns:
                df["aroon_dn"] = aroon[dn_col]

        if roc is not None:
            df["roc"] = roc

        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]

            prev_up = df["aroon_up"].iloc[i - 1]
            prev_dn = df["aroon_dn"].iloc[i - 1]
            curr_up = df["aroon_up"].iloc[i]
            curr_dn = df["aroon_dn"].iloc[i]
            roc = df["roc"].iloc[i]

            if not in_position:
                # Aroon Up crosses above Aroon Down with positive ROC
                bullish_cross = prev_up <= prev_dn and curr_up > curr_dn
                if bullish_cross and roc > 0:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True
            else:
                # Aroon Down crosses above Aroon Up OR momentum gone negative
                bearish_cross = prev_dn <= prev_up and curr_dn > curr_up
                if bearish_cross or roc < 0:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
