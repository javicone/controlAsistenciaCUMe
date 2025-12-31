from datetime import datetime
from fastapi import HTTPException
import logging
from repositories.asistenciaRepository import (
    get_usuario_id_by_uid,
    get_aula_id_by_device_id,
    get_clase_actual_by_aula_and_time,
    insert_asistencia,
    fetch_asistencias_by_usuario,
    fetch_all_asistencias,
)
from repositories.claseRepository import get_clase_from_webservice

logger = logging.getLogger(__name__)

async def registrar_asistencia(uid: str, device_id: str, timestamp: datetime = None) -> dict:
    """Registra asistencia vinculando profesor, aula y clase actual"""
    
    # 1. Validar que el profesor existe
    usuario_id = await get_usuario_id_by_uid(uid)
    if not usuario_id:
        logger.error(f"❌ Profesor no encontrado para UID: {uid}")
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    # 2. Obtener aula desde device_id y nombre del aula
    aula_id = await get_aula_id_by_device_id(device_id)
    if not aula_id:
        logger.error(f"❌ Aula no encontrada para device_id: {device_id}")
        raise HTTPException(status_code=404, detail=f"Aula no configurada para dispositivo {device_id}")
    
    # Obtener nombre del aula desde aulas_estado para consultar webservice
    from services.aula_service import aulas_estado
    nombre_aula = None
    if device_id in aulas_estado:
        nombre_aula = aulas_estado[device_id].get("aula") or aulas_estado[device_id].get("nombre")
    
    # 3. Usar timestamp del dispositivo o del servidor
    fecha_hora = timestamp if timestamp else datetime.now()
    
    # 4. Intentar obtener clase actual desde BD primero
    clase = await get_clase_actual_by_aula_and_time(aula_id, fecha_hora)
    
    # 5. Si no hay clase en BD, consultar webservice
    if not clase and nombre_aula:
        logger.info(f"🌐 No hay clase en BD, consultando webservice para {nombre_aula}")
        clase_ws = await get_clase_from_webservice(nombre_aula)
        
        if clase_ws and "asignatura" in clase_ws:
            # Convertir respuesta del webservice a formato esperado
            clase = {
                "id": None,  # No tenemos ID de la BD
                "profesor_id": usuario_id,  # Asumimos que es el profesor correcto
                "asignatura": clase_ws["asignatura"],
                "hora_inicio": clase_ws.get("hora_inicio"),
                "hora_fin": clase_ws.get("hora_fin")
            }
            logger.info(f"✅ Clase obtenida desde webservice: {clase['asignatura']}")
    
    clase_id = None
    asignatura = None
    
    if clase:
        # 6. Validar que el profesor del fichaje coincida con el profesor de la clase
        # Solo validar si tenemos profesor_id de la BD
        if clase.get("profesor_id") and clase["profesor_id"] != usuario_id:
            logger.warning(
                f"⚠️ El profesor {usuario_id} (UID: {uid}) intentó fichar en clase de profesor {clase['profesor_id']}"
            )
            raise HTTPException(
                status_code=403, 
                detail=f"No puedes fichar en esta clase. La clase de {clase['asignatura']} está asignada a otro profesor"
            )
        
        clase_id = clase.get("id")
        asignatura = clase["asignatura"]
        logger.info(
            f"✅ Fichaje válido: Profesor {usuario_id} en clase ({asignatura}) "
            f"de {clase.get('hora_inicio')} a {clase.get('hora_fin')}"
        )
    else:
        logger.error(
            f"❌ No hay clase programada en aula '{nombre_aula}' para {fecha_hora}. "
            f"Fichaje rechazado."
        )
        raise HTTPException(
            status_code=400, 
            detail=f"No hay clase programada en '{nombre_aula}' en este momento. No se puede fichar."
        )
    
    # 7. Guardar asistencia
    await insert_asistencia(usuario_id, aula_id, fecha_hora, clase_id)
    
    return {
        "mensaje": "Asistencia registrada",
        "usuario_id": usuario_id,
        "aula_id": aula_id,
        "clase_id": clase_id,
        "asignatura": asignatura,
        "fecha_hora": fecha_hora
    }

async def obtener_asistencias(user_id: str, rol: str) -> list:
    if rol == "profesor":
        return await fetch_asistencias_by_usuario(user_id)
    elif rol in ["conserje", "administrador"]:
        return await fetch_all_asistencias()
    else:
        raise HTTPException(status_code=403, detail="Acceso denegado")