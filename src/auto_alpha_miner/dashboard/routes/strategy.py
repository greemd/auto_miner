"""Strategy detail page: run backtest on demand."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_strategies, get_symbols, run_backtest, save_strategy_file

router = APIRouter()


class BacktestRequest(BaseModel):
    strategy: str
    symbol: str
    start: str = "2020-01-01"
    end: str = "2024-12-31"
    capital: float = 100_000.0


class SaveStrategyRequest(BaseModel):
    name: str
    file: str
    code: str


@router.get("/strategy", response_class=HTMLResponse)
def strategy_page(request: Request):
    return templates.TemplateResponse(request, "strategy.html", context={
        "active": "strategy",
        "strategies": get_strategies(),
        "symbols": get_symbols(),
    })


@router.get("/strategy/editor", response_class=HTMLResponse)
def strategy_editor_page(request: Request):
    return templates.TemplateResponse(request, "strategy_editor.html", context={
        "active": "strategy_editor",
    })


@router.post("/api/strategy/save")
def api_save_strategy(req: SaveStrategyRequest):
    try:
        save_strategy_file(req.name, req.file, req.code)
        return JSONResponse({"success": True})
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


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


# --- Cache Management ---

@router.get("/api/cache/info")
def cache_info():
    """Return info about cached data files."""
    from auto_alpha_miner.data import _CACHE_DIR
    if not _CACHE_DIR.exists():
        return {"files": [], "total_size_mb": 0}
    files = []
    total = 0
    for f in sorted(_CACHE_DIR.glob("*.parquet")):
        size = f.stat().st_size
        total += size
        files.append({"name": f.name, "size_kb": round(size / 1024, 1)})
    return {"files": files, "total_size_mb": round(total / 1024 / 1024, 2)}


@router.post("/api/cache/clear")
def cache_clear():
    """Delete all cached data files."""
    from auto_alpha_miner.data import _CACHE_DIR
    if not _CACHE_DIR.exists():
        return {"ok": True, "deleted": 0}
    count = 0
    for f in _CACHE_DIR.glob("*.parquet"):
        f.unlink()
        count += 1
    return {"ok": True, "deleted": count}
