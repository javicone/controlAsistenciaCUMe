from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models.user import UserLogin, TokenData
from services.auth_service import authenticate_user, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login")
@router.post("/login", include_in_schema=False)
async def login(user_data: UserLogin):
    """Inicia sesión y devuelve un token JWT"""
    user = await authenticate_user(user_data.correo, user_data.password)
    access_token = create_access_token(data={"sub": str(user.id), "rol": user.rol})
    return {"token": access_token, "rol": user.rol}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Dependencia para obtener el usuario actual desde el token"""
    return decode_access_token(token)