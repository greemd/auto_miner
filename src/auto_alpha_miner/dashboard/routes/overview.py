"""Overview page: AI research dashboard with progress tracking."""

from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_journal_data

router = APIRouter()


def _avg_sharpe(results: dict, symbols: list[str]) -> float:
    vals = []
    for sym in symbols:
        r = results.get(sym, {})
        s = r.get("sharpe_ratio", r.get("sharpe", None))
        if s is not None:
            vals.append(s)
    return sum(vals) / len(vals) if vals else 0.0


@router.get("/", response_class=HTMLResponse)
def overview(request: Request):
    journal = get_journal_data()
    approaches = journal["approaches"]
    symbols = journal["config"].get("benchmark_symbols", [])
    directions = journal.get("directions", [])
    next_steps = journal.get("next_steps", [])

    # --- Research Stats ---
    total_approaches = len(approaches)
    baselines = [a for a in approaches if a["status"] == "baseline"]
    researched = [a for a in approaches if a["status"] != "baseline"]
    num_baselines = len(baselines)
    num_researched = len(researched)

    # Categories explored
    categories = set(a["category"] for a in approaches if a["category"])
    all_indicators = set()
    for a in approaches:
        all_indicators.update(a.get("indicators", []))

    # --- Performance Analysis ---
    # Best baseline avg sharpe
    baseline_sharpes = [_avg_sharpe(a["results"], symbols) for a in baselines]
    best_baseline_sharpe = max(baseline_sharpes) if baseline_sharpes else 0.0
    best_baseline_name = ""
    for a in baselines:
        if _avg_sharpe(a["results"], symbols) == best_baseline_sharpe:
            best_baseline_name = a["name"]

    # Best overall avg sharpe
    best_sharpe = -999.0
    best_name = "-"
    for a in approaches:
        s = _avg_sharpe(a["results"], symbols)
        if s > best_sharpe:
            best_sharpe = s
            best_name = a["name"]
    if best_sharpe <= -999.0:
        best_sharpe = 0.0

    # Improvement over baseline
    improvement = best_sharpe - best_baseline_sharpe if best_baseline_sharpe else 0.0
    improvement_pct = (improvement / best_baseline_sharpe * 100) if best_baseline_sharpe else 0.0

    # Beat baseline count
    beat_baseline = sum(
        1 for a in researched
        if _avg_sharpe(a["results"], symbols) > best_baseline_sharpe
    )
    beat_rate = (beat_baseline / num_researched * 100) if num_researched else 0.0

    # --- Per-symbol best strategy ---
    symbol_bests = {}
    for sym in symbols:
        best_s = -999.0
        best_n = "-"
        best_ret = 0.0
        best_mdd = 0.0
        for a in approaches:
            r = a["results"].get(sym, {})
            s = r.get("sharpe_ratio", r.get("sharpe", None))
            if s is not None and s > best_s:
                best_s = s
                best_n = a["name"]
                best_ret = r.get("total_return", r.get("return", 0.0))
                best_mdd = r.get("max_drawdown", r.get("mdd", 0.0))
        symbol_bests[sym] = {
            "strategy": best_n,
            "sharpe": round(best_s, 2) if best_s > -999 else 0.0,
            "ret": round(best_ret, 1),
            "mdd": round(best_mdd, 1),
        }

    # --- Category analysis ---
    category_stats = defaultdict(lambda: {"count": 0, "avg_sharpe": 0.0, "sharpes": []})
    for a in approaches:
        cat = a["category"] or "other"
        s = _avg_sharpe(a["results"], symbols)
        category_stats[cat]["count"] += 1
        category_stats[cat]["sharpes"].append(s)
    for cat, data in category_stats.items():
        data["avg_sharpe"] = round(sum(data["sharpes"]) / len(data["sharpes"]), 2) if data["sharpes"] else 0.0

    # --- Timeline (approaches in order with sharpe) ---
    timeline = []
    for a in approaches:
        s = _avg_sharpe(a["results"], symbols)
        timeline.append({
            "id": a["id"],
            "name": a["name"],
            "date": a["date"],
            "avg_sharpe": round(s, 2),
            "status": a["status"],
            "category": a["category"],
            "is_best": a["name"] == best_name,
        })

    # --- Heatmap data ---
    strategies = [a["name"] for a in approaches]
    heatmap_values = []
    for a in approaches:
        row = []
        for sym in symbols:
            sym_results = a["results"].get(sym, {})
            sharpe = sym_results.get("sharpe_ratio", sym_results.get("sharpe", None))
            row.append(round(sharpe, 2) if sharpe is not None else None)
        heatmap_values.append(row)

    # --- Sort for table ---
    sorted_approaches = sorted(approaches, key=lambda a: _avg_sharpe(a["results"], symbols), reverse=True)

    # --- AI Engine info ---
    ai_model = "Claude Sonnet 4"
    ai_engine = "Claude Code"
    total_cycles = num_researched  # each AI-generated strategy = 1 cycle

    # --- Tried hypotheses with detail ---
    tried_hypotheses = []
    for a in approaches:
        avg_s = _avg_sharpe(a["results"], symbols)
        beat = avg_s > best_baseline_sharpe if best_baseline_sharpe else False
        tried_hypotheses.append({
            "id": a["id"],
            "name": a["name"],
            "date": a["date"],
            "approach": a["approach"],
            "category": a["category"],
            "indicators": a.get("indicators", []),
            "parameters": a.get("parameters", {}),
            "analysis": a.get("analysis", ""),
            "status": a["status"],
            "avg_sharpe": round(avg_s, 2),
            "beat_baseline": beat,
            "is_best": a["name"] == best_name,
        })

    # --- Discovered strategies (AI-generated that beat baseline) ---
    discovered = [h for h in tried_hypotheses if h["status"] != "baseline" and h["beat_baseline"]]

    return templates.TemplateResponse(request, "overview.html", context={
        "active": "overview",
        # AI Engine
        "ai_model": ai_model,
        "ai_engine": ai_engine,
        "total_cycles": total_cycles,
        # Research progress
        "total_approaches": total_approaches,
        "num_baselines": num_baselines,
        "num_researched": num_researched,
        "num_categories": len(categories),
        "num_indicators": len(all_indicators),
        "categories": list(categories),
        "all_indicators": sorted(all_indicators),
        # Performance
        "best_sharpe": round(best_sharpe, 2),
        "best_name": best_name,
        "best_baseline_sharpe": round(best_baseline_sharpe, 2),
        "best_baseline_name": best_baseline_name,
        "improvement": round(improvement, 2),
        "improvement_pct": round(improvement_pct, 1),
        "beat_baseline": beat_baseline,
        "beat_rate": round(beat_rate, 1),
        # Hypotheses
        "tried_hypotheses": tried_hypotheses,
        "discovered": discovered,
        # Research context
        "directions": directions,
        "next_steps": next_steps,
        "symbol_bests": symbol_bests,
        "category_stats": dict(category_stats),
        "timeline": timeline,
        # Table and heatmap
        "approaches": sorted_approaches,
        "symbols": symbols,
        "heatmap": {
            "strategies": strategies,
            "symbols": symbols,
            "values": heatmap_values,
        },
    })
