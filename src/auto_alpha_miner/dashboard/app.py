"""FastAPI application factory for the dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

_DASHBOARD_DIR = Path(__file__).parent
_TEMPLATES_DIR = _DASHBOARD_DIR / "templates"
_STATIC_DIR = _DASHBOARD_DIR / "static"

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

app = FastAPI(title="Auto Alpha Miner Dashboard")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# Import and register routes
from auto_alpha_miner.dashboard.routes import overview, strategy, compare, research, portfolio, status  # noqa: E402

app.include_router(overview.router)
app.include_router(strategy.router)
app.include_router(compare.router)
app.include_router(portfolio.router)
app.include_router(research.router)
app.include_router(status.router)
