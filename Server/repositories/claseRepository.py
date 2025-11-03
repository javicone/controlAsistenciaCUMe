from utils.database_pool import get_db_pool
import aiomysql

async def get_clase_actual(aula: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query_actual = """
            SELECT c.asignatura, c.hora_inicio, c.hora_fin 
            FROM clases c 
            JOIN aulas a ON c.aula_id = a.id 
            WHERE a.nombre = %s 
                AND CURTIME() BETWEEN c.hora_inicio AND c.hora_fin
                AND CURDATE() = DATE(c.fecha)
            ORDER BY c.hora_inicio ASC 
            LIMIT 1
            """
            await cursor.execute(query_actual, (aula,))
            return await cursor.fetchone()

async def get_clase_proxima_hoy(aula: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query_proxima = """
            SELECT c.asignatura, c.hora_inicio, c.hora_fin 
            FROM clases c 
            JOIN aulas a ON c.aula_id = a.id 
            WHERE a.nombre = %s 
                AND c.hora_inicio > CURTIME()
                AND CURDATE() = DATE(c.fecha)
            ORDER BY c.hora_inicio ASC 
            LIMIT 1
            """
            await cursor.execute(query_proxima, (aula,))
            return await cursor.fetchone()

async def get_clase_siguiente(aula: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query_siguiente = """
            SELECT c.asignatura, c.hora_inicio, c.hora_fin, c.fecha
            FROM clases c 
            JOIN aulas a ON c.aula_id = a.id 
            WHERE a.nombre = %s 
                AND c.fecha > CURDATE()
            ORDER BY c.fecha ASC, c.hora_inicio ASC 
            LIMIT 1
            """
            await cursor.execute(query_siguiente, (aula,))
            return await cursor.fetchone()