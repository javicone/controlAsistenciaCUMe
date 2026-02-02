import asyncio
import logging.config
import os
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Cargar variables de entorno primero
load_dotenv()

# Configuración
from middleware.cors import setup_cors
from routers import auth, asistencias, aulas, clases, websockets, views
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

# Configurar CORS
setup_cors(app)

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