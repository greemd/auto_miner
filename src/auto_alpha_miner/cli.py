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

    def _get_default_collector() -> CachedCollector:
        return CachedCollector(YFinanceCollector())

    def _get_default_engine(capital: float) -> BacktestEngine:
        return BacktestEngine(initial_capital=capital)

    _load_strategies()

    if strategy not in STRATEGY_REGISTRY:
        typer.echo(f"Unknown strategy: {strategy}")
        typer.echo(f"Available: {', '.join(STRATEGY_REGISTRY.keys())}")
        raise typer.Exit(1)

    collector_instance = _get_default_collector()
    typer.echo(f"Fetching {symbol} data ({start} ~ {end})...")
    df = collector_instance.fetch(symbol, start, end)

    strat = STRATEGY_REGISTRY[strategy]()
    engine_instance = _get_default_engine(capital)

    typer.echo(f"Running {strategy} strategy...")
    result = engine_instance.run(df, strat, symbol)
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

    def _get_default_collector() -> CachedCollector:
        return CachedCollector(YFinanceCollector())

    def _get_default_engine(capital: float) -> BacktestEngine:
        return BacktestEngine(initial_capital=capital)

    _load_strategies()

    collector_instance = _get_default_collector()
    typer.echo(f"Fetching {symbol} data ({start} ~ {end})...")
    df = collector_instance.fetch(symbol, start, end)

    engine_instance = _get_default_engine(capital)

    for name, strat_cls in STRATEGY_REGISTRY.items():
        strat = strat_cls()
        result = engine_instance.run(df, strat, symbol)
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

    def _get_default_collector() -> CachedCollector:
        return CachedCollector(YFinanceCollector())

    def _get_default_multi_engine(capital: float) -> MultiSymbolEngine:
        return MultiSymbolEngine(initial_capital=capital)

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
    collector_instance = _get_default_collector()

    # Fetch data for all symbols
    data = {}
    for sym in symbols:
        typer.echo(f"Fetching {sym} data...")
        try:
            data[sym] = collector_instance.fetch(sym, start, end)
        except ValueError as e:
            typer.echo(f"  Warning: {e} — skipping")

    if not data:
        typer.echo("No data fetched. Exiting.")
        raise typer.Exit(1)

    if rebalance and rebalance not in ("W", "M", "Q"):
        typer.echo(f"Unknown rebalance frequency: {rebalance}. Use W, M, or Q.")
        raise typer.Exit(1)

    allocator = EqualWeightAllocator()
    engine_instance = _get_default_multi_engine(capital)

    rebal_label = {"W": "weekly", "M": "monthly", "Q": "quarterly"}.get(rebalance, "fixed") if rebalance else "fixed"
    typer.echo(f"\nRunning {strategy} on {len(data)} symbols with equal allocation ({rebal_label} rebalancing)...")
    result = engine_instance.run(data, STRATEGY_REGISTRY[strategy], allocator, rebalance=rebalance)
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


# ── Research commands ──────────────────────────────────────────────

@app.command("research-init")
def research_init(
    journal: str = typer.Option("research/journal.md", help="Journal file path"),
) -> None:
    """Initialize research journal with baseline results from existing strategies."""
    from pathlib import Path
    from datetime import date

    from auto_alpha_miner.config import STRATEGY_REGISTRY
    from auto_alpha_miner.research.journal import Journal, TriedApproach, create_default_journal
    from auto_alpha_miner.research.runner import run_cycle

    _load_strategies()

    journal_path = Path(journal)
    if journal_path.exists():
        typer.echo(f"Journal already exists at {journal_path}")
        raise typer.Exit(1)

    j = create_default_journal(journal_path)
    typer.echo("Running baseline backtests on existing strategies...")

    # Map existing strategies to metadata
    strategy_meta = {
        "turtle": ("trend-following", ["Donchian"], {"entry_period": "20", "exit_period": "10"}),
        "rsi": ("mean-reversion", ["RSI"], {"period": "14", "oversold": "30", "overbought": "70"}),
        "ma_cross": ("trend-following", ["SMA"], {"fast": "50", "slow": "200"}),
    }

    approach_id = 1
    for name in STRATEGY_REGISTRY:
        typer.echo(f"  Running {name}...")
        try:
            results = run_cycle(name, j.config.benchmark_symbols, j.config.start, j.config.end, j.config.capital)
        except Exception as e:
            typer.echo(f"  Warning: {name} failed — {e}")
            continue

        category, indicators, params = strategy_meta.get(name, ("other", [name], {}))
        approach = TriedApproach(
            id=approach_id,
            name=f"baseline_{name}",
            date=str(date.today()),
            approach=f"Baseline: {STRATEGY_REGISTRY[name].__doc__ or name}",
            category=category,
            indicators=indicators,
            parameters=params,
            results=results,
            analysis="Baseline strategy for comparison.",
            status="baseline",
        )
        j.add_result(approach)
        approach_id += 1

    j.update_best_results()
    j.save()
    typer.echo(f"\nJournal created at {journal_path} with {len(j.tried_approaches)} baseline strategies.")


@app.command("research-run")
def research_run(
    strategy: str = typer.Option(..., help="Strategy name to backtest"),
    journal: str = typer.Option("research/journal.md", help="Journal file path"),
) -> None:
    """Run a strategy backtest and output structured results."""
    from pathlib import Path

    from auto_alpha_miner.config import STRATEGY_REGISTRY
    from auto_alpha_miner.research.journal import Journal
    from auto_alpha_miner.research.runner import run_research_cycle

    _load_strategies()

    journal_path = Path(journal)
    if not journal_path.exists():
        typer.echo(f"Journal not found: {journal_path}. Run 'research-init' first.")
        raise typer.Exit(1)

    j = Journal(journal_path)
    if j.has_strategy(strategy):
        typer.echo(f"Strategy '{strategy}' already exists in journal. Use a different name.")
        raise typer.Exit(1)

    if strategy not in STRATEGY_REGISTRY:
        typer.echo(f"Strategy '{strategy}' not found in registry.")
        typer.echo(f"Available: {', '.join(STRATEGY_REGISTRY.keys())}")
        raise typer.Exit(1)

    typer.echo(f"Running {strategy} on {', '.join(j.config.benchmark_symbols)}...")
    results = run_research_cycle(journal_path, strategy)

    # Output structured results
    typer.echo("\n=== RESEARCH RESULT ===")
    typer.echo(f"strategy: {strategy}")
    for symbol, metrics in results.items():
        typer.echo(f"--- {symbol} ---")
        for k, v in metrics.items():
            typer.echo(f"{k}: {v}")
    typer.echo("=== END RESULT ===")


@app.command("research-validate")
def research_validate(
    file: str = typer.Option(..., help="Path to strategy .py file"),
) -> None:
    """Validate a generated strategy file."""
    from pathlib import Path
    from auto_alpha_miner.research.validator import validate_strategy_file

    _load_strategies()

    file_path = Path(file)
    valid, error = validate_strategy_file(file_path)
    if valid:
        typer.echo("VALID")
    else:
        typer.echo(f"INVALID: {error}")
        raise typer.Exit(1)


@app.command("research-status")
def research_status(
    journal: str = typer.Option("research/journal.md", help="Journal file path"),
) -> None:
    """Print a summary of the research journal."""
    from pathlib import Path
    from auto_alpha_miner.research.journal import Journal

    journal_path = Path(journal)
    if not journal_path.exists():
        typer.echo(f"Journal not found: {journal_path}. Run 'research-init' first.")
        raise typer.Exit(1)

    j = Journal(journal_path)

    typer.echo(f"\n{'=' * 50}")
    typer.echo(f"  Research Journal Status")
    typer.echo(f"{'=' * 50}")
    typer.echo(f"  Approaches tried:  {len(j.tried_approaches)}")

    if j.tried_approaches:
        # Find best Sharpe across all approaches
        best_sharpe = 0.0
        best_name = ""
        for a in j.tried_approaches:
            spy = a.results.get("SPY", {})
            s = spy.get("sharpe_ratio", spy.get("sharpe", 0.0))
            if s > best_sharpe:
                best_sharpe = s
                best_name = a.name
        typer.echo(f"  Best Sharpe (SPY): {best_sharpe:.2f} ({best_name})")

    typer.echo(f"{'=' * 50}")

    if j.next_steps:
        typer.echo("  Next Steps:")
        for step in j.next_steps:
            typer.echo(f"    - {step}")
    typer.echo(f"{'=' * 50}\n")


# ── Dashboard command ──────────────────────────────────────────────

@app.command("dashboard")
def dashboard(
    host: str = typer.Option("127.0.0.1", help="Host to bind"),
    port: int = typer.Option(8050, help="Port number"),
) -> None:
    """Start the local web dashboard."""
    import uvicorn

    _load_strategies()
    typer.echo(f"Starting dashboard at http://{host}:{port}")
    uvicorn.run(
        "auto_alpha_miner.dashboard.app:app",
        host=host,
        port=port,
    )


if __name__ == "__main__":
    app()
