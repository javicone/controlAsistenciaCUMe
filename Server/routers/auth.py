from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from config import ALGORITHM, SECRET_KEY
from security import jwt
from models.user import UserLogin
from security.jwt import verify_token
from models.webTokens import DeviceAuthRequest, TokenResponse
from repositories.nodos import verificar_nodo_existe 
from services.auth_service import authenticate_user 
from services.auth_service import create_access_token
from utils.database_pool import get_db_pool
import logging
from repositories.usuarioRepository import get_usuario_por_mail
from fastapi import APIRouter, Form, HTTPException, Depends, Request, status

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/auth/device", response_model=TokenResponse)
async def authenticate_device(auth_request: DeviceAuthRequest):
    """
    Autenticar dispositivo ESP32 y generar token JWT
    """
    logger.info(f"🔐 Autenticación solicitada para: {auth_request.device_id}")
    try:
        logger.info(f"   Device ID: {auth_request.device_id}")
        logger.info(f"   API Key: {auth_request.api_key[:10]}...") 
        
        # 1. Obtener el POOL (la caja de conexiones)
        pool = await get_db_pool()
        
        # 2. Adquirir una CONEXIÓN individual (sacar un cable de la caja)
        async with pool.acquire() as conn:
            # Pasamos la conexión real ('conn'), no el pool
            existe = await verificar_nodo_existe(conn, auth_request.device_id, auth_request.api_key)
            print(existe)
            print("api key: ")
            print(auth_request.api_key)

            if not existe:
                logger.warning(f"❌ Credenciales inválidas para {auth_request.device_id}")
                raise HTTPException(
                    status_code=401,
                    detail="Credenciales de dispositivo inválidas"
                )
            
            logger.info(f"✅ Nodo verificado: {auth_request.device_id}")
            
            # 3. Crear token JWT correctamente (como diccionario)
            # Añadimos 'rol': 'device' para que el WebSocket sepa qué es
            token_data = {
                "sub": auth_request.device_id,
                "rol": "device" 
                
            }
            token = create_access_token(token_data)
            
            logger.info(f"🎟️ Token generado para {auth_request.device_id}")
            
            return TokenResponse(access_token=token, token_type="bearer")
            
        # No hace falta finally: conn.close() porque el 'async with' 
        # devuelve la conexión al pool automáticamente.
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en autenticación: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")





# Endpoint de prueba sin autenticación
@router.get("/auth/test")
async def test_auth():
    """Endpoint de prueba para verificar que /auth funciona"""
    return {"status": "ok", "message": "Auth endpoint funcionando"}

@router.post("/auth/login")
async def login_usuario(correo:str= Form(...), password:str= Form(...)):
    """Login de usuarios web (admin/conserje)"""
    try:
        # ✅ authenticate_user devuelve UserInDB (Pydantic model)
        user = await authenticate_user(correo, password)
        logger.info(f"✅ Usuario autenticado: {user.correo} (rol: {user.rol})")
        # Determinar scope según rol
        # Crear token JWT con claims adicionales
        token_data = {
            "id": str(user.id),
            "rol": user.rol,
            "correo": user.correo,
            "nombre": user.nombre,
        }
        token = create_access_token(token_data)
        logger.info(f"🎟️ Token generado para {user.correo} (rol: {user.rol})")
         # ✅ REDIRIGIR SEGÚN EL ROL
        if user.rol == "administrador":
            redirect_url = "/adminPanel"
        elif user.rol == "profesor":
            redirect_url = "/profesor/asistencias"
        elif user.rol == "conserje":
            redirect_url = "/conserje"
        else:
            redirect_url = "/dashboard"
        logger.info(f"🔀 Redirigiendo a: {redirect_url}")
        # ✅ Crear respuesta de redirección con el token en cookie/header
        response = RedirectResponse(url=redirect_url, status_code=303)
        # Guardar token en cookie HttpOnly (más seguro)
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,  # No accesible desde JavaScript
            secure=False,    # Solo HTTPS (cambiar a False en desarrollo HTTP)
            samesite="lax",
            max_age=86400   # 24 horas
        )
        
        return response            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )
    
async def verificar_token_web(request: Request, rol_requerido: str = None):
    """
    Verifica el token almacenado en la cookie 'access_token'.
    Valida la firma, la expiración y opcionalmente el rol.
    """
    # 1. Obtener el token de la cookie
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró la sesión (Cookie faltante)"
        )

    try:
        # 2. Decodificar el token
        # Esto valida automáticamente la firma y la fecha de expiración (exp)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_rol = payload.get("rol")
        user_email = payload.get("correo")
        
        if user_rol is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta información de rol"
            )

        # 3. Verificar el Rol (si se requiere uno específico)
        if rol_requerido:
            # Si el rol requerido es 'admin', solo entra admin.
            # Si es 'conserje', podría entrar conserje (y quizás admin si quisieras jerarquía)
            if user_rol != rol_requerido:
                logger.warning(f"⛔ Acceso denegado para {user_email}. Rol actual: {user_rol}, Requerido: {rol_requerido}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No tienes permisos suficientes. Se requiere rol: {rol_requerido}"
                )

        logger.info(f"✅ Token válido para usuario web: {user_email} ({user_rol})")
        return payload

    except JWTError as e:
        logger.error(f"❌ Error decodificando token web: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada"
        )
    

@router.get("/logout")
async def logout(request: Request):
    logger.info(f"🔐 Logout solicitado: {request.client.host}")
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token", path="/")
    return response