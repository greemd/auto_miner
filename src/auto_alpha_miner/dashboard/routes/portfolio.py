"""Portfolio backtest page: multi-symbol backtesting."""

from __future__ import annotations

import importlib
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from auto_alpha_miner.config import PUBLIC_MODE
from auto_alpha_miner.dashboard.app import templates, require_private_mode
from auto_alpha_miner.dashboard.services import get_strategies, get_symbols
from auto_alpha_miner.config import STRATEGY_REGISTRY, UNIVERSES
from auto_alpha_miner.data import CachedCollector, YFinanceCollector
from auto_alpha_miner.backtest.allocator import ALLOCATOR_REGISTRY
from auto_alpha_miner.backtest.multi_engine import MultiSymbolEngine
from auto_alpha_miner.evaluation.metrics import evaluate_portfolio

router = APIRouter()


def _ensure_strategies():
    import auto_alpha_miner.strategy as strat_pkg
    strat_dir = Path(strat_pkg.__file__).parent
    for f in strat_dir.glob("*.py"):
        if f.name.startswith("_"):
            continue
        importlib.import_module(f"auto_alpha_miner.strategy.{f.stem}")


class PortfolioRequest(BaseModel):
    strategy: str
    universe: str
    allocator: str = "equal"
    rebalance: str | None = None
    start: str = "2020-01-01"
    end: str = "2024-12-31"
    capital: float = 100_000.0


@router.get("/portfolio", response_class=HTMLResponse)
def portfolio_page(request: Request):
    _ensure_strategies()
    return templates.TemplateResponse(request, "portfolio.html", context={
        "active": "portfolio",
        "public_mode": PUBLIC_MODE,
        "strategies": list(STRATEGY_REGISTRY.keys()),
        "universes": {name: symbols for name, symbols in UNIVERSES.items()},
        "allocators": list(ALLOCATOR_REGISTRY.keys()),
    })


@router.post("/api/portfolio")
def api_portfolio(req: PortfolioRequest, _=Depends(require_private_mode)):
    _ensure_strategies()

    if req.strategy not in STRATEGY_REGISTRY:
        return JSONResponse({"error": f"Strategy '{req.strategy}' not found"}, status_code=400)
    if req.universe not in UNIVERSES:
        return JSONResponse({"error": f"Universe '{req.universe}' not found"}, status_code=400)
    if req.allocator not in ALLOCATOR_REGISTRY:
        return JSONResponse({"error": f"Allocator '{req.allocator}' not found"}, status_code=400)

    try:
        symbols = UNIVERSES[req.universe]
        collector = CachedCollector(YFinanceCollector())

        data = {}
        errors = []
        for sym in symbols:
            try:
                data[sym] = collector.fetch(sym, req.start, req.end)
            except ValueError as e:
                errors.append(f"{sym}: {e}")

        if not data:
            return JSONResponse({"error": "No data fetched for any symbol"}, status_code=400)

        allocator = ALLOCATOR_REGISTRY[req.allocator]()
        engine = MultiSymbolEngine(initial_capital=req.capital)

        rebalance = req.rebalance if req.rebalance in ("W", "M", "Q") else None
        result = engine.run(data, STRATEGY_REGISTRY[req.strategy], allocator, rebalance=rebalance)
        metrics = evaluate_portfolio(result)

        # Build response
        ec = result.combined_equity
        cummax = ec.cummax()
        drawdown = (ec - cummax) / cummax

        # Per-symbol equity curves
        symbol_curves = {}
        for sym, sr in result.symbol_results.items():
            symbol_curves[sym] = {
                "dates": [d.isoformat() for d in sr.equity_curve.index],
                "values": sr.equity_curve.tolist(),
            }

        return {
            "strategy": result.strategy_name,
            "allocator": result.allocator_name,
            "universe": req.universe,
            "symbols": list(data.keys()),
            "rebalance": rebalance or "fixed",
            "equity_curve": {
                "dates": [d.isoformat() for d in ec.index],
                "values": ec.tolist(),
            },
            "drawdown": {
                "dates": [d.isoformat() for d in drawdown.index],
                "values": drawdown.tolist(),
            },
            "symbol_curves": symbol_curves,
            "weights": {s: round(w, 4) for s, w in result.weights.items()},
            "metrics": {
                "total_return": round(metrics["total_return"] * 100, 2),
                "cagr": round(metrics["cagr"] * 100, 2),
                "max_drawdown": round(metrics["max_drawdown"] * 100, 2),
                "max_dd_duration_days": int(metrics.get("max_dd_duration_days", 0)),
                "sharpe_ratio": round(metrics["sharpe_ratio"], 2),
                "sortino_ratio": round(metrics.get("sortino_ratio", 0), 2),
                "calmar_ratio": round(metrics.get("calmar_ratio", 0), 2),
                "win_rate": round(metrics["win_rate"] * 100, 1),
                "profit_factor": round(metrics["profit_factor"], 2),
                "trade_count": int(metrics["trade_count"]),
            },
            "errors": errors,
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
