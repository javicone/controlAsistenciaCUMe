import asyncio
import logging
import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

# Configuración
from middleware.cors import setup_cors

# JWT seguridad
from security import jwt

# Routers
from routers import auth, asistencias, aulas, clases, websockets, views

# Utils
from utils.database_pool import close_db_pool, get_db_pool

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Crear aplicación
app = FastAPI(
    title="Sistema de Control de Asistencia",
    description="API para gestión de asistencias y monitoreo de aulas",
    version="2.0.0"
)

# Configurar CORS
setup_cors(app)

# Montar archivos estáticos
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logging.info("✅ Archivos estáticos montados")

# Incluir routers
app.include_router(views.router)
app.include_router(auth.router, prefix="")  # monta /login y /auth/login
app.include_router(asistencias.router)
app.include_router(aulas.router)
app.include_router(clases.router)
app.include_router(websockets.router)

# Ruta de health check
@app.get("/health")
async def health_check():
    """Verifica el estado del servidor sin tocar la base de datos"""
    from utils.database_pool import _pool
    return {
        "status": "ok",
        "pool_initialized": _pool is not None
    }

# Eventos de ciclo de vida
@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Servidor iniciado")
    try:
        # Inicializar pool con timeout de forma no bloqueante
        asyncio.create_task(initialize_pool())
    except Exception as e:
        logging.error(f"❌ Error en startup: {e}")

async def initialize_pool():
    """Inicializa el pool de forma asíncrona sin bloquear el servidor"""
    try:
        pool = await asyncio.wait_for(get_db_pool(), timeout=10.0)
        logging.info(f"✅ Pool inicializado: {pool.size}/{pool.maxsize} conexiones")
    except asyncio.TimeoutError:
        logging.error("❌ Timeout inicializando pool de base de datos")
    except Exception as e:
        logging.error(f"❌ Error inicializando pool: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()
    logging.info("🔒 Servidor detenido")

# Ejecutar servidor
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Iniciando servidor FastAPI...")
       # --- INICIO DEL FIX: Usar rutas absolutas ---
    # 1. Definir las rutas absolutas usando BASE_DIR
    KEY_FILE_PATH = BASE_DIR / "keys" / "key_https.pem"
    CERT_FILE_PATH = BASE_DIR / "keys" / "cert_https.pem"
    
    # 2. Verificar existencia usando .exists() de pathlib
    ssl_enabled = KEY_FILE_PATH.exists() and CERT_FILE_PATH.exists()
    
    # 3. Asignar los valores para uvicorn
    if ssl_enabled:
        print("🔒 SSL/TLS HABILITADO ✅")
        print(f"   📍 https://0.0.0.0:8000")
        print(f"   📚 https://0.0.0.0:8000/docs")
        print(f"   🔌 wss://0.0.0.0:8000/ws")
        # Convertir Path objects a string para uvicorn
        ssl_keyfile = str(KEY_FILE_PATH)
        ssl_certfile = str(CERT_FILE_PATH)
    else:
        print(f"⚠️ SSL/TLS DESHABILITADO. Archivos no encontrados en: {KEY_FILE_PATH.parent.resolve()}")
        ssl_keyfile = None
        ssl_certfile = None
    
    print("="*60 + "\n")
    
    uvicorn.run(
        "appFastApi:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        # WebSocket config - desactivar ping del servidor para evitar conflictos
        # con el heartbeat del ESP32
        ws_ping_interval=None,  # Desactivar ping del servidor
        ws_ping_timeout=None,   # Sin timeout de ping
    )