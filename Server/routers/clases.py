from fastapi import APIRouter
from services.clase_service import obtener_clase_actual, obtener_clase_test

router = APIRouter(prefix="/clases", tags=["Clases"])

@router.get("/proxima")
async def proxima_clase(aula: str):
    """Obtiene la clase actual o próxima de un aula"""
    return await obtener_clase_actual(aula)

@router.get("/test")
async def clase_test(aula: str):
    """Endpoint de prueba con datos simulados"""
    return await obtener_clase_test(aula)