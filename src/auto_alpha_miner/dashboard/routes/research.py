"""Research journal viewer page."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from auto_alpha_miner.dashboard.app import templates
from auto_alpha_miner.dashboard.services import get_journal_data

router = APIRouter()


@router.get("/research", response_class=HTMLResponse)
def research_page(request: Request):
    journal = get_journal_data()
    return templates.TemplateResponse(request, "research.html", context={
        "active": "research",
        "journal": journal,
    })


@router.get("/api/research/journal")
def api_journal():
    return get_journal_data()
