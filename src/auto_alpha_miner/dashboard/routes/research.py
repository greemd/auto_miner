"""Research journal viewer, editor, and research trigger."""

from __future__ import annotations

import importlib
import traceback
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_journal_data
from auto_alpha_miner.config import STRATEGY_REGISTRY
from auto_alpha_miner.research.journal import Journal, TriedApproach
from auto_alpha_miner.research.runner import run_cycle

router = APIRouter()

JOURNAL_PATH = Path("research/journal.md")


class UpdateListRequest(BaseModel):
    items: list[str]


class AddItemRequest(BaseModel):
    item: str


class DeleteItemRequest(BaseModel):
    index: int


class RunResearchRequest(BaseModel):
    strategy: str
    approach_desc: str = ""
    category: str = ""
    indicators: str = ""
    analysis: str = ""


@router.get("/research", response_class=HTMLResponse)
def research_page(request: Request):
    journal = get_journal_data()
    # Load all strategy modules
    strategies = list(STRATEGY_REGISTRY.keys())
    # Find which strategies are already in journal
    tested = {a["name"] for a in journal["approaches"]}
    available = [s for s in strategies if s not in tested]
    return templates.TemplateResponse(request, "research.html", context={
        "active": "research",
        "journal": journal,
        "strategies": strategies,
        "available_strategies": available,
        "tested_strategies": sorted(tested),
    })


@router.get("/api/research/journal")
def api_journal():
    return get_journal_data()


# --- Next Steps CRUD ---

@router.post("/api/research/next-steps")
def update_next_steps(req: UpdateListRequest):
    journal = Journal(JOURNAL_PATH)
    journal.next_steps = req.items
    journal.save()
    return {"ok": True, "items": journal.next_steps}


@router.post("/api/research/next-steps/add")
def add_next_step(req: AddItemRequest):
    journal = Journal(JOURNAL_PATH)
    journal.next_steps.append(req.item)
    journal.save()
    return {"ok": True, "items": journal.next_steps}


@router.post("/api/research/next-steps/delete")
def delete_next_step(req: DeleteItemRequest):
    journal = Journal(JOURNAL_PATH)
    if 0 <= req.index < len(journal.next_steps):
        journal.next_steps.pop(req.index)
        journal.save()
    return {"ok": True, "items": journal.next_steps}


# --- Research Directions CRUD ---

@router.post("/api/research/directions")
def update_directions(req: UpdateListRequest):
    journal = Journal(JOURNAL_PATH)
    journal.research_directions = req.items
    journal.save()
    return {"ok": True, "items": journal.research_directions}


@router.post("/api/research/directions/add")
def add_direction(req: AddItemRequest):
    journal = Journal(JOURNAL_PATH)
    journal.research_directions.append(req.item)
    journal.save()
    return {"ok": True, "items": journal.research_directions}


@router.post("/api/research/directions/delete")
def delete_direction(req: DeleteItemRequest):
    journal = Journal(JOURNAL_PATH)
    if 0 <= req.index < len(journal.research_directions):
        journal.research_directions.pop(req.index)
        journal.save()
    return {"ok": True, "items": journal.research_directions}


# --- Run Research ---



@router.post("/api/research/run")
def run_research(req: RunResearchRequest):
    """Run a strategy across all benchmark symbols and save results to journal."""

    strategy_name = req.strategy
    if strategy_name not in STRATEGY_REGISTRY:
        return JSONResponse({"ok": False, "error": f"Strategy '{strategy_name}' not found in registry."}, status_code=400)

    journal = Journal(JOURNAL_PATH)

    # Check if already tested
    if journal.has_strategy(strategy_name):
        return JSONResponse({"ok": False, "error": f"Strategy '{strategy_name}' already exists in journal."}, status_code=400)

    try:
        # Run backtest across all benchmark symbols
        results = run_cycle(
            strategy_name=strategy_name,
            symbols=journal.config.benchmark_symbols,
            start=journal.config.start,
            end=journal.config.end,
            capital=journal.config.capital,
        )

        # Build approach entry
        strat_cls = STRATEGY_REGISTRY[strategy_name]
        indicators = [i.strip() for i in req.indicators.split(",") if i.strip()] if req.indicators else [strategy_name]
        approach = TriedApproach(
            id=journal.next_id(),
            name=strategy_name,
            date=str(date.today()),
            approach=req.approach_desc or (strat_cls.__doc__ or strategy_name),
            category=req.category or "other",
            indicators=indicators,
            parameters={},
            results=results,
            analysis=req.analysis or "Strategy tested via dashboard.",
            status="tested",
        )

        journal.add_result(approach)
        journal.update_best_results()
        journal.save()

        # Build response summary
        summary = {}
        for sym, metrics in results.items():
            summary[sym] = {
                "sharpe": round(metrics.get("sharpe_ratio", 0), 2),
                "return": round(metrics.get("total_return", 0), 1),
                "mdd": round(metrics.get("max_drawdown", 0), 1),
            }

        return {
            "ok": True,
            "approach_id": approach.id,
            "name": strategy_name,
            "results": summary,
        }

    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e), "traceback": traceback.format_exc()}, status_code=500)


@router.post("/api/research/ai-cycle")
def run_ai_cycle():
    """Trigger a full AI research cycle (calls research_cycle.sh).

    This runs Claude Code to autonomously:
    1. Read the journal and identify what to try next
    2. Generate a brand new strategy (code)
    3. Validate and backtest it
    4. Update the journal with results
    """
    import subprocess
    import threading

    script_path = Path("scripts/research_cycle.sh")
    if not script_path.exists():
        return JSONResponse({"ok": False, "error": "research_cycle.sh not found"}, status_code=404)

    # Check if a cycle is already running
    lock_file = Path("/tmp/research_cycle.lock")
    if lock_file.exists():
        return JSONResponse({"ok": False, "error": "A research cycle is already running."}, status_code=409)

    def run_cycle_bg():
        try:
            lock_file.touch()
            import os
            env = os.environ.copy()
            env["PATH"] = "/home/ubuntu/.local/bin:/home/ubuntu/.cargo/bin:/usr/local/bin:" + env.get("PATH", "")
            env["HOME"] = "/home/ubuntu"
            result = subprocess.run(
                ["bash", str(script_path)],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(Path.cwd()),
                env=env,
            )
            # Write result to a status file
            status_file = Path("/tmp/research_cycle_result.json")
            import json
            status_file.write_text(json.dumps({
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-2000:] if result.stdout else "",
                "stderr_tail": result.stderr[-1000:] if result.stderr else "",
            }))
        except subprocess.TimeoutExpired:
            import json
            Path("/tmp/research_cycle_result.json").write_text(json.dumps({
                "ok": False, "returncode": -1, "stdout_tail": "", "stderr_tail": "Timeout after 600s",
            }))
        except Exception as e:
            import json
            Path("/tmp/research_cycle_result.json").write_text(json.dumps({
                "ok": False, "returncode": -1, "stdout_tail": "", "stderr_tail": str(e),
            }))
        finally:
            lock_file.unlink(missing_ok=True)

    thread = threading.Thread(target=run_cycle_bg, daemon=True)
    thread.start()

    return {"ok": True, "message": "AI research cycle started in background."}


@router.get("/api/research/ai-cycle/status")
def ai_cycle_status():
    """Check the status of a running AI research cycle."""
    import json
    lock_file = Path("/tmp/research_cycle.lock")
    result_file = Path("/tmp/research_cycle_result.json")

    if lock_file.exists():
        return {"status": "running"}

    if result_file.exists():
        data = json.loads(result_file.read_text())
        return {"status": "completed", **data}

    return {"status": "idle"}


@router.get("/api/research/strategies")
def get_available_strategies():
    """Return list of registered strategies and their test status."""
    journal = Journal(JOURNAL_PATH)
    tested = {a.name for a in journal.tried_approaches}

    strategies = []
    for name, cls in STRATEGY_REGISTRY.items():
        strategies.append({
            "name": name,
            "doc": cls.__doc__ or "",
            "tested": name in tested,
        })
    return {"strategies": strategies}
