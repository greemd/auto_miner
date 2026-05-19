"""Dashboard routes for real-time status and progress updates."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from auto_alpha_miner.dashboard.app import templates

router = APIRouter()

@router.get("/status", response_class=HTMLResponse)
async def status(request: Request):
    return templates.TemplateResponse("status.html", {"request": request, "title": "Real-time Status"})
