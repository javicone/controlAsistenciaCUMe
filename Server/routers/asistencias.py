from fastapi import APIRouter, Depends
from models.asistencia import RegistroAsistencia
from models.user import TokenData
from services.asistencia_service import registrar_asistencia, obtener_asistencias
from routers.auth import get_current_user

router = APIRouter(prefix="/asistencias", tags=["Asistencias"])

@router.post("/registro")
async def registro_asistencia(registro: RegistroAsistencia):
    """Registra la asistencia de un profesor"""
    return await registrar_asistencia(registro.uid, registro.nombre_aula)

@router.get("")
async def listar_asistencias(current_user: TokenData = Depends(get_current_user)):
    """Obtiene las asistencias según el rol del usuario"""
    return await obtener_asistencias(current_user.id, current_user.rol)