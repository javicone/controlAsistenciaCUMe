from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from Server.models.webTokens import DeviceAuthRequest, TokenResponse
from Server.repositories.nodos import get_device
from Server.security.jwt import DevicePrincipal, issue_token
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

@router.post("/device", response_model=TokenResponse)
def auth_device(body: DeviceAuthRequest):
    rec = get_device(body.device_id)
    if not rec or rec["api_key"] != body.api_key:
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = issue_token(sub=body.device_id, scope="device", exp_seconds=3600)
    return TokenResponse(access_token=token)

# Ejemplo de endpoint protegido para dispositivos
@router.get("/device/ping")
def device_ping(device_id: str = DevicePrincipal):
    return {"ok": True, "device_id": device_id}