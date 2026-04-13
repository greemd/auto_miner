"""Compare page: overlay multiple strategies on one symbol."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_strategies, get_symbols, run_compare

router = APIRouter()


class CompareRequest(BaseModel):
    strategies: list[str]
    symbol: str
    start: str = "2020-01-01"
    end: str = "2024-12-31"
    capital: float = 100_000.0


@router.get("/compare", response_class=HTMLResponse)
def compare_page(request: Request):
    return templates.TemplateResponse(request, "compare.html", context={
        "active": "compare",
        "strategies": get_strategies(),
        "symbols": get_symbols(),
    })


@router.post("/api/compare")
def api_compare(req: CompareRequest):
    try:
        results = run_compare(req.strategies, req.symbol, req.start, req.end, req.capital)
        return JSONResponse(results)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
