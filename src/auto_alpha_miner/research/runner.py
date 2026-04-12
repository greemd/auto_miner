"""Execute one research cycle: backtest a strategy across benchmark symbols."""

from __future__ import annotations

from pathlib import Path

from auto_alpha_miner.backtest.engine import BacktestEngine
from auto_alpha_miner.config import STRATEGY_REGISTRY
from auto_alpha_miner.data import CachedCollector, YFinanceCollector
from auto_alpha_miner.evaluation.metrics import evaluate
from auto_alpha_miner.research.journal import Journal


def run_cycle(
    strategy_name: str,
    symbols: list[str],
    start: str,
    end: str,
    capital: float = 100_000.0,
) -> dict[str, dict[str, float]]:
    """Run a strategy across multiple symbols and return metrics.

    Returns dict of symbol -> metrics dict.
    """
    if strategy_name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{strategy_name}' not found in registry")

    collector = CachedCollector(YFinanceCollector())
    engine = BacktestEngine(initial_capital=capital)
    all_results: dict[str, dict[str, float]] = {}

    for symbol in symbols:
        df = collector.fetch(symbol, start, end)
        strat = STRATEGY_REGISTRY[strategy_name]()
        result = engine.run(df, strat, symbol)
        metrics = evaluate(result)

        # Convert metrics to percentage-friendly format for journal
        all_results[symbol] = {
            "sharpe_ratio": metrics["sharpe_ratio"],
            "total_return": metrics["total_return"] * 100,  # Convert to percentage
            "cagr": metrics["cagr"] * 100,
            "max_drawdown": metrics["max_drawdown"] * 100,
            "win_rate": metrics["win_rate"] * 100,
            "profit_factor": metrics["profit_factor"],
            "trade_count": metrics["trade_count"],
        }

    return all_results


def run_research_cycle(
    journal_path: Path,
    strategy_name: str,
) -> dict[str, dict[str, float]]:
    """Run a research cycle using journal configuration.

    Loads config from journal, runs backtest, returns results.
    """
    journal = Journal(journal_path)
    config = journal.config

    return run_cycle(
        strategy_name=strategy_name,
        symbols=config.benchmark_symbols,
        start=config.start,
        end=config.end,
        capital=config.capital,
    )
