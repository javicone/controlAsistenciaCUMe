from datetime import datetime
from fastapi import HTTPException
from utils.database_pool import get_db_pool
import aiomysql

async def registrar_asistencia(uid: str, nombre_aula: str) -> dict:
    """Registra la asistencia de un profesor en un aula"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Obtener usuario_id
            await cursor.execute(
                "SELECT id FROM usuarios WHERE uid_tarjeta = %s", 
                (uid,)
            )
            usuario = await cursor.fetchone()
            if not usuario:
                raise HTTPException(status_code=404, detail="Profesor no encontrado")
            
            # Obtener aula_id
            await cursor.execute(
                "SELECT id FROM aulas WHERE nombre = %s", 
                (nombre_aula,)
            )
            aula = await cursor.fetchone()
            if not aula:
                raise HTTPException(status_code=404, detail="Aula no encontrada")

            # Insertar asistencia
            fecha_hora = datetime.now()
            await cursor.execute(
                "INSERT INTO asistencias (usuario_id, aula_id, fecha_hora) VALUES (%s, %s, %s)",
                (usuario["id"], aula["id"], fecha_hora)
            )
    
    return {
        "mensaje": "Asistencia registrada",
        "usuario_id": usuario["id"],
        "aula_id": aula["id"],
        "fecha_hora": fecha_hora
    }

async def obtener_asistencias(user_id: str, rol: str) -> list:
    """Obtiene las asistencias según el rol del usuario"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            if rol == "profesor":
                await cursor.execute(
                    "SELECT * FROM asistencias WHERE usuario_id = %s", 
                    (user_id,)
                )
            elif rol in ["conserje", "administrador"]:
                await cursor.execute("SELECT * FROM asistencias")
            else:
                raise HTTPException(status_code=403, detail="Acceso denegado")
            
            asistencias = await cursor.fetchall()
    
    return asistencias