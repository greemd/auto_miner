"""MACD histogram sign-change + OBV trend confirmation strategy.

Entry: MACD histogram crosses from negative to positive (momentum flip bullish)
       AND OBV is above its EMA (rising volume confirming buyer participation).
Exit:  MACD histogram crosses from positive to negative (momentum flip bearish)
       OR OBV drops below its EMA (volume conviction fading).

MACD histogram sign-changes are more responsive than EMA crossovers — they
detect acceleration shifts rather than lagging price crosses. OBV acts as a
volume-based trend filter: sustained moves require volume participation, so
requiring OBV > OBV_EMA avoids entering low-conviction breakouts.
"""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta

from auto_alpha_miner.config import register_strategy
from auto_alpha_miner.strategy.base import BaseStrategy, Signal


@register_strategy
class MacdObvVolumeStrategy(BaseStrategy):
    """MACD histogram flip gated by OBV trend confirmation."""

    name = "research_007_macd_obv_volume"

    def __init__(
        self,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        obv_ema_period: int = 20,
    ):
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.obv_ema_period = obv_ema_period

    def prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        macd = ta.macd(
            df["Close"],
            fast=self.macd_fast,
            slow=self.macd_slow,
            signal=self.macd_signal,
        )
        if macd is not None:
            hist_col = f"MACDh_{self.macd_fast}_{self.macd_slow}_{self.macd_signal}"
            if hist_col in macd.columns:
                df["macd_hist"] = macd[hist_col]

        obv = ta.obv(df["Close"], df["Volume"])
        if obv is not None:
            df["obv"] = obv
            df["obv_ema"] = ta.ema(df["obv"], length=self.obv_ema_period)

        df.dropna(inplace=True)
        return df

    def generate_signals(self, df: pd.DataFrame) -> list[Signal]:
        signals: list[Signal] = []
        in_position = False

        for i in range(1, len(df)):
            date = df.index[i]

            prev_hist = df["macd_hist"].iloc[i - 1]
            curr_hist = df["macd_hist"].iloc[i]
            obv = df["obv"].iloc[i]
            obv_ema = df["obv_ema"].iloc[i]

            if not in_position:
                # MACD histogram flips positive with OBV above its EMA
                hist_flip_up = prev_hist <= 0 and curr_hist > 0
                if hist_flip_up and obv > obv_ema:
                    signals.append(Signal(date=date, action="BUY"))
                    in_position = True
            else:
                # MACD histogram flips negative OR OBV falls below its EMA
                hist_flip_down = prev_hist >= 0 and curr_hist < 0
                obv_bearish = obv < obv_ema
                if hist_flip_down or obv_bearish:
                    signals.append(Signal(date=date, action="SELL"))
                    in_position = False

        return signals
