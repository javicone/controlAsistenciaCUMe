from datetime import datetime
from fastapi import HTTPException
from repositories.asistenciaRepository import (
    get_usuario_id_by_uid,
    get_aula_id_by_nombre,
    insert_asistencia,
    fetch_asistencias_by_usuario,
    fetch_all_asistencias,
)

async def registrar_asistencia(uid: str, nombre_aula: str) -> dict:
    usuario_id = await get_usuario_id_by_uid(uid)
    if not usuario_id:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    aula_id = await get_aula_id_by_nombre(nombre_aula)
    if not aula_id:
        raise HTTPException(status_code=404, detail="Aula no encontrada")

    fecha_hora = datetime.now()
    await insert_asistencia(usuario_id, aula_id, fecha_hora)
    
    return {
        "mensaje": "Asistencia registrada",
        "usuario_id": usuario_id,
        "aula_id": aula_id,
        "fecha_hora": fecha_hora
    }

async def obtener_asistencias(user_id: str, rol: str) -> list:
    if rol == "profesor":
        return await fetch_asistencias_by_usuario(user_id)
    elif rol in ["conserje", "administrador"]:
        return await fetch_all_asistencias()
    else:
        raise HTTPException(status_code=403, detail="Acceso denegado")