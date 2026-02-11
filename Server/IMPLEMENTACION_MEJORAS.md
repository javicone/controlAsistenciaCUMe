# 🛠️ Implementación de Mejoras Críticas

**Para:** Equipo de desarrollo  
**De:** Code Review - Senior Backend Skill  
**Fecha:** Febrero 2026

Este documento contiene código listo para implementar las mejoras críticas identificadas en el code review.

---

## 📋 Índice de Implementaciones

1. [Hash de Contraseñas con Bcrypt](#1-hash-de-contraseñas)
2. [Sistema JWT Unificado](#2-sistema-jwt-unificado)
3. [Rate Limiting](#3-rate-limiting)
4. [Middleware de Errores](#4-middleware-de-errores)
5. [Validación de Inputs](#5-validación-de-inputs)
6. [CORS Seguro](#6-cors-seguro)
7. [Logs con Rotación](#7-logs-con-rotación)
8. [WebSocket Heartbeat](#8-websocket-heartbeat)

---

## 1. Hash de Contraseñas

### Paso 1: Instalar Dependencia

```bash
pip install passlib[bcrypt]
```

### Paso 2: Crear Módulo de Password Hashing

**Archivo:** `Server/security/password.py`

```python
from passlib.context import CryptContext
from typing import Tuple

# Configuración de bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Factor de trabajo (más alto = más seguro pero más lento)
)

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash bcrypt de la contraseña
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash bcrypt almacenado
        
    Returns:
        bool: True si la contraseña es correcta
    """
    return pwd_context.verify(plain_password, hashed_password)

def needs_rehash(hashed_password: str) -> bool:
    """
    Verifica si un hash necesita ser regenerado (por cambio de rounds).
    
    Args:
        hashed_password: Hash bcrypt existente
        
    Returns:
        bool: True si debe rehashear
    """
    return pwd_context.needs_update(hashed_password)
```

### Paso 3: Actualizar Auth Service

**Archivo:** `Server/services/auth_service.py`

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.user import TokenData, UserInDB
from utils.database_pool import get_db_pool
from repositories.usuarioRepository import get_usuario_por_mail
from security.password import verify_password  # ← NUEVO
import logging

logger = logging.getLogger(__name__)

def create_access_token(data: dict) -> str:
    """Crea un token JWT simple"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """Decodifica y valida un token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") or payload.get("id") or payload.get("device_id")
        rol: str = payload.get("rol")
        
        if user_id is None or rol is None:
            raise credentials_exception
            
        return TokenData(id=user_id, rol=rol)
        
    except JWTError:
        raise credentials_exception

async def authenticate_user(correo: str, password: str) -> UserInDB:
    """
    Autentica un usuario por correo y contraseña.
    
    ✅ ACTUALIZADO: Usa bcrypt para verificar contraseña hasheada
    """
    user = await get_usuario_por_mail(correo)
    
    if not user:
        logger.warning(f"❌ Intento de login fallido: usuario no existe ({correo})")
        # Delay para prevenir timing attacks
        verify_password("fake_password", "$2b$12$dummy_hash")
        raise HTTPException(
            status_code=401, 
            detail="Correo o contraseña incorrectos"
        )
    
    # ✅ CAMBIO PRINCIPAL: Verificar hash en vez de comparación directa
    if not verify_password(password, user["password"]):
        logger.warning(f"❌ Intento de login fallido: contraseña incorrecta ({correo})")
        raise HTTPException(
            status_code=401, 
            detail="Correo o contraseña incorrectos"
        )
    
    logger.info(f"✅ Login exitoso: {correo}")
    return UserInDB(**user)
```

### Paso 4: Script de Migración de Contraseñas

**Archivo:** `Server/scripts/migrate_passwords.py`

```python
#!/usr/bin/env python3
"""
Script para migrar contraseñas existentes de texto plano a bcrypt.

⚠️  EJECUTAR UNA SOLA VEZ en producción
⚠️  HACER BACKUP de la BD antes de ejecutar

Uso:
    python Server/scripts/migrate_passwords.py
"""

import asyncio
import sys
from pathlib import Path

# Añadir Server/ al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.database_pool import get_db_pool, close_db_pool
from security.password import hash_password
import aiomysql

async def migrate_passwords():
    """Migra todas las contraseñas de texto plano a bcrypt"""
    
    print("🔐 Iniciando migración de contraseñas...")
    print("⚠️  ASEGÚRATE DE TENER UN BACKUP DE LA BASE DE DATOS\n")
    
    respuesta = input("¿Continuar? (sí/no): ")
    if respuesta.lower() not in ['sí', 'si', 'yes', 's', 'y']:
        print("❌ Migración cancelada")
        return
    
    try:
        pool = await get_db_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                # 1. Obtener todos los usuarios
                await cursor.execute("SELECT id, correo, password FROM usuarios")
                usuarios = await cursor.fetchall()
                
                if not usuarios:
                    print("⚠️  No hay usuarios en la base de datos")
                    return
                
                print(f"\n📊 Encontrados {len(usuarios)} usuarios")
                
                # 2. Verificar si ya están hasheadas (bcrypt starts with $2b$)
                ya_hasheadas = sum(1 for u in usuarios if u['password'].startswith('$2b$'))
                
                if ya_hasheadas == len(usuarios):
                    print("✅ Todas las contraseñas ya están hasheadas")
                    return
                
                print(f"   - {ya_hasheadas} ya hasheadas")
                print(f"   - {len(usuarios) - ya_hasheadas} por hashear\n")
                
                # 3. Hashear contraseñas pendientes
                migradas = 0
                for usuario in usuarios:
                    if not usuario['password'].startswith('$2b$'):
                        # Hashear contraseña
                        nueva_hash = hash_password(usuario['password'])
                        
                        # Actualizar en BD
                        await cursor.execute(
                            "UPDATE usuarios SET password = %s WHERE id = %s",
                            (nueva_hash, usuario['id'])
                        )
                        
                        migradas += 1
                        print(f"✅ Migrado: {usuario['correo']}")
                
                # 4. Commit de cambios
                await conn.commit()
                
                print(f"\n🎉 Migración completada:")
                print(f"   - {migradas} contraseñas hasheadas")
                print(f"   - {ya_hasheadas} ya estaban hasheadas")
                print(f"   - {len(usuarios)} usuarios totales\n")
                
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        raise
    finally:
        await close_db_pool()

if __name__ == "__main__":
    asyncio.run(migrate_passwords())
```

**Ejecutar:**
```bash
# 1. Hacer backup primero
mysqldump -u root -p control-asistencia > backup_antes_migracion.sql

# 2. Ejecutar migración
python Server/scripts/migrate_passwords.py

# 3. Verificar que funciona el login
```

---

## 2. Sistema JWT Unificado

### Opción Recomendada: HS256 Simplificado

**Archivo:** `Server/security/jwt_unified.py`

```python
"""
Sistema JWT unificado usando HS256.

Reemplaza a:
- services/auth_service.py (create_access_token, decode_access_token)
- security/jwt.py (issue_token, verify_token)
"""

from datetime import datetime, timedelta, timezone
from typing import Literal
from jose import jwt, JWTError
from fastapi import HTTPException, status
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
import logging

logger = logging.getLogger(__name__)

# Tipos de roles válidos
RolType = Literal["device", "admin", "teacher", "conserje"]

def create_token(
    subject: str,
    rol: RolType,
    exp_minutes: int = None
) -> str:
    """
    Crea un token JWT firmado con HS256.
    
    Args:
        subject: Identificador único (user_id, device_id, email)
        rol: Rol del usuario (device, admin, teacher, conserje)
        exp_minutes: Minutos hasta expiración (default: config)
        
    Returns:
        str: Token JWT firmado
        
    Example:
        >>> token = create_token("user@example.com", "admin")
        >>> token = create_token("ESP32_001", "device", exp_minutes=60)
    """
    if exp_minutes is None:
        exp_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,           # Subject (identificador único)
        "rol": rol,               # Rol del usuario
        "iat": int(now.timestamp()),                    # Issued at
        "exp": int((now + timedelta(minutes=exp_minutes)).timestamp()),  # Expiration
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"🎟️ Token creado para {subject} (rol: {rol}, exp: {exp_minutes}min)")
    
    return token

def verify_token(
    token: str,
    required_rol: RolType = None
) -> dict:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        required_rol: Rol requerido (opcional). Si se especifica, valida que coincida.
        
    Returns:
        dict: Payload decodificado con keys: sub, rol, iat, exp
        
    Raises:
        HTTPException: 401 si el token es inválido
        HTTPException: 403 si el rol no coincide
        
    Example:
        >>> payload = verify_token(token)
        >>> payload = verify_token(token, required_rol="admin")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validar rol si se especifica
        if required_rol:
            token_rol = payload.get("rol")
            if token_rol != required_rol:
                logger.warning(f"⛔ Rol incorrecto: esperado {required_rol}, recibido {token_rol}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado: se requiere rol '{required_rol}'"
                )
        
        logger.debug(f"✅ Token válido para {payload.get('sub')} (rol: {payload.get('rol')})")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("⏰ Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"❌ Token inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_token_subject(token: str) -> str:
    """
    Obtiene el subject del token sin validar rol.
    
    Args:
        token: Token JWT
        
    Returns:
        str: Subject (user_id, device_id, etc)
    """
    payload = verify_token(token)
    return payload.get("sub")

def get_token_rol(token: str) -> str:
    """
    Obtiene el rol del token.
    
    Args:
        token: Token JWT
        
    Returns:
        str: Rol (device, admin, etc)
    """
    payload = verify_token(token)
    return payload.get("rol")
```

### Actualizar Archivos Existentes

**1. Deprecar `security/jwt.py`**

Añadir al inicio del archivo:
```python
"""
⚠️  DEPRECATED: Usar security/jwt_unified.py en su lugar
Este archivo se mantiene como referencia temporal
"""
import warnings
warnings.warn(
    "security/jwt.py está deprecado. Usar security/jwt_unified.py",
    DeprecationWarning,
    stacklevel=2
)
```

**2. Actualizar `services/auth_service.py`**

```python
# Cambiar imports
from security.jwt_unified import create_token, verify_token, get_token_subject

# Actualizar funciones
def create_access_token(data: dict) -> str:
    """WRAPPER para compatibilidad - Usar create_token directamente"""
    return create_token(
        subject=data.get("sub") or data.get("id"),
        rol=data.get("rol"),
        exp_minutes=data.get("exp_minutes")
    )

def decode_access_token(token: str) -> TokenData:
    """WRAPPER para compatibilidad - Usar verify_token directamente"""
    payload = verify_token(token)
    return TokenData(id=payload["sub"], rol=payload["rol"])
```

**3. Actualizar `routers/auth.py`**

```python
from security.jwt_unified import create_token

@router.post("/auth/device", response_model=TokenResponse)
async def authenticate_device(auth_request: DeviceAuthRequest):
    """Autenticar dispositivo ESP32"""
    # ... verificaciones existentes ...
    
    # ✅ SIMPLIFICADO
    token = create_token(
        subject=auth_request.device_id,
        rol="device",
        exp_minutes=1440 # 24 horas
    )
    
    return TokenResponse(access_token=token, token_type="bearer")
```

**4. Actualizar `routers/websockets.py`**

```python
from security.jwt_unified import verify_token

async def _obtener_identidad_dispositivo(websocket: WebSocket, token: str) -> str:
    """Valida el token y retorna el device_id"""
    try:
        payload = verify_token(token, required_rol="device")
        return payload["sub"]
    except HTTPException as e:
        logger.error(f"❌ Token inválido: {e.detail}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None
```

---

## 3. Rate Limiting

### Paso 1: Instalar

```bash
pip install slowapi
```

### Paso 2: Configurar en Main App

**Archivo:** `Server/appFastApi.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Después de crear app
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
```

### Paso 3: Aplicar en Endpoints Críticos

**Archivo:** `Server/routers/auth.py`

```python
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # Máximo 5 intentos por minuto por IP
async def login(request: Request, correo: str = Form(...), password: str = Form(...)):
    """Login con rate limiting"""
    # ... código existente ...

@router.post("/auth/device")
@limiter.limit("10/minute")  # Dispositivos pueden intentar más veces
async def authenticate_device(request: Request, auth_request: DeviceAuthRequest):
    """Autenticación de dispositivo con rate limiting"""
    # ... código existente ...
```

---

## 4. Middleware de Errores

**Archivo:** `Server/middleware/error_handler.py`

```python
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Maneja HTTPException de forma consistente"""
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail} - "
        f"{request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación Pydantic"""
    logger.warning(f"Validación fallida: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Error de validación",
            "errors": exc.errors()
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Captura errores no controlados"""
    logger.error(
        f"Error no controlado en {request.method} {request.url.path}",
        exc_info=exc
    )
    
    # NO exponer detalles en producción
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"}
    )

def setup_error_handlers(app):
    """Configura todos los handlers de error"""
    from fastapi.exceptions import HTTPException
    
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
```

**En `appFastApi.py`:**

```python
from middleware.error_handler import setup_error_handlers

# Después de crear app
setup_error_handlers(app)
```

---

## 5. Validación de Inputs

### Actualizar Models

**Archivo:** `Server/models/user.py`

```python
from pydantic import BaseModel, EmailStr, constr, validator, Field
from typing import Optional

class UserLogin(BaseModel):
    correo: EmailStr  # ← Valida formato email
    contraseña: constr(min_length=8, max_length=100)  # ← Longitud
    
    @validator('correo')
    def email_lowercase(cls, v):
        """Normalizar email a minúsculas"""
        return v.lower().strip()
    
    @validator('contraseña')
    def password_not_common(cls, v):
        """Verificar que no sea una contraseña común"""
        common = ['12345678', 'password', 'qwerty', 'admin123']
        if v.lower() in common:
            raise ValueError('Contraseña demasiado común')
        return v

class DeviceAuthRequest(BaseModel):
    device_id: constr(min_length=3, max_length=50, strip_whitespace=True)
    api_key: constr(min_length=16, max_length=100)
    
    @validator('device_id')
    def device_id_format(cls, v):
        """Validar formato de device_id"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('device_id debe ser alfanumérico')
        return v

class RegistroAsistencia(BaseModel):
    uid: constr(min_length=10, max_length=20, strip_whitespace=True)
    aula: constr(min_length=3, max_length=50, strip_whitespace=True)
    
    @validator('uid')
    def uid_format(cls, v):
        """Validar formato UID hexadecimal"""
        try:
            int(v, 16)  # Verificar que es hexadecimal
        except ValueError:
            raise ValueError('UID debe ser hexadecimal')
        return v.upper()  # Normalizar a mayúsculas
```

---

## 6. CORS Seguro

**Archivo:** `Server/middleware/cors.py`

```python
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

logger = logging.getLogger(__name__)

def setup_cors(app):
    """
    Configura CORS de forma segura.
    En producción, CORS_ORIGINS debe ser una lista específica de dominios.
    """
    cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    
    # Parsear lista de orígenes
    allowed_origins = [origin.strip() for origin in cors_origins_str.split(",")]
    
    # ⚠️ Advertir si se usa wildcard en producción
    if "*" in allowed_origins:
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            logger.error("⚠️  CORS_ORIGINS='*' en producción NO es seguro")
        else:
            logger.warning("⚠️  CORS abierto (*) - solo para desarrollo")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        max_age=3600,  # Cachear preflight por 1 hora
    )
    
    logger.info(f"✅ CORS configurado: {allowed_origins}")
```

**En `.env`:**

```bash
# Desarrollo
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Producción
CORS_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

---

## 7. Logs con Rotación

**Archivo:** `Server/appFastApi.py` (actualizar LOGGING_CONFIG)

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
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
            'encoding': 'utf-8',
        },
        'error_file': {
            'formatter': 'detailed',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'error.log'),
            'maxBytes': 10_485_760,
            'backupCount': 5,
            'encoding': 'utf-8',
            'level': 'ERROR',
        },
    },
    'root': {
        'level': os.getenv('LOG_LEVEL', 'INFO'),
        'handlers': ['console', 'file', 'error_file'],
    },
}
```

---

## 8. WebSocket Heartbeat

**Archivo:** `Server/routers/websockets.py`

```python
import asyncio
from datetime import datetime

async def websocket_heartbeat(websocket: WebSocket, client_id: str):
    """
    Envía pings cada 30 segundos para mantener conexión viva.
    Si el cliente no responde, la conexión se cerrará automáticamente.
    """
    try:
        while True:
            await asyncio.sleep(30)
            try:
                await websocket.send_json({
                    "tipo": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                })
                logging.debug(f"❤️ Ping enviado a {client_id}")
            except Exception as e:
                logging.info(f"💔 Cliente {client_id} desconectado (ping falló)")
                break
    except asyncio.CancelledError:
        logging.debug(f"❤️ Heartbeat cancelado para {client_id}")

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    device_id = await _obtener_identidad_dispositivo(websocket, token)
    if not device_id:
        return
    
    await websocket.accept()
    
    # Iniciar heartbeat en background
    heartbeat_task = asyncio.create_task(websocket_heartbeat(websocket, device_id))
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            # Responder a pongs del cliente
            if data.get("tipo") == "pong":
                logging.debug(f"💚 Pong recibido de {device_id}")
                continue
            
            # ... resto del código ...
            
    except WebSocketDisconnect:
        logging.info(f"🔌 WebSocket desconectado: {device_id}")
    finally:
        heartbeat_task.cancel()
        await manager.disconnect(device_id)
```

---

## 📋 Checklist de Implementación

### Semana 1: Seguridad Crítica

- [ ] Instalar `passlib[bcrypt]`
- [ ] Crear `security/password.py`
- [ ] Actualizar `services/auth_service.py`
- [ ] Ejecutar `scripts/migrate_passwords.py`
- [ ] Probar login con contraseñas hasheadas
- [ ] Actualizar `requirements.txt`

### Semana 2: JWT y Rate Limiting

- [ ] Crear `security/jwt_unified.py`
- [ ] Deprecar `security/jwt.py`
- [ ] Actualizar todos los routers
- [ ] Instalar `slowapi`
- [ ] Configurar rate limiting en `/login` y `/auth/device`
- [ ] Probar límites con herramientas como `ab` o `locust`

### Semana 3: Error Handling y Validación

- [ ] Crear `middleware/error_handler.py`
- [ ] Registrar handlers en `appFastApi.py`
- [ ] Actualizar modelos Pydantic con validaciones
- [ ] Instalar `email-validator`
- [ ] Probar errores retornados (no deben exponer stack traces)

### Semana 4: Mejoras Adicionales

- [ ] Actualizar CORS en `middleware/cors.py`
- [ ] Configurar logs con rotación
- [ ] Implementar WebSocket heartbeat
- [ ] Documentar todos los cambios
- [ ] Code review final

---

## 🧪 Testing

### Test de Hash de Contraseñas

```python
# tests/test_password.py
from security.password import hash_password, verify_password

def test_password_hashing():
    password = "MiContraseña123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert hashed.startswith("$2b$")
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)
```

### Test de Rate Limiting

```bash
# Usar Apache Bench para probar
ab -n 20 -c 5 -p login.json -T application/json http://localhost:8000/login

# Debería fallar después de 5 requests en 1 minuto
```

---

## 📚 Recursos

- **Passlib Docs:** https://passlib.readthedocs.io/
- **SlowAPI Docs:** https://slowapi.readthedocs.io/
- **Pydantic Validation:** https://docs.pydantic.dev/latest/concepts/validators/

---

**¿Dudas sobre la implementación?** Consultar el code review completo en `CODIGO_REVIEW.md`.
