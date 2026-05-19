from celery import current_task
from auto_alpha_miner.celery_app import app
from auto_alpha_miner.research.journal import create_default_journal
from auto_alpha_miner.research.runner import run_cycle
from auto_alpha_miner.config import STRATEGY_REGISTRY
from datetime import date
from pathlib import Path

@app.task
def research_init_task(journal_path_str: str) -> None:
    current_task.update_state(state='PROGRESS', meta={'current': 0, 'total': 1, 'status': 'Initializing research journal...'})
    journal_path = Path(journal_path_str)
    if journal_path.exists():
        print(f"Journal already exists at {journal_path}")
        return

    j = create_default_journal(journal_path)
    print("Running baseline backtests on existing strategies...")

    strategy_meta = {
        "turtle": ("trend-following", ["Donchian"], {"entry_period": "20", "exit_period": "10"}),
        "rsi": ("mean-reversion", ["RSI"], {"period": "14", "oversold": "30", "overbought": "70"}),
        "ma_cross": ("trend-following", ["SMA"], {"fast": "50", "slow": "200"}),
    }

    approach_id = 1
    total_strategies = len(STRATEGY_REGISTRY)
    for i, name in enumerate(STRATEGY_REGISTRY):
        current_task.update_state(state='PROGRESS', meta={'current': i + 1, 'total': total_strategies, 'status': f'Running baseline backtest for {name}...'})

        print(f"  Running {name}...")
        try:
            results = run_cycle(name, j.config.benchmark_symbols, j.config.start, j.config.end, j.config.capital)
        except Exception as e:
            print(f"  Warning: {name} failed — {e}")
            continue

        category, indicators, params = strategy_meta.get(name, ("other", [name], {}))
        approach = j.TriedApproach(
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
    print(f"\nJournal created at {journal_path} with {len(j.tried_approaches)} baseline strategies.")

@app.task
def research_run_task(journal_path_str: str, strategy_name: str) -> None:
    current_task.update_state(state='PROGRESS', meta={'current': 0, 'total': 1, 'status': f'Starting research run for {strategy_name}...'})

    from auto_alpha_miner.research.journal import Journal
    from auto_alpha_miner.research.runner import run_research_cycle

    journal_path = Path(journal_path_str)
    if not journal_path.exists():
        print(f"Journal not found: {journal_path}. Run research_init_task first.")
        return

    j = Journal(journal_path)
    if j.has_strategy(strategy_name):
        print(f"Strategy \'{strategy_name}\' already exists in journal. Use a different name.")
        return

    if strategy_name not in STRATEGY_REGISTRY:
        print(f"Strategy \'{strategy_name}\' not found in registry.")
        print(f"Available: {', '.join(STRATEGY_REGISTRY.keys())}")
        return

    print(f"Running {strategy_name} on {", ".join(j.config.benchmark_symbols)}...")
    current_task.update_state(state='PROGRESS', meta={'current': 1, 'total': 1, 'status': f'Executing research cycle for {strategy_name}...'})

    results = run_research_cycle(journal_path, strategy_name)

    print("\n=== RESEARCH RESULT ===")
    print(f"strategy: {strategy_name}")
    for symbol, metrics in results.items():
        print(f"--- {symbol} ---")
        for k, v in metrics.items():
            print(f"{k}: {v}")
    print("=== END RESULT ===")
