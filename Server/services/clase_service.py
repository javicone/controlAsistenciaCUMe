from datetime import datetime, timedelta
from fastapi import HTTPException
from repositories.claseRepository import (
    get_clase_actual,
    get_clase_proxima_hoy,
    get_clase_siguiente,
    get_clase_from_webservice
)

async def obtener_clase_actual(aula: str) -> dict:
    clase_actual = await get_clase_actual(aula)
    if clase_actual:
        return {
            "aula": aula,
            "asignatura": clase_actual["asignatura"],
            "hora_inicio": clase_actual["hora_inicio"].strftime("%H:%M:%S"),
            "hora_fin": clase_actual["hora_fin"].strftime("%H:%M:%S"),
            "estado": "en_curso"
        }
    
    clase_proxima = await get_clase_proxima_hoy(aula)
    if clase_proxima:
        return {
            "aula": aula,
            "asignatura": clase_proxima["asignatura"],
            "hora_inicio": clase_proxima["hora_inicio"].strftime("%H:%M:%S"),
            "hora_fin": clase_proxima["hora_fin"].strftime("%H:%M:%S"),
            "estado": "proxima"
        }
    
    clase_siguiente = await get_clase_siguiente(aula)
    if clase_siguiente:
        return {
            "aula": aula,
            "asignatura": clase_siguiente["asignatura"],
            "hora_inicio": clase_siguiente["hora_inicio"].strftime("%H:%M:%S"),
            "hora_fin": clase_siguiente["hora_fin"].strftime("%H:%M:%S"),
            "fecha": clase_siguiente["fecha"].strftime("%Y-%m-%d"),
            "estado": "proxima_fecha"
        }
    
    raise HTTPException(
        status_code=404, 
        detail=f"No se encontraron clases para el aula {aula}"
    )

async def obtener_clase_test(aula: str) -> dict:
    clase_siguiente = await get_clase_from_webservice(aula)
    
    # Si el webservice devuelve un mensaje (no hay clases), devolverlo
    if "mensaje" in clase_siguiente:
        return {
            "mensaje": clase_siguiente["mensaje"]
        }
    
    # Si hay datos de clase, formatearlos
    return {
        "asignatura": clase_siguiente["asignatura"],
        "hora_inicio": clase_siguiente["hora_inicio"].strftime("%H:%M:%S"),
        "hora_fin": clase_siguiente["hora_fin"].strftime("%H:%M:%S"),
    }