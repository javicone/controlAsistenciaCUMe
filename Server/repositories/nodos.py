import aiomysql
from typing import Optional, Dict
from venv import logger


async def fetch_one(conn, query: str, params=()):
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchone()
    except Exception as e:
        logger.error(f"DB Error fetch_one: {e}")
        return None


async def execute_write(conn, query: str, params=()):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(query, params)
            await conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"DB Error write: {e}")
        await conn.rollback()
        return None


# --------------------------------------------------------
# LÓGICA DE NODOS (versión mínima)
# --------------------------------------------------------

async def verificar_nodo_existe(conn, device_id: str, api_key: str) -> bool:
    query = "SELECT id FROM nodos WHERE device_id = %s AND api_key = %s"
    return (await fetch_one(conn, query, (device_id, api_key))) is not None


async def obtener_nodo(conn, device_id: str) -> Optional[Dict]:
    query = "SELECT id, device_id, api_key FROM nodos WHERE device_id = %s"
    return await fetch_one(conn, query, (device_id,))


async def crear_nodo(conn, device_id: str, api_key: str) -> Optional[int]:
    query = "INSERT INTO nodos (device_id, api_key) VALUES (%s, %s)"
    return await execute_write(conn, query, (device_id, api_key))


async def actualizar_api_key(conn, device_id: str, nueva_key: str) -> bool:
    query = "UPDATE nodos SET api_key = %s WHERE device_id = %s"
    return execute_write(conn, query, (nueva_key, device_id)) is not None


async def eliminar_nodo(conn, device_id: str) -> bool:
    query = "DELETE FROM nodos WHERE device_id = %s"
    return execute_write(conn, query, (device_id,)) is not None
