from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user import UserLogin
from security.jwt import verify_token
from models.webTokens import DeviceAuthRequest, TokenResponse
from repositories.nodos import verificar_nodo_existe 
from services.auth_service import authenticate_user 
from services.auth_service import create_access_token
from utils.database_pool import get_db_pool
import logging
from repositories.usuarioRepository import get_usuario_por_mail

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
        # ✅ AÑADIR: Log de la petición recibida
        logger.info(f"   Device ID: {auth_request.device_id}")
        logger.info(f"   API Key: {auth_request.api_key[:10]}...") # Solo primeros 10 chars
        
        # Verificar que el nodo existe en la base de datos
        conn = await get_db_pool()
        try:
            existe = await verificar_nodo_existe(conn, auth_request.device_id, auth_request.api_key)
            # si no existe se le crea el JWT
            if not existe:
                logger.warning(f"❌ Credenciales inválidas para {auth_request.device_id}")
                raise HTTPException(
                    status_code=401,
                    detail="Credenciales de dispositivo inválidas"
                )
            logger.info(f"✅ Nodo verificado: {auth_request.device_id}")
            
            # Crear token JWT
            token = create_access_token(auth_request.device_id)
            
            logger.info(f"🎟️ Token generado para {auth_request.device_id}")
            logger.info(f"   Longitud: {len(token)} caracteres")
            
            return TokenResponse(token=token)
            
        finally:
            conn.close()
            
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
async def login_usuario(credentials: UserLogin):
    """Login de usuarios web (admin/conserje)"""
    logger.info(f"🔐 Login solicitado para usuario: {credentials.correo}")
    
    try:
        # ✅ authenticate_user devuelve UserInDB (Pydantic model)
        user = await authenticate_user(credentials.correo, credentials.password)
        logger.info(f"✅ Usuario autenticado: {user.correo} (rol: {user.rol})")
        # Determinar scope según rol
        scope = "admin" if user.rol == "admin" else "conserje" if user.rol == "conserje" else "usuario"
        # Crear token JWT con claims adicionales
        token_data = {
            "sub": str(user.id),
            "scope": scope,
            "rol": user.rol,
            "correo": user.correo
        }
        token = create_access_token(token_data)
        logger.info(f"🎟️ Token generado para {user.correo} (scope: {scope})")
         # ✅ REDIRIGIR SEGÚN EL ROL
        if user.rol == "admin":
            redirect_url = "/admin"
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
            secure=True,    # Solo HTTPS (cambiar a False en desarrollo HTTP)
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