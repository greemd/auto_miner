"""Dashboard routes for real-time status and progress updates."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Dict, Any
from auto_alpha_miner.celery_app import app as celery_app
from celery.result import AsyncResult
from auto_alpha_miner.dashboard.app import templates

router = APIRouter()

@router.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    return templates.TemplateResponse("status.html", {"request": request, "title": "Real-time Status"})

@router.get("/api/task-status/{task_id}", response_class=JSONResponse)
async def get_task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "status": "Pending..."
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
            "result": task.info.get("result", "")
        }
        if "result" in task.info:
            response["result"] = task.info["result"]
    else:
        # Something went wrong in the task itself
        response = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),
            "result": str(task.info)
        }
    return response


