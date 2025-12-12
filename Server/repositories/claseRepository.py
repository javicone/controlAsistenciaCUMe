from utils.database_pool import get_db_pool
import aiomysql
import aiohttp
import asyncio
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

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
        

async def get_clase_from_webservice(aula: str) -> Optional[Dict]:
    """
    Obtiene la información de la clase actual desde el webservice de reserva de instalaciones.
    
    Args:
        aula: Nombre del aula (ej: "Aula 1")
    
    Returns:
        Dict con {asignatura, hora_inicio, hora_fin} o None si hay error
    """
    url = "https://docencia-cum.unex.es/ReservaInstalaciones_ant/ws.php"
    
    try:
        logger.info(f"🌐 Consultando webservice para aula: {aula}")
        
        async with aiohttp.ClientSession() as session:
            # Realizar petición GET con el parámetro aula
            async with session.get(url, params={"aula": aula}, timeout=aiohttp.ClientTimeout(total=10)) as response:
                
                # Verificar código de respuesta HTTP
                if response.status != 200:
                    logger.error(f"❌ Error HTTP {response.status} al consultar webservice")
                    return None
                
                # Intentar parsear como JSON
                try:
                    data = await response.json()
                    
                    # Verificar que tenga los campos esperados
                    if "asignatura" in data and "hora_inicio" in data and "hora_fin" in data:
                        logger.info(f"✅ Datos obtenidos del webservice: {data['asignatura']}")
                        return {
                            "asignatura": data["asignatura"],
                            "hora_inicio": data["hora_inicio"],
                            "hora_fin": data["hora_fin"]
                        }
                    # Si no hay campos de clase pero hay mensaje, devolver el mensaje
                    elif "mensaje" in data:
                        logger.info(f"ℹ️ Mensaje del webservice: {data['mensaje']}")
                        return {
                            "mensaje": data["mensaje"]
                        }
                    else:
                        logger.warning(f"⚠️ Respuesta JSON sin campos esperados: {data}")
                        return None
                        
                except aiohttp.ContentTypeError:
                    # Si no es JSON, intentar leer como texto (podría ser un mensaje de error)
                    text = await response.text()
                    logger.warning(f"⚠️ Respuesta no es JSON válido: {text}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"❌ Error de conexión al webservice: {e}")
        return None
    except asyncio.TimeoutError:
        logger.error(f"❌ Timeout al consultar webservice (>10s)")
        return None
    except Exception as e:
        logger.error(f"❌ Error inesperado al consultar webservice: {e}")
        return None


async def get_clase_actual_integrada(aula: str) -> Optional[Dict]:
    """
    Obtiene la clase actual priorizando el webservice externo,
    y usa la BD local como fallback.
    
    Args:
        aula: Nombre del aula
    
    Returns:
        Dict con información de la clase o None
    """
    # 1. Intentar primero con el webservice externo
    clase_ws = await get_clase_from_webservice(aula)
    
    if clase_ws:
        logger.info(f"✅ Usando datos del webservice para {aula}")
        return clase_ws
    
    # 2. Fallback a base de datos local
    logger.info(f"⚠️ Webservice no disponible, consultando BD local para {aula}")
    clase_bd = await get_clase_actual(aula)
    
    if clase_bd:
        logger.info(f"✅ Usando datos de BD local para {aula}")
        return clase_bd
    
    logger.warning(f"❌ No se encontró clase actual para {aula} en webservice ni BD")
    return None