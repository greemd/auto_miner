"""Strategy detail page: run backtest on demand."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_strategies, get_symbols, run_backtest

router = APIRouter()


class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    start: str = "2020-01-01"
    end: str = "2024-12-31"
    capital: float = 100_000.0


@router.get("/strategy", response_class=HTMLResponse)
def strategy_page(request: Request):
    return templates.TemplateResponse(request, "strategy.html", context={
        "active": "strategy",
        "strategies": get_strategies(),
        "symbols": get_symbols(),
    })


@router.post("/api/backtest")
def api_backtest(req: BacktestRequest):
    try:
        result = run_backtest(req.strategy, req.symbol, req.start, req.end, req.capital)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@router.get("/api/strategies")
def api_strategies():
    return get_strategies()


@router.get("/api/symbols")
def api_symbols():
    return get_symbols()
