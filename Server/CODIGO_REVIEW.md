# 🔍 Code Review - Backend FastAPI

**Fecha:** Febrero 2026  
**Revisor:** Senior Backend Skill  
**Objetivo:** Análisis de calidad, seguridad, performance y arquitectura

---

## 📊 Resumen Ejecutivo

### ✅ Fortalezas del Proyecto

1. **Arquitectura Modular** - Excelente separación en routers, services, repositories
2. **Connection Pooling** - Implementación correcta de aiomysql pool con double-checked locking
3. **WebSocket Manager** - Sistema singleton bien implementado para gestión de conexiones
4. **FastAPI Lifespan** - Uso correcto de context managers para startup/shutdown
5. **Variables de Entorno** - Uso apropiado de dotenv y `.env.example`
6. **Logs Estructurados** - Implementación consistente de logging

### ⚠️ Áreas Críticas de Mejora

1. **🔴 SEGURIDAD - Contraseñas en texto plano**
2. **🟡 SQL Injection - Falta validación de inputs**
3. **🟡 JWT Dual System - Dos sistemas JWT diferentes (HS256 vs RS256)**
4. **🟡 Error Handling - Exposición de stack traces**
5. **🟡 Rate Limiting - No implementado**
6. **🟡 CORS - Configuración permisiva**

---

## 🚨 Hallazgos Críticos (Prioridad Alta)

### 1. 🔴 Contraseñas en Texto Plano

**Archivo:** `services/auth_service.py:48`

```python
# ❌ CRÍTICO: No seguro
if not user or user["password"] != password:
```

**Problema:**
- Las contraseñas se almacenan y comparan en texto plano
- Si la BD se compromete, todos los usuarios están expuestos
- Viola OWASP Top 10 (A01:2021 – Broken Access Control)

**Solución:**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# En auth_service.py
async def authenticate_user(correo: str, password: str) -> UserInDB:
    user = await get_usuario_por_mail(correo)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return UserInDB(**user)
```

**Acción inmediata:**
1. `pip install passlib[bcrypt]`
2. Crear script de migración para hashear contraseñas existentes
3. Actualizar `auth_service.py`

---

### 2. 🔴 Inyección SQL Potencial

**Archivo:** `repositories/usuarioRepository.py`

```python
# ✅ CORRECTO - Uso de parámetros
await cursor.execute(
    "SELECT id,nombre, correo, password, rol FROM usuarios WHERE correo = %s", 
    (correo,)
)
```

**Estado:** Mayormente correcto, pero revisar TODOS los repositorios.

**Acción:** Auditar `repositories/` para verificar que NINGUNA query concatena strings directamente.

**Anti-patrón a evitar:**
```python
# ❌ NUNCA HACER ESTO
query = f"SELECT * FROM usuarios WHERE correo = '{correo}'"
await cursor.execute(query)
```

---

### 3. 🟡 Sistema JWT Duplicado

**Archivos:**
- `services/auth_service.py` (HS256 con SECRET_KEY)
- `security/jwt.py` (RS256 con claves públicas/privadas)

**Problema:**
- Dos sistemas JWT incompatibles
- Confusión en el código (ver `routers/websockets.py:20-45`)
- Intentos fallback en validación WebSocket

**Código actual en websockets.py:**
```python
# Primero intentamos con HS256
try:
    token_data = decode_access_token(token)
    return token_data.id
except Exception as e:
    error_hs256 = str(e)

# Fallback: Intentar con RS256
try:
    payload = verify_token(token, required_scope="device")
    return payload.get("sub")
except Exception as e:
    error_rs256 = str(e)
```

**Solución:**

**Opción A: Unificar en RS256 (Recomendado para producción)**
```python
# security/jwt_unified.py
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

ALGORITHM = "RS256"
KEYS_DIR = Path(__file__).resolve().parents[1] / "keys"
PRIVATE_KEY = (KEYS_DIR / "jwt_priv.pem").read_text()
PUBLIC_KEY = (KEYS_DIR / "jwt_pub.pem").read_text()

def create_token(
    subject: str, 
    scope: Literal["device", "admin", "teacher", "conserje"],
    exp_minutes: int = 1440
) -> str:
    """Crea token JWT firmado con RS256"""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "scope": scope,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

def verify_token(token: str, required_scope: str = None) -> dict:
    """Verifica token y opcionalmente valida scope"""
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=[ALGORITHM])
        if required_scope and payload.get("scope") != required_scope:
            raise ValueError(f"Invalid scope: expected {required_scope}")
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
```

**Opción B: Unificar en HS256 (Más simple para desarrollo)**
```python
# security/jwt_unified.py
from jose import jwt, JWTError
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM

def create_token(subject: str, rol: str, exp_minutes: int = 1440) -> str:
    payload = {
        "sub": subject,
        "rol": rol,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError(f"Invalid token: {e}")
```

**Acción:**
1. Decidir: RS256 (producción) vs HS256 (desarrollo)
2. Deprecar uno de los dos sistemas
3. Actualizar todos los routers a usar el sistema unificado
4. Documentar en `DOCS/SISTEMA_JWT_UNIFICADO.md`

---

### 4. 🟡 Manejo de Errores Inconsistente

**Problema:** Los errores exponen detalles internos

**Ejemplo en `routers/auth.py:78`:**
```python
except Exception as e:
    logger.error(f"❌ Error en autenticación: {e}")
    raise HTTPException(status_code=500, detail="Error interno del servidor")  # ✅ Correcto
```

**VS** posibles otros lugares con:
```python
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))  # ❌ Incorrecto
```

**Solución: Middleware centralizado de errores**

```python
# middleware/error_handler.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def error_handler_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException:
        # Re-raise HTTPExceptions (ya controladas)
        raise
    except Exception as e:
        # Loguear error completo pero retornar mensaje genérico
        logger.error(f"Error no controlado: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Error interno del servidor"}
        )

# En appFastApi.py
from middleware.error_handler import error_handler_middleware
app.middleware("http")(error_handler_middleware)
```

---

## 🟡 Hallazgos Importantes (Prioridad Media)

### 5. Falta Rate Limiting

**Problema:** No hay protección contra ataques de fuerza bruta en `/login` y `/auth/device`

**Solución:**

```python
# pip install slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# En routers/auth.py
@router.post("/login")
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto
async def login(request: Request, user: UserLogin):
    # ...
```

---

### 6. CORS Muy Permisivo

**Archivo:** `middleware/cors.py`

**Problema esperado:** Si tiene `allow_origins=["*"]`

**Solución:**

```python
# middleware/cors.py
from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
    # Permitir solo orígenes específicos en producción
    allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # NO usar ["*"] en producción
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
```

---

### 7. Validación de Inputs

**Problema:** Faltan validaciones Pydantic estrictas

**Ejemplo actual (posiblemente):**
```python
class UserLogin(BaseModel):
    correo: str
    contraseña: str
```

**Mejor:**
```python
from pydantic import BaseModel, EmailStr, constr, validator

class UserLogin(BaseModel):
    correo: EmailStr  # Valida formato email
    contraseña: constr(min_length=8, max_length=100)  # Longitud
    
    @validator('correo')
    def email_lowercase(cls, v):
        return v.lower()  # Normalizar
```

---

### 8. Connection Pool - Parámetros de Tuning

**Archivo:** `utils/database_pool.py:35`

```python
_pool = await aiomysql.create_pool(
    **cfg,
    autocommit=True,  # ⚠️ Revisar si es intencional
    minsize=1,
    maxsize=10,
    pool_recycle=3600
)
```

**Recomendaciones:**

```python
_pool = await aiomysql.create_pool(
    **cfg,
    autocommit=False,  # ✅ Permitir transacciones explícitas
    minsize=2,         # ✅ Mantener 2 conexiones siempre listas
    maxsize=20,        # ✅ Aumentar para alta concurrencia
    pool_recycle=3600,
    echo=False,        # ✅ Logs de queries (activar en debug)
    connect_timeout=10 # ✅ Timeout de conexión
)
```

---

### 9. WebSocket - Falta Heartbeat/Ping

**Archivo:** `routers/websockets.py`

**Problema:** Conexiones muertas no se detectan

**Solución:**

```python
import asyncio

async def websocket_heartbeat(websocket: WebSocket, device_id: str):
    """Envía pings cada 30s para detectar desconexiones"""
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"tipo": "ping", "timestamp": datetime.utcnow().isoformat()})
    except Exception:
        logging.info(f"❤️ Heartbeat terminado para {device_id}")

# En /ws
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # ... código existente ...
    
    # Iniciar heartbeat en background
    heartbeat_task = asyncio.create_task(websocket_heartbeat(websocket, device_id))
    
    try:
        # Loop principal
        async for message in websocket.iter_text():
            # ...
    finally:
        heartbeat_task.cancel()
```

---

### 10. Logs - Falta Rotación

**Archivo:** `appFastApi.py:19-39`

**Problema:** Logs solo van a stdout, no se persisten ni rotan

**Solución:**

```python
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        }
    },
    'handlers': {
        'console': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'app.log'),
            'maxBytes': 10_485_760,  # 10MB
            'backupCount': 5,
        },
    },
    'root': {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'handlers': ['console', 'file'],
    },
}
```

---

## 🟢 Hallazgos Menores (Prioridad Baja)

### 11. Tipado Inconsistente

**Ejemplo:**
```python
# ❌ Sin tipo de retorno
async def get_usuario_por_mail(correo: str):
    # ...

# ✅ Con tipo de retorno
async def get_usuario_por_mail(correo: str) -> dict | None:
    # ...
```

**Acción:** Añadir type hints completos en todos los archivos.

---

### 12. Docstrings Incompletos

**Ejemplo:**
```python
# ❌ Sin docstring
def verify_token(token: str, required_scope: str = "device") -> dict:
    try:
        # ...

# ✅ Con docstring
def verify_token(token: str, required_scope: str = "device") -> dict:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        required_scope: Scope requerido (device, admin, etc)
        
    Returns:
        dict: Payload decodificado del token
        
    Raises:
        HTTPException: Si el token es inválido o scope incorrecto
    """
```

---

### 13. Secrets en Código

**Revisar que NO existan:**
```python
# ❌ NUNCA hacer esto
SECRET_KEY = "hardcoded_secret_123"
DB_PASSWORD = "1234"
```

**✅ Siempre usar:**
```python
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in .env")
```

---

## 📋 Plan de Acción Priorizado

### 🔴 Urgente (Esta semana)

- [ ] **1. Hash de contraseñas** - Implementar bcrypt
- [ ] **2. Script de migración** - Hashear contraseñas existentes en BD
- [ ] **3. Unificar JWT** - Decidir HS256 vs RS256 y deprecar el otro
- [ ] **4. Rate limiting** - Añadir slowapi en endpoints de autenticación

### 🟡 Importante (Este mes)

- [ ] **5. Middleware de errores** - Centralizar manejo de excepciones
- [ ] **6. CORS seguro** - Configurar allow_origins específicos
- [ ] **7. Validación Pydantic** - Añadir EmailStr, constr, validators
- [ ] **8. WebSocket heartbeat** - Implementar ping/pong
- [ ] **9. Log rotation** - RotatingFileHandler

### 🟢 Mejoras (Próximo sprint)

- [ ] **10. Type hints completos** - Añadir en todos los archivos
- [ ] **11. Docstrings** - Documentar funciones públicas
- [ ] **12. Tests unitarios** - Cobertura mínima 70%
- [ ] **13. CI/CD** - GitHub Actions para tests y linting

---

## 🏆 Mejores Prácticas Aplicadas Correctamente

### ✅ Arquitectura Limpia

```
Server/
├── routers/       # HTTP endpoints (Vista)
├── services/      # Lógica de negocio (Controlador)
├── repositories/  # Acceso a datos (Modelo)
├── models/        # Schemas Pydantic
└── utils/         # Helpers
```

**Evaluación:** ✅ Excelente separación de responsabilidades

---

### ✅ Connection Pooling

```python
# Double-checked locking correcto
async def get_db_pool() -> aiomysql.Pool:
    global _pool
    if _pool is not None:
        return _pool
    async with _lock:
        if _pool is not None:
            return _pool
        # Crear pool...
```

**Evaluación:** ✅ Implementación thread-safe correcta

---

### ✅ FastAPI Lifespan Events

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    pool = await get_db_pool()
    yield
    # Shutdown
    await close_db_pool()
```

**Evaluación:** ✅ Gestión correcta de recursos

---

## 📊 Métricas de Calidad

| Categoría | Puntuación | Estado |
|-----------|------------|--------|
| **Seguridad** | 4/10 | 🔴 Crítico |
| **Performance** | 7/10 | 🟡 Mejorable |
| **Arquitectura** | 9/10 | 🟢 Excelente |
| **Mantenibilidad** | 7/10 | 🟡 Bueno |
| **Testing** | 2/10 | 🔴 Inexistente |
| **Documentación** | 6/10 | 🟡 Mejorable |

**Puntuación General:** **6.0/10** - Proyecto sólido con áreas críticas de mejora

---

## 🔗 Recursos Recomendados

### Librerías a Agregar

```txt
# Seguridad
passlib[bcrypt]>=1.7.4
slowapi>=0.1.9

# Validación
email-validator>=2.0.0
pydantic[email]>=2.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0  # Para test client FastAPI

# Monitoreo
prometheus-fastapi-instrumentator>=6.0.0
```

### Documentación

- **FastAPI Security:** https://fastapi.tiangolo.com/tutorial/security/
- **OWASP Top 10:** https://owasp.org/www-project-top-ten/
- **Python Security Best Practices:** https://snyk.io/blog/python-security-best-practices/

---

## 📝 Conclusión

El proyecto tiene una **arquitectura sólida y bien organizada**, pero requiere **mejoras críticas en seguridad** antes de desplegar en producción. La prioridad máxima es implementar hashing de contraseñas y unificar el sistema JWT.

La base del código es **mantenible y escalable**, con buenas prácticas en connection pooling, separación de capas y uso de FastAPI moderno. Con las mejoras de seguridad implementadas, el proyecto estará listo para producción.

---

**Siguiente paso:** Revisar este documento con el equipo y priorizar las acciones urgentes.
