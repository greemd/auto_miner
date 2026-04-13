"""Bridge between backtest engine and JSON-serializable dashboard data."""

from __future__ import annotations

from pathlib import Path

from auto_alpha_miner.backtest.engine import BacktestEngine, BacktestResult
from auto_alpha_miner.config import STRATEGY_REGISTRY, SYMBOL_MAP
from auto_alpha_miner.data import CachedCollector, YFinanceCollector
from auto_alpha_miner.evaluation.metrics import evaluate
from auto_alpha_miner.research.journal import Journal


def get_strategies() -> list[str]:
    return list(STRATEGY_REGISTRY.keys())


def get_symbols() -> list[str]:
    return list(SYMBOL_MAP.keys())


def run_backtest(
    strategy_name: str,
    symbol: str,
    start: str = "2020-01-01",
    end: str = "2024-12-31",
    capital: float = 100_000.0,
) -> dict:
    """Run a single backtest and return JSON-serializable result."""
    if strategy_name not in STRATEGY_REGISTRY:
        raise ValueError(f"Strategy '{strategy_name}' not found")

    collector = CachedCollector(YFinanceCollector())
    df = collector.fetch(symbol, start, end)
    strat = STRATEGY_REGISTRY[strategy_name]()
    engine = BacktestEngine(initial_capital=capital)
    result = engine.run(df, strat, symbol)
    metrics = evaluate(result)

    return backtest_result_to_dict(result, metrics)


def run_compare(
    strategy_names: list[str],
    symbol: str,
    start: str = "2020-01-01",
    end: str = "2024-12-31",
    capital: float = 100_000.0,
) -> list[dict]:
    """Run multiple strategies on one symbol and return list of results."""
    collector = CachedCollector(YFinanceCollector())
    df = collector.fetch(symbol, start, end)
    engine = BacktestEngine(initial_capital=capital)
    results = []

    for name in strategy_names:
        if name not in STRATEGY_REGISTRY:
            continue
        strat = STRATEGY_REGISTRY[name]()
        result = engine.run(df, strat, symbol)
        metrics = evaluate(result)
        results.append(backtest_result_to_dict(result, metrics))

    return results


def get_journal_data(journal_path: str = "research/journal.md") -> dict:
    """Load and serialize journal data."""
    path = Path(journal_path)
    if not path.exists():
        return {"approaches": [], "next_steps": [], "directions": [], "config": {}}

    journal = Journal(path)
    approaches = []
    for a in journal.tried_approaches:
        approaches.append({
            "id": a.id,
            "name": a.name,
            "date": a.date,
            "approach": a.approach,
            "category": a.category,
            "indicators": a.indicators,
            "parameters": a.parameters,
            "results": a.results,
            "analysis": a.analysis,
            "status": a.status,
        })

    return {
        "approaches": approaches,
        "next_steps": journal.next_steps,
        "directions": journal.research_directions,
        "config": {
            "benchmark_symbols": journal.config.benchmark_symbols,
            "start": journal.config.start,
            "end": journal.config.end,
            "capital": journal.config.capital,
        },
    }


def backtest_result_to_dict(result: BacktestResult, metrics: dict) -> dict:
    """Convert BacktestResult + metrics to JSON-serializable dict."""
    ec = result.equity_curve
    cummax = ec.cummax()
    drawdown = (ec - cummax) / cummax

    return {
        "symbol": result.symbol,
        "strategy": result.strategy_name,
        "equity_curve": {
            "dates": [d.isoformat() for d in ec.index],
            "values": ec.tolist(),
        },
        "drawdown": {
            "dates": [d.isoformat() for d in drawdown.index],
            "values": drawdown.tolist(),
        },
        "metrics": {
            "total_return": round(metrics["total_return"] * 100, 2),
            "cagr": round(metrics["cagr"] * 100, 2),
            "max_drawdown": round(metrics["max_drawdown"] * 100, 2),
            "sharpe_ratio": round(metrics["sharpe_ratio"], 2),
            "win_rate": round(metrics["win_rate"] * 100, 1),
            "profit_factor": round(metrics["profit_factor"], 2),
            "trade_count": int(metrics["trade_count"]),
        },
        "trades": [
            {
                "entry_date": t.entry_date.isoformat() if t.entry_date else None,
                "exit_date": t.exit_date.isoformat() if t.exit_date else None,
                "entry_price": round(t.entry_price, 2),
                "exit_price": round(t.exit_price, 2) if t.exit_price else None,
                "pnl": round(t.pnl, 2) if t.pnl is not None else None,
                "return_pct": round(t.return_pct * 100, 2) if t.return_pct is not None else None,
            }
            for t in result.trades
        ],
    }
