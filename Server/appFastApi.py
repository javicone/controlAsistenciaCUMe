import logging
import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Configuración
from middleware.cors import setup_cors

# Routers
from routers import auth, asistencias, aulas, clases, websockets, views

# Utils
from utils.database_pool import close_db_pool

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

# Eventos de ciclo de vida
@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Servidor iniciado")

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()
    logging.info("🔒 Servidor detenido")

# Ejecutar servidor
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Iniciando servidor FastAPI...")
    print("="*60)
    
    ssl_keyfile = "./key.pem"
    ssl_certfile = "./cert.pem"
    ssl_enabled = os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile)
    
    if ssl_enabled:
        print("🔒 SSL/TLS HABILITADO ✅")
        print(f"   📍 https://0.0.0.0:5000")
        print(f"   📚 https://0.0.0.0:5000/docs")
        print(f"   🔌 wss://0.0.0.0:5000/ws")
    else:
        print("⚠️ SSL/TLS DESHABILITADO")
        ssl_keyfile = None
        ssl_certfile = None
    
    print("="*60 + "\n")
    
    uvicorn.run(
        "appFastApi:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )