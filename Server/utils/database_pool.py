import aiomysql
from database import DB_CONFIG
import logging

_pool = None

async def get_db_pool():
    """
    Obtiene o crea el pool de conexiones a la base de datos
    """
    global _pool
    
    if _pool is None:
        cfg = dict(DB_CONFIG) if isinstance(DB_CONFIG, dict) else dict(vars(DB_CONFIG))
        
        # Mapear claves incompatibles
        if "database" in cfg and "db" not in cfg:
            cfg["db"] = cfg.pop("database")
        
        try:
            _pool = await aiomysql.create_pool(**cfg, autocommit=True)
            logging.info("✅ Pool de base de datos creado")
        except TypeError as e:
            raise RuntimeError(f"Error creando pool aiomysql: {list(cfg.keys())} — {e}")
    
    return _pool

async def close_db_pool():
    """
    Cierra el pool de conexiones
    """
    global _pool
    if _pool:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
        logging.info("🔒 Pool de base de datos cerrado")