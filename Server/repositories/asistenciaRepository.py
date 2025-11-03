from datetime import datetime
from utils.database_pool import get_db_pool
import aiomysql

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

async def insert_asistencia(usuario_id: int, aula_id: int, fecha_hora: datetime) -> None:
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "INSERT INTO asistencias (usuario_id, aula_id, fecha_hora) VALUES (%s, %s, %s)",
                (usuario_id, aula_id, fecha_hora)
            )

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