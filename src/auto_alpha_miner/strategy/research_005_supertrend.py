"""Supertrend trend-following strategy.

Uses the ATR-based Supertrend indicator as a single clean signal source.
Buys when price crosses above the Supertrend line (direction flips bullish),
sells when price crosses below (direction flips bearish).

Supertrend is adaptive — it widens in volatile periods and tightens in calm
ones — so it naturally adjusts stop distance without manual parameter tuning.
"""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class SupertrendStrategy(BaseStrategy):
    """ATR-based Supertrend trend-following."""

    name = "research_005_supertrend"

    def __init__(
        self,
        atr_period: int = 10,
        multiplier: float = 3.0,
    ):
        self.atr_period = atr_period
        self.multiplier = multiplier

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        st = ta.supertrend(
            df["High"],
            df["Low"],
            df["Close"],
            length=self.atr_period,
            multiplier=self.multiplier,
        )
        if st is not None:
            dir_col = f"SUPERTd_{self.atr_period}_{self.multiplier}"
            if dir_col in st.columns:
                df["st_dir"] = st[dir_col]

        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]
            prev_dir = df["st_dir"].iloc[i - 1]
            curr_dir = df["st_dir"].iloc[i]

            if not in_position:
                # Flip from bearish (-1) to bullish (1)
                if prev_dir < 0 and curr_dir > 0:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True
            else:
                # Flip from bullish (1) to bearish (-1)
                if prev_dir > 0 and curr_dir < 0:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
