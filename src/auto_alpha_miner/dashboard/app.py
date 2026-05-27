"""FastAPI application factory for the dashboard."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from auto_alpha_miner.config import DASHBOARD_API_KEY

_DASHBOARD_DIR = Path(__file__).parent
_TEMPLATES_DIR = _DASHBOARD_DIR / "templates"
_STATIC_DIR = _DASHBOARD_DIR / "static"

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

app = FastAPI(title="Auto Alpha Miner Dashboard")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/static"):
            return await call_next(request)
        api_key = (
            request.query_params.get("key")
            or request.headers.get("X-API-Key", "")
            or request.cookies.get("api_key", "")
        )
        if not api_key or api_key != DASHBOARD_API_KEY:
            from starlette.responses import HTMLResponse
            return HTMLResponse(
                content="""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="utf-8"><title>인증 필요</title>
<style>
body{font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#0f172a;color:#e2e8f0;}
.card{background:#1e293b;padding:2.5rem;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.4);text-align:center;max-width:420px;}
h1{font-size:1.5rem;margin-bottom:.5rem;}
p{color:#94a3b8;margin-bottom:1.5rem;}
input{padding:.75rem 1rem;border:1px solid #334155;border-radius:8px;background:#0f172a;color:#e2e8f0;width:100%;box-sizing:border-box;margin-bottom:1rem;font-size:1rem;}
button{padding:.75rem 1.5rem;background:#3b82f6;color:#fff;border:none;border-radius:8px;font-size:1rem;cursor:pointer;}
button:hover{background:#2563eb;}
.error{color:#f87171;margin-top:.75rem;display:none;}
</style></head>
<body>
<div class="card">
<h1>🔐 접근 권한 필요</h1>
<p>이 대시보드는 인증이 필요합니다.<br>API 키를 입력해주세요.</p>
<input type="password" id="keyInput" placeholder="API 키 입력" autofocus>
<button onclick="submitKey()">접속</button>
<p class="error" id="errorMsg">잘못된 키입니다.</p>
</div>
<script>
function submitKey(){var k=document.getElementById('keyInput').value;if(!k)return;var u=new URL(window.location);u.searchParams.set('key',k);window.location.href=u.toString();}
document.getElementById('keyInput').addEventListener('keydown',function(e){if(e.key==='Enter')submitKey();});
</script>
</body>
</html>""",
                status_code=401,
            )
        if request.query_params.get("key") and not request.cookies.get("api_key"):
            redirect = RedirectResponse(url=str(request.url.remove_query_params("key")), status_code=302)
            redirect.set_cookie(key="api_key", value=api_key, httponly=True, samesite="lax")
            return redirect
        return await call_next(request)


app.add_middleware(APIKeyMiddleware)

# Import and register routes
from auto_alpha_miner.dashboard.routes import overview, strategy, compare, research, portfolio  # noqa: E402

app.include_router(overview.router)
app.include_router(strategy.router)
app.include_router(compare.router)
app.include_router(portfolio.router)
app.include_router(research.router)
