from fastapi import APIRouter, Depends
from models.asistencia import RegistroAsistencia
from models.user import TokenData
from services.asistencia_service import registrar_asistencia, obtener_asistencias

router = APIRouter(prefix="/asistencias", tags=["Asistencias"])

@router.post("/registro")
async def registro_asistencia(registro: RegistroAsistencia):
    """Registra la asistencia de un profesor"""
    return await registrar_asistencia(registro.uid, registro.nombre_aula)

