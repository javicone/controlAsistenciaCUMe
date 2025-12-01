from datetime import datetime, timedelta
from flask import logging
from jose import JWTError, jwt
from fastapi import HTTPException, logger, status
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.user import TokenData, UserInDB
from utils.database_pool import get_db_pool
import aiomysql
from repositories.usuarioRepository import get_usuario_por_mail
    
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
        
        # ✅ FIX: Buscar en múltiples campos posibles
        user_id: str = payload.get("sub") or payload.get("id") or payload.get("device_id")
        rol: str = payload.get("rol")
        
        if user_id is None or rol is None:
            raise credentials_exception
            
        return TokenData(id=user_id, rol=rol)
        
    except JWTError:
        raise credentials_exception

async def authenticate_user(correo: str, password: str) -> UserInDB:
    """Autentica un usuario por correo y contraseña"""
    user = await get_usuario_por_mail(correo)
    if not user or user["password"] != password:  # TODO: usar passlib para hash
        raise HTTPException(
            status_code=401, 
            detail="Correo o contraseña incorrectos"
        )
    
    return UserInDB(**user)