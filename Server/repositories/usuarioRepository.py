from utils.database_pool import get_db_pool
import aiomysql

async def get_usuario_por_mail(correo: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT id,nombre, correo, password, rol FROM usuarios WHERE correo = %s", 
                (correo,)
            )
            return await cursor.fetchone()