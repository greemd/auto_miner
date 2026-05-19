"""Data collection utilities using yfinance."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

from auto_alpha_miner.config import SYMBOL_MAP
from datetime import datetime

_CACHE_DIR = Path(__file__).resolve().parents[2] / ".data_cache"


class YFinanceCollector:
    """Fetch OHLCV data from Yahoo Finance."""

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        ticker = SYMBOL_MAP.get(symbol, symbol)
        df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if df.empty:
            raise ValueError(f"No data returned for {symbol} ({ticker})")
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df


class CachedCollector:
    """Wraps a collector with parquet file caching."""

    def __init__(self, inner: YFinanceCollector, cache_dir: Path | None = None, cache_expiry_days: int = 7) -> None:
        self._inner = inner
        self._cache_dir = cache_dir or _CACHE_DIR
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry_days = cache_expiry_days

    def fetch(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        cache_file = self._cache_dir / f"{symbol}_{start}_{end}.parquet"
        if cache_file.exists():
            # Check if cache is expired
            file_mod_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if (datetime.now() - file_mod_time).days < self.cache_expiry_days:
                return pd.read_parquet(cache_file)
            print(f"Cache for {symbol} ({start}-{end}) expired. Re-fetching...")
        df = self._inner.fetch(symbol, start, end)
        df.to_parquet(cache_file)
        return df
