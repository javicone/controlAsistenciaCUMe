from datetime import datetime
from utils.database_pool import get_db_pool
import aiomysql
from typing import Optional, Dict

async def get_usuario_id_by_uid(uid: str) -> int | None:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id FROM usuarios WHERE uid_tarjeta = %s", 
                (uid,)
            )
            usuario = await cursor.fetchone()
            return usuario["id"] if usuario else None

async def get_aula_id_by_device_id(device_id: str) -> int | None:
    """
    Obtiene el aula_id asociado a un device_id.
    Primero intenta buscar en aulas_estado (memoria), luego en BD.
    """
    from services.aula_service import aulas_estado
    
    # 1. Buscar en memoria (aulas_estado)
    if device_id in aulas_estado:
        nombre_aula = aulas_estado[device_id].get("aula") or aulas_estado[device_id].get("nombre")
        if nombre_aula:
            # Buscar aula_id por nombre
            return await get_aula_id_by_nombre(nombre_aula)
    
    # 2. Si no está en memoria, buscar directamente por device_id en BD
    # (En el futuro podrías tener una tabla devices con device_id → aula_id)
    return None

async def get_aula_id_by_nombre(nombre_aula: str) -> int | None:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id FROM aulas WHERE nombre = %s", 
                (nombre_aula,)
            )
            aula = await cursor.fetchone()
            return aula["id"] if aula else None

async def get_clase_actual_by_aula_and_time(aula_id: int, fecha_hora: datetime) -> Optional[Dict]:
    """Busca la clase que está en curso en un aula en un momento específico"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """
                SELECT id, profesor_id, asignatura, hora_inicio, hora_fin
                FROM clases
                WHERE aula_id = %s
                  AND %s BETWEEN hora_inicio AND hora_fin
                ORDER BY hora_inicio DESC
                LIMIT 1
                """,
                (aula_id, fecha_hora)
            )
            return await cursor.fetchone()

async def insert_asistencia(usuario_id: int, aula_id: int, fecha_hora: datetime, clase_id: Optional[int] = None) -> None:
    """Inserta asistencia. clase_id se guarda solo si la tabla lo soporta"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Por ahora solo guardamos usuario_id, aula_id, fecha_hora
            # Si en el futuro se agrega clase_id a la tabla, descomentar la versión extendida
            await cursor.execute(
                "INSERT INTO asistencias (usuario_id, aula_id, fecha_hora) VALUES (%s, %s, %s)",
                (usuario_id, aula_id, fecha_hora)
            )
            # Versión futura con clase_id:
            # await cursor.execute(
            #     "INSERT INTO asistencias (usuario_id, aula_id, fecha_hora, clase_id) VALUES (%s, %s, %s, %s)",
            #     (usuario_id, aula_id, fecha_hora, clase_id)
            # )

async def fetch_asistencias_by_usuario(user_id: str) -> list:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM asistencias WHERE usuario_id = %s", 
                (user_id,)
            )
            return await cursor.fetchall()

async def fetch_all_asistencias() -> list:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM asistencias")
            return await cursor.fetchall()