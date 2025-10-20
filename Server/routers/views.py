from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["Vistas"])

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Control de Asistencia</h1><p><a href='/docs'>📚 API Docs</a></p>")
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Dashboard</h1><p><a href='/'>🏠 Inicio</a></p>")
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/conserjes", response_class=HTMLResponse)
async def conserjes(request: Request):
    if templates is None:
        return HTMLResponse("<h1>Conserjes</h1><p><a href='/'>🏠 Inicio</a></p>")
    return templates.TemplateResponse("conserjes.html", {"request": request})