"""Overview page: stats, best results table, Sharpe heatmap."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_journal_data

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def overview(request: Request):
    journal = get_journal_data()
    approaches = journal["approaches"]

    # Stats
    total_strategies = len(approaches)
    best_sharpe = 0.0
    best_name = "-"
    for a in approaches:
        spy = a["results"].get("SPY", {})
        s = spy.get("sharpe_ratio", spy.get("sharpe", 0.0))
        if s > best_sharpe:
            best_sharpe = s
            best_name = a["name"]

    # Heatmap data: strategies x symbols
    symbols = journal["config"].get("benchmark_symbols", [])
    strategies = [a["name"] for a in approaches]
    heatmap_values = []
    for a in approaches:
        row = []
        for sym in symbols:
            sym_results = a["results"].get(sym, {})
            sharpe = sym_results.get("sharpe_ratio", sym_results.get("sharpe", None))
            row.append(sharpe)
        heatmap_values.append(row)

    # Sort approaches by SPY Sharpe descending for the table
    def get_spy_sharpe(a):
        spy = a.get("results", {}).get("SPY", {})
        return spy.get("sharpe_ratio", spy.get("sharpe", 0.0))

    sorted_approaches = sorted(approaches, key=get_spy_sharpe, reverse=True)

    return templates.TemplateResponse(request, "overview.html", context={
        "active": "overview",
        "total_strategies": total_strategies,
        "best_sharpe": round(best_sharpe, 2),
        "best_name": best_name,
        "approaches": sorted_approaches,
        "symbols": symbols,
        "heatmap": {
            "strategies": strategies,
            "symbols": symbols,
            "values": heatmap_values,
        },
    })
