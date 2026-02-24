import asyncio
import logging.config
import os
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from dotenv import load_dotenv

# Cargar variables de entorno primero
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Configuración
from middleware.cors import setup_cors
from middleware.rate_limit import rate_limit_exceeded_handler
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import auth, asistencias, aulas, clases, websockets, views, usuarios, gestion_crud
from utils.database_pool import close_db_pool, get_db_pool

# Configuración de logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['default'],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Configurar SSL
def configure_ssl(base_dir: Path) -> tuple[str | None, str | None]:
    """Configura SSL si los certificados existen"""
    key_file = base_dir / "keys" / "key_https.pem"
    cert_file = base_dir / "keys" / "cert_https.pem"
    
    if key_file.exists() and cert_file.exists():
        print("🔒 SSL/TLS HABILITADO ✅")
        print(f"   📍 https://0.0.0.0:8000")
        return str(key_file), str(cert_file)
    else:
        print(f"⚠️ SSL/TLS DESHABILITADO")
        print(f"   📍 http://0.0.0.0:8000")
        return None, None

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Servidor iniciado")
    try:
        pool = await asyncio.wait_for(get_db_pool(), timeout=10.0)
        logger.info(f"✅ Pool inicializado: {pool.size}/{pool.maxsize} conexiones")
    except Exception as e:
        logger.error(f"❌ Error inicializando pool: {e}")
    
    yield  # Servidor funcionando
    
    # Shutdown
    await close_db_pool()
    logger.info("🔒 Servidor detenido")

# Crear aplicación
app = FastAPI(
    title="Sistema de Control de Asistencia",
    description="API para gestión de asistencias y monitoreo de aulas",
    version="2.0.0",
    lifespan=lifespan
)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configurar CORS
setup_cors(app)

# Templates para páginas de error
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Manejadores de excepciones personalizados
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Maneja errores HTTP (404, 403, etc.) mostrando error.html"""
    
    # Mapeo de códigos de error comunes
    error_messages = {
        404: "No hemos podido encontrar la página que buscas.",
        403: "No tienes permiso para acceder a este recurso.",
        401: "Debes iniciar sesión para acceder a este recurso.",
        500: "Ha ocurrido un error interno en el servidor.",
        503: "El servicio no está disponible temporalmente."
    }
    
    # Obtener mensaje personalizado o usar el del error
    message = error_messages.get(exc.status_code, exc.detail or "Ha ocurrido un error.")
    
    # Renderizar directamente error.html
    return templates.TemplateResponse(
        "error.html",
        {"request": request},
        status_code=exc.status_code,
        headers={"X-Error-Code": str(exc.status_code), "X-Error-Message": message}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de datos"""
    logger.error(f"Error de validación: {exc}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request},
        status_code=400,
        headers={"X-Error-Code": "400", "X-Error-Message": "Los datos enviados no son válidos."}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja excepciones no controladas"""
    logger.error(f"Error no controlado: {exc}", exc_info=True)
    return templates.TemplateResponse(
        "error.html",
        {"request": request},
        status_code=500,
        headers={"X-Error-Code": "500", "X-Error-Message": "Ha ocurrido un error inesperado."}
    )

# Archivos estáticos
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info("✅ Archivos estáticos montados")

# Routers
app.include_router(views.router)
app.include_router(auth.router, prefix="")
app.include_router(asistencias.router)
app.include_router(aulas.router)
app.include_router(clases.router)
app.include_router(usuarios.router)
app.include_router(gestion_crud.router)
app.include_router(websockets.router)

# Health check mejorado
@app.get("/health")
async def health_check():
    """Verifica el estado del servidor y base de datos"""
    try:
        pool = await get_db_pool()
        return {
            "status": "ok",
            "database": "connected",
            "pool_size": f"{pool.size}/{pool.maxsize}"
        }
    except Exception as e:
        return {
            "status": "error", 
            "database": "disconnected",
            "error": str(e)
        }

# Ejecutar servidor
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Iniciando servidor FastAPI...")
    
    ssl_keyfile, ssl_certfile = configure_ssl(BASE_DIR)
    
    print("="*60 + "\n")
    
    uvicorn.run(
        "appFastApi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        ws_ping_interval=None,
        ws_ping_timeout=None,
    )