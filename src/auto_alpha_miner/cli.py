"""CLI entry point for auto-miner."""

from __future__ import annotations

from typing import Optional

import typer

app = typer.Typer(help="Auto Alpha Miner — backtest trading strategies on market data.")


def _load_strategies() -> None:
    """Auto-import all strategy modules from the strategy package directory."""
    import importlib
    from pathlib import Path
    import auto_alpha_miner.strategy as strat_pkg

    strat_dir = Path(strat_pkg.__file__).parent
    for f in strat_dir.glob("*.py"):
        if f.name.startswith("_"):
            continue
        module_name = f"auto_alpha_miner.strategy.{f.stem}"
        importlib.import_module(module_name)


@app.command()
def run(
    symbol: str = typer.Option("SP500", help="Symbol or alias (e.g., NASDAQ, SP500, BTC, KOSPI)"),
    strategy: str = typer.Option("turtle", help="Strategy name (turtle, rsi, ma_cross)"),
    start: str = typer.Option("2020-01-01", help="Start date (YYYY-MM-DD)"),
    end: str = typer.Option("2024-12-31", help="End date (YYYY-MM-DD)"),
    capital: float = typer.Option(100_000.0, help="Initial capital"),
    plot: bool = typer.Option(False, help="Show matplotlib chart"),
    save_chart: Optional[str] = typer.Option(None, help="Save chart to file path"),
) -> None:
    """Run a backtest for a single strategy on a symbol."""
    from auto_alpha_miner.config import STRATEGY_REGISTRY
    from auto_alpha_miner.data import CachedCollector, YFinanceCollector
    from auto_alpha_miner.backtest.engine import BacktestEngine
    from auto_alpha_miner.evaluation.metrics import evaluate
    from auto_alpha_miner.evaluation.report import print_report, plot_report

    _load_strategies()

    if strategy not in STRATEGY_REGISTRY:
        typer.echo(f"Unknown strategy: {strategy}")
        typer.echo(f"Available: {', '.join(STRATEGY_REGISTRY.keys())}")
        raise typer.Exit(1)

    collector = CachedCollector(YFinanceCollector())
    typer.echo(f"Fetching {symbol} data ({start} ~ {end})...")
    df = collector.fetch(symbol, start, end)

    strat = STRATEGY_REGISTRY[strategy]()
    engine = BacktestEngine(initial_capital=capital)

    typer.echo(f"Running {strategy} strategy...")
    result = engine.run(df, strat, symbol)
    metrics = evaluate(result)
    print_report(result, metrics)

    if plot or save_chart:
        plot_report(result, metrics, save_path=save_chart)


@app.command("run-all")
def run_all(
    symbol: str = typer.Option("SP500", help="Symbol or alias"),
    start: str = typer.Option("2020-01-01", help="Start date"),
    end: str = typer.Option("2024-12-31", help="End date"),
    capital: float = typer.Option(100_000.0, help="Initial capital"),
) -> None:
    """Run all registered strategies on a symbol and compare."""
    from auto_alpha_miner.config import STRATEGY_REGISTRY
    from auto_alpha_miner.data import CachedCollector, YFinanceCollector
    from auto_alpha_miner.backtest.engine import BacktestEngine
    from auto_alpha_miner.evaluation.metrics import evaluate
    from auto_alpha_miner.evaluation.report import print_report

    _load_strategies()

    collector = CachedCollector(YFinanceCollector())
    typer.echo(f"Fetching {symbol} data ({start} ~ {end})...")
    df = collector.fetch(symbol, start, end)

    engine = BacktestEngine(initial_capital=capital)

    for name, strat_cls in STRATEGY_REGISTRY.items():
        strat = strat_cls()
        result = engine.run(df, strat, symbol)
        metrics = evaluate(result)
        print_report(result, metrics)


@app.command("run-portfolio")
def run_portfolio(
    universe: str = typer.Option(..., help="Universe name from config.yaml (e.g., global, crypto, us_etf)"),
    strategy: str = typer.Option("turtle", help="Strategy name"),
    rebalance: Optional[str] = typer.Option(None, help="Rebalance frequency: W (weekly), M (monthly), Q (quarterly). None = fixed weights"),
    start: str = typer.Option("2020-01-01", help="Start date"),
    end: str = typer.Option("2024-12-31", help="End date"),
    capital: float = typer.Option(100_000.0, help="Initial capital"),
    plot: bool = typer.Option(False, help="Show matplotlib chart"),
    save_chart: Optional[str] = typer.Option(None, help="Save chart to file path"),
) -> None:
    """Run a strategy across multiple symbols with equal-weight portfolio allocation."""
    from auto_alpha_miner.config import STRATEGY_REGISTRY, UNIVERSES
    from auto_alpha_miner.data import CachedCollector, YFinanceCollector
    from auto_alpha_miner.backtest.allocator import EqualWeightAllocator
    from auto_alpha_miner.backtest.multi_engine import MultiSymbolEngine
    from auto_alpha_miner.evaluation.metrics import evaluate_portfolio
    from auto_alpha_miner.evaluation.report import print_portfolio_report, plot_portfolio_report

    _load_strategies()

    if universe not in UNIVERSES:
        typer.echo(f"Unknown universe: {universe}")
        typer.echo(f"Available: {', '.join(UNIVERSES.keys())}")
        raise typer.Exit(1)

    if strategy not in STRATEGY_REGISTRY:
        typer.echo(f"Unknown strategy: {strategy}")
        typer.echo(f"Available: {', '.join(STRATEGY_REGISTRY.keys())}")
        raise typer.Exit(1)

    symbols = UNIVERSES[universe]
    collector = CachedCollector(YFinanceCollector())

    # Fetch data for all symbols
    data = {}
    for sym in symbols:
        typer.echo(f"Fetching {sym} data...")
        try:
            data[sym] = collector.fetch(sym, start, end)
        except ValueError as e:
            typer.echo(f"  Warning: {e} — skipping")

    if not data:
        typer.echo("No data fetched. Exiting.")
        raise typer.Exit(1)

    if rebalance and rebalance not in ("W", "M", "Q"):
        typer.echo(f"Unknown rebalance frequency: {rebalance}. Use W, M, or Q.")
        raise typer.Exit(1)

    allocator = EqualWeightAllocator()
    engine = MultiSymbolEngine(initial_capital=capital)

    rebal_label = {"W": "weekly", "M": "monthly", "Q": "quarterly"}.get(rebalance, "fixed") if rebalance else "fixed"
    typer.echo(f"\nRunning {strategy} on {len(data)} symbols with equal allocation ({rebal_label} rebalancing)...")
    result = engine.run(data, STRATEGY_REGISTRY[strategy], allocator, rebalance=rebalance)
    metrics = evaluate_portfolio(result)
    print_portfolio_report(result, metrics)

    if plot or save_chart:
        plot_portfolio_report(result, metrics, save_path=save_chart)


@app.command("list-strategies")
def list_strategies() -> None:
    """List all available strategies."""
    _load_strategies()
    from auto_alpha_miner.config import STRATEGY_REGISTRY

    typer.echo("Available strategies:")
    for name, cls in STRATEGY_REGISTRY.items():
        typer.echo(f"  {name:15s} — {cls.__doc__ or ''}")


@app.command("list-symbols")
def list_symbols() -> None:
    """List supported symbol aliases."""
    from auto_alpha_miner.config import SYMBOL_MAP

    typer.echo("Symbol aliases:")
    for alias, ticker in SYMBOL_MAP.items():
        typer.echo(f"  {alias:10s} → {ticker}")


@app.command("list-universes")
def list_universes() -> None:
    """List available portfolio universes from config.yaml."""
    from auto_alpha_miner.config import UNIVERSES

    typer.echo("Available universes:")
    for name, symbols in UNIVERSES.items():
        typer.echo(f"  {name:15s} — {', '.join(symbols)}")


if __name__ == "__main__":
    app()
