# main.py
import logging
import asyncio
import json
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any

import uvicorn
from pathlib import Path

# Framework y servidor
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Seguridad y JWT
from jose import JWTError, jwt
from passlib.context import CryptContext

# Modelos de datos con Pydantic
from pydantic import BaseModel

# Base de datos asíncrona
import aiomysql 
from database import DB_CONFIG # Asumimos que tienes un dict de configuración
from config import SECRET_KEY
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

#importamos uvicorn para lanzar el servidor
import uvicorn

# --- Configuración Inicial ---
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Agregar esto después de los imports y antes de crear la app


# Obtener el directorio donde está este archivo
BASE_DIR = Path(__file__).parent

# Definir rutas
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

print(f"🔍 Directorio base: {BASE_DIR}")
print(f"🔍 Buscando static en: {STATIC_DIR}")
print(f"🔍 Buscando templates en: {TEMPLATES_DIR}")
print(f"📂 Static existe: {STATIC_DIR.exists()}")
print(f"📂 Templates existe: {TEMPLATES_DIR.exists()}")



app = FastAPI()

# Middleware CORS ESTO HAY Q QUITARLO EN PRODUCCION
from fastapi.middleware.cors import CORSMiddleware
# Añadir justo después de crear la app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://10.153.102.94:5000",
         "http://localhost:5000",
        # añadir otros orígenes de UI si hace falta
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
# Verificar que las carpetas existen antes de montar
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    print("✅ Static files montados correctamente")
else:
    print("❌ Error: La carpeta 'static' no existe")
    print(f"📁 Estructura actual en {BASE_DIR}:")
    for item in BASE_DIR.iterdir():
        print(f"   {'📂' if item.is_dir() else '📄'} {item.name}")

if TEMPLATES_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    print("✅ Templates configurados correctamente")
else:
    print("❌ Error: La carpeta 'templates' no existe")
    templates = None

# --- Modelos Pydantic (Validación Automática) ---
# Pydantic reemplaza la validación manual y request.get_json()

class UserLogin(BaseModel):
    correo: str
    password: str

class AulaLogin(BaseModel):
    nombre_aula: str
    password_aula: str
    
class RegistroAsistencia(BaseModel):
    uid: str
    nombre_aula: str

class DatosAula(BaseModel):
    aula: str
    temperatura: float
    luz: float
    personas: int
    clase_en_curso: bool
    
class Clase(BaseModel):
    asignatura: str
    hora_inicio: datetime
    hora_fin: datetime

class ControlRelay(BaseModel):
    aula: str
    relay: bool

class TokenData(BaseModel):
    id: str | None = None
    rol: str | None = None

# --- Seguridad con JWT ---
# Esto reemplaza a Flask-JWT-Extended


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para obtener el usuario actual desde el token
async def get_current_user(token: str = Depends(OAuth2)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        rol: str = payload.get("rol")
        if user_id is None or rol is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, rol=rol)
    except JWTError:
        raise credentials_exception
    return token_data


# --- Base de Datos Asíncrona ---
async def get_db_pool():
    """
    Crea el pool corrigiendo claves incompatibles en DB_CONFIG:
    - transforma 'database' -> 'db' para aiomysql
    """
    # DB_CONFIG viene de tu módulo database (asumimos dict)
    cfg = dict(DB_CONFIG) if isinstance(DB_CONFIG, dict) else dict(vars(DB_CONFIG))
    # mapear llave 'database' a 'db' si existe
    if "database" in cfg and "db" not in cfg:
        cfg["db"] = cfg.pop("database")
    # opcional: mapear 'passwd'/'password' según tu config
    if "password" in cfg and "passwd" not in cfg:
        # aiomysql acepta 'password' pero si tienes 'passwd' puedes mapear al revés; aquí no hacemos nada
        pass

    try:
        pool = await aiomysql.create_pool(**cfg, autocommit=True)
        return pool
    except TypeError as e:
        # mostrar info útil para debug
        raise RuntimeError(f"Error creando pool aiomysql — parámetros enviados: {list(cfg.keys())} — {e}")
# ...existing code...

# --- Gestor de Conexiones WebSocket ---
# Una clase para manejar los clientes conectados de forma limpia
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        json_message = json.dumps(message)
        for connection in self.active_connections:
            await connection.send_text(json_message)

manager = ConnectionManager()
aulas_estado: Dict[str, Any] = {} # Mantenemos el estado en memoria

# --- Endpoints ---

# Servir plantillas HTML (equivalente a render_template)
# Reemplazar las líneas 130-139 con esto:

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    if templates is None:
        return HTMLResponse("""
        <h1>Control de Asistencia</h1>
        <p>Sistema en modo desarrollo - Templates no configurados</p>
        <p><a href="/docs">📚 Ver documentación API</a></p>
        """)
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return HTMLResponse(f"<h1>Error</h1><p>Error cargando template: {str(e)}</p>")

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    if templates is None:
        return HTMLResponse("""
        <h1>Dashboard de Profesores</h1>
        <p>Panel en modo desarrollo</p>
        <p><a href="/">🏠 Volver al inicio</a></p>
        """)
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request})
    except Exception as e:
        return HTMLResponse(f"<h1>Dashboard</h1><p>Error: {str(e)}</p>")

@app.get("/conserjes", response_class=HTMLResponse)
async def get_conserjes(request: Request):
    if templates is None:
        return HTMLResponse("""
        <h1>Panel de Conserjes</h1>
        <p>Panel en modo desarrollo</p>
        <p><a href="/">🏠 Volver al inicio</a></p>
        """)
    try:
        return templates.TemplateResponse("conserjes.html", {"request": request})
    except Exception as e:
        return HTMLResponse(f"<h1>Panel de Conserjes</h1><p>Error: {str(e)}</p>")
# --- Endpoints de la API ---

@app.post("/login")
async def login(user_data: UserLogin):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT id, rol, password FROM usuarios WHERE correo = %s", (user_data.correo,))
            user = await cursor.fetchone()

    pool.close()
    await pool.wait_closed()

    if not user or user["password"] != user_data.password: # En producción, usa passlib para verificar hash
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    access_token = create_access_token(data={"sub": str(user["id"]), "rol": user["rol"]})
    return {"token": access_token, "rol": user["rol"]}


@app.post("/registro")
async def registrar_asistencia(registro: RegistroAsistencia):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Obtener usuario_id
            await cursor.execute("SELECT id FROM usuarios WHERE uid_tarjeta = %s", (registro.uid,))
            usuario = await cursor.fetchone()
            if not usuario:
                raise HTTPException(status_code=404, detail="Profesor no encontrado")
            
            # Obtener aula_id
            await cursor.execute("SELECT id FROM aulas WHERE nombre = %s", (registro.nombre_aula,))
            aula = await cursor.fetchone()
            if not aula:
                raise HTTPException(status_code=404, detail="Aula no encontrada")

            # Insertar asistencia
            fecha_hora = datetime.now()
            await cursor.execute(
                "INSERT INTO asistencias (usuario_id, aula_id, fecha_hora) VALUES (%s, %s, %s)",
                (usuario["id"], aula["id"], fecha_hora)
            )
            # await conn.commit() # No es necesario con autocommit=True

    pool.close()
    await pool.wait_closed()
    return {
        "mensaje": "Asistencia registrada",
        "usuario_id": usuario["id"],
        "aula_id": aula["id"],
        "fecha_hora": fecha_hora.isoformat()
    }


@app.get("/asistencias")
async def obtener_asistencias(current_user: TokenData = Depends(get_current_user)):
    # El rol y el id vienen de la dependencia get_current_user
    rol = current_user.rol
    user_id = current_user.id
    
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            if rol == "profesor":
                await cursor.execute("SELECT * FROM asistencias WHERE usuario_id = %s", (user_id,))
            elif rol in ["conserje", "administrador"]:
                await cursor.execute("SELECT * FROM asistencias")
            else:
                raise HTTPException(status_code=403, detail="Acceso denegado")
            
            asistencias = await cursor.fetchall()

    pool.close()
    await pool.wait_closed()
    return asistencias


@app.post("/datos_aula")
async def recibir_datos_aula(datos: DatosAula):
    # Actualizar en memoria
    aulas_estado[datos.aula] = {
        "temperatura": datos.temperatura,
        "luz": datos.luz,
        "personas": datos.personas,
        "clase_en_curso": datos.clase_en_curso,
        "relay": aulas_estado.get(datos.aula, {}).get("relay", False),
    }
    
    # Difundir a todos los clientes WebSocket
    # La llamada es directa y asíncrona, sin hilos.
    await manager.broadcast({
        "tipo": "actualizacion_aula",
        "aula": datos.aula,
        **aulas_estado[datos.aula]
    })
    
    return {"mensaje": "Datos actualizados correctamente"}

@app.get("/estado_aulas")
async def obtener_estado_aulas():
    return aulas_estado

@app.post("/control_relay")
async def controlar_relay(control: ControlRelay):
    if control.aula not in aulas_estado:
        raise HTTPException(status_code=404, detail="Aula no encontrada")
    
    # Actualizar estado del relay
    aulas_estado[control.aula]["relay"] = control.relay
    
    # Difundir a todos los clientes WebSocket
    await manager.broadcast({
        "tipo": "actualizacion_relay",
        "aula": control.aula,
        "relay": control.relay,
        **aulas_estado[control.aula]
    })
    
    return {"mensaje": f"Relay en aula {control.aula} actualizado a {control.relay}"}
# Agregar este endpoint después de los otros

@app.get("/proxima_clase_test")
async def obtener_clase_test(aula: str):
    """
    Endpoint de prueba que devuelve datos simulados
    """
    from datetime import datetime, timedelta
    
    # Obtener la hora actual + 1 hora como inicio
    ahora = datetime.now()
    hora_inicio = ahora + timedelta(hours=1)
    hora_fin = hora_inicio + timedelta(hours=1, minutes=30)  # 1.5 horas de duración
    
    return {
        "asignatura": "Fundamentos de Programación",
        "hora_inicio": hora_inicio.strftime("%H:%M:%S"),
        "hora_fin": hora_fin.strftime("%H:%M:%S"),
    }

@app.get("/proxima_clase")
async def obtener_clase_actual(aula: str):
    """
    Obtiene la clase que está actualmente en curso o la próxima clase en el aula especificada
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Primero, buscar clase actual (en curso)
            query_actual = """
            SELECT c.asignatura, c.hora_inicio, c.hora_fin 
            FROM clases c 
            JOIN aulas a ON c.aula_id = a.id 
            WHERE a.nombre = %s 
                AND CURTIME() BETWEEN c.hora_inicio AND c.hora_fin
                AND CURDATE() = DATE(c.fecha)
            ORDER BY c.hora_inicio ASC 
            LIMIT 1
            """
            await cursor.execute(query_actual, (aula,))
            clase_actual = await cursor.fetchone()
            
            # Si no hay clase actual, buscar la próxima clase
            if not clase_actual:
                query_proxima = """
                SELECT c.asignatura, c.hora_inicio, c.hora_fin 
                FROM clases c 
                JOIN aulas a ON c.aula_id = a.id 
                WHERE a.nombre = %s 
                    AND c.hora_inicio > CURTIME()
                    AND CURDATE() = DATE(c.fecha)
                ORDER BY c.hora_inicio ASC 
                LIMIT 1
                """
                await cursor.execute(query_proxima, (aula,))
                clase_proxima = await cursor.fetchone()
                
                if not clase_proxima:
                    # No hay clases hoy, buscar próxima clase en días siguientes
                    query_siguiente = """
                    SELECT c.asignatura, c.hora_inicio, c.hora_fin, c.fecha
                    FROM clases c 
                    JOIN aulas a ON c.aula_id = a.id 
                    WHERE a.nombre = %s 
                        AND c.fecha > CURDATE()
                    ORDER BY c.fecha ASC, c.hora_inicio ASC 
                    LIMIT 1
                    """
                    await cursor.execute(query_siguiente, (aula,))
                    clase_siguiente = await cursor.fetchone()
                    
                    if not clase_siguiente:
                        pool.close()
                        await pool.wait_closed()
                        raise HTTPException(
                            status_code=404, 
                            detail=f"No se encontraron clases para el aula {aula}"
                        )
                    
                    pool.close()
                    await pool.wait_closed()
                    return {
                        "aula": aula,
                        "asignatura": clase_siguiente["asignatura"],
                        "hora_inicio": clase_siguiente["hora_inicio"].strftime("%H:%M:%S"),
                        "hora_fin": clase_siguiente["hora_fin"].strftime("%H:%M:%S"),
                        "fecha": clase_siguiente["fecha"].strftime("%Y-%m-%d"),
                        "estado": "proxima_fecha"
                    }
                
                pool.close()
                await pool.wait_closed()
                return {
                    "aula": aula,
                    "asignatura": clase_proxima["asignatura"],
                    "hora_inicio": clase_proxima["hora_inicio"].strftime("%H:%M:%S"),
                    "hora_fin": clase_proxima["hora_fin"].strftime("%H:%M:%S"),
                    "estado": "proxima"
                }
            
            # Hay clase actual
            pool.close()
            await pool.wait_closed()
            return {
                "aula": aula,
                "asignatura": clase_actual["asignatura"],
                "hora_inicio": clase_actual["hora_inicio"].strftime("%H:%M:%S"),
                "hora_fin": clase_actual["hora_fin"].strftime("%H:%M:%S"),
                "estado": "en_curso"
            }

# También puedes crear un endpoint más específico solo para clase actual
@app.get("/clase_actual")
async def obtener_solo_clase_actual(aula: str):
    """
    Obtiene únicamente la clase que está en curso en este momento
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
            SELECT c.asignatura, c.hora_inicio, c.hora_fin 
            FROM clases c 
            JOIN aulas a ON c.aula_id = a.id 
            WHERE a.nombre = %s 
                AND CURTIME() BETWEEN c.hora_inicio AND c.hora_fin
                AND CURDATE() = DATE(c.fecha)
            ORDER BY c.hora_inicio ASC 
            LIMIT 1
            """
            await cursor.execute(query, (aula,))
            clase = await cursor.fetchone()
    
    pool.close()
    await pool.wait_closed()
    
    if not clase:
        return {
            "aula": aula,
            "asignatura": None,
            "hora_inicio": None,
            "hora_fin": None,
            "estado": "sin_clase"
        }
    
    return {
        "aula": aula,
        "asignatura": clase["asignatura"],
        "hora_inicio": clase["hora_inicio"].strftime("%H:%M:%S"),
        "hora_fin": clase["hora_fin"].strftime("%H:%M:%S"),
        "estado": "en_curso"
    }

# --- Endpoint WebSocket ---
# Esto reemplaza el servidor de websockets y el ws_handler
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Enviar estado inicial al conectar
    await websocket.send_json({
        "tipo": "estado_inicial",
        "data": aulas_estado
    })

    try:
        while True:
            # Puedes dejar esto si esperas mensajes del cliente
            data = await websocket.receive_text()
            logging.info(f"Mensaje recibido por WS: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info("Cliente WebSocket desconectado.")



 #--- Ejecución del servidor ---
if __name__ == "__main__":
    print("🚀 Iniciando servidor FastAPI...")
    print("📂 Directorio actual:", os.getcwd())
    print("🌐 Servidor disponible en: http://0.0.0.0:5000")
    print("📚 Documentación en: http://0.0.0.0:5000/docs")
    uvicorn.run("appFastApi:app", host="0.0.0.0", port=5000, reload=True)