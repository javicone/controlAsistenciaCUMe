from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import logging
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Ruta raíz simplificada sin dependencia de DB"""
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logging.error(f"Error en ruta raíz: {e}")
        return HTMLResponse(content=f"<h1>Error: {e}</h1>", status_code=500)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    """Dashboard principal"""
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        logging.error(f"Error en dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/administrador", response_class=HTMLResponse)
async def administrador_view(request: Request):
    """Vista de administrador"""
    try:
        return templates.TemplateResponse("administrador.html", {"request": request})
    except Exception as e:
        logging.error(f"Error en admin: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/profesor/asistencias", response_class=HTMLResponse)
async def asistencias_profesor(request: Request):
    """Vista de asistencias para profesores"""
    try:
        return templates.TemplateResponse("asistencias_profesor.html", {"request": request})
    except Exception as e:
        logging.error(f"Error en asistencias profesor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conserjes", response_class=HTMLResponse)
async def panel_conserjes(request: Request):
    """Panel de conserjes"""
    try:
        return templates.TemplateResponse("conserjes.html", {"request": request})
    except Exception as e:
        logging.error(f"Error en panel conserjes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/gestion-aulas", response_class=HTMLResponse)
async def gestion_aulas(request: Request):
    """Gestión de aulas y dispositivos ESP32"""
    try:
        return templates.TemplateResponse("gestion_aulas.html", {"request": request})
    except Exception as e:
        logging.error(f"Error en gestión de aulas: {e}")
        raise HTTPException(status_code=500, detail=str(e))