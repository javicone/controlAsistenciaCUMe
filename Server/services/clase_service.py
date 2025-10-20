from datetime import datetime, timedelta
from fastapi import HTTPException
from utils.database_pool import get_db_pool
import aiomysql

async def obtener_clase_actual(aula: str) -> dict:
    """Obtiene la clase actual o próxima de un aula"""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            # Buscar clase actual
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
            clase_actual = await cursor.fetchone()
            
            if clase_actual:
                return {
                    "aula": aula,
                    "asignatura": clase_actual["asignatura"],
                    "hora_inicio": clase_actual["hora_inicio"].strftime("%H:%M:%S"),
                    "hora_fin": clase_actual["hora_fin"].strftime("%H:%M:%S"),
                    "estado": "en_curso"
                }
            
            # Buscar próxima clase hoy
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
            clase_proxima = await cursor.fetchone()
            
            if clase_proxima:
                return {
                    "aula": aula,
                    "asignatura": clase_proxima["asignatura"],
                    "hora_inicio": clase_proxima["hora_inicio"].strftime("%H:%M:%S"),
                    "hora_fin": clase_proxima["hora_fin"].strftime("%H:%M:%S"),
                    "estado": "proxima"
                }
            
            # Buscar próxima clase en días siguientes
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
            clase_siguiente = await cursor.fetchone()
            
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
    """Endpoint de prueba con datos simulados"""
    ahora = datetime.now()
    hora_inicio = ahora + timedelta(hours=1)
    hora_fin = hora_inicio + timedelta(hours=1, minutes=30)
    
    return {
        "asignatura": "Fundamentos de Programación",
        "hora_inicio": hora_inicio.strftime("%H:%M:%S"),
        "hora_fin": hora_fin.strftime("%H:%M:%S"),
    }