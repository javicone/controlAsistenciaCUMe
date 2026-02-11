"""
Sistema de hashing de contraseñas usando bcrypt.

Proporciona funciones seguras para:
- Hashear contraseñas nuevas
- Verificar contraseñas contra su hash
- Detectar hashes que necesitan actualización
"""

from passlib.context import CryptContext
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Configuración de bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Factor de trabajo (más alto = más seguro pero más lento)
)

def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash bcrypt de la contraseña (formato: $2b$12$...)
        
    Example:
        >>> hashed = hash_password("MiContraseña123!")
        >>> hashed.startswith("$2b$")
        True
    """
    try:
        hashed = pwd_context.hash(password)
        logger.debug(f"🔒 Contraseña hasheada exitosamente")
        return hashed
    except Exception as e:
        logger.error(f"❌ Error hasheando contraseña: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Esta función es resistente a timing attacks ya que bcrypt
    internamente usa comparación de tiempo constante.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash bcrypt almacenado
        
    Returns:
        bool: True si la contraseña es correcta, False en caso contrario
        
    Example:
        >>> hashed = hash_password("MiContraseña123!")
        >>> verify_password("MiContraseña123!", hashed)
        True
        >>> verify_password("OtraContraseña", hashed)
        False
    """
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        if result:
            logger.debug("✅ Contraseña verificada correctamente")
        else:
            logger.debug("❌ Contraseña incorrecta")
        return result
    except Exception as e:
        logger.warning(f"⚠️ Error verificando contraseña: {e}")
        # Si hay error (ej: hash inválido), retornar False
        return False

def needs_rehash(hashed_password: str) -> bool:
    """
    Verifica si un hash necesita ser regenerado.
    
    Útil cuando se cambia el factor de trabajo (rounds) o se actualiza
    el algoritmo de hashing.
    
    Args:
        hashed_password: Hash bcrypt existente
        
    Returns:
        bool: True si debe rehashear la contraseña
        
    Example:
        >>> # Si cambiamos de rounds=10 a rounds=12
        >>> needs_rehash("$2b$10$old_hash...")
        True
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception as e:
        logger.warning(f"⚠️ Error verificando si necesita rehash: {e}")
        return False

def is_hashed(password: str) -> bool:
    """
    Verifica si una cadena parece ser un hash bcrypt.
    
    Args:
        password: Cadena a verificar
        
    Returns:
        bool: True si parece un hash bcrypt válido
        
    Example:
        >>> is_hashed("$2b$12$abc123...")
        True
        >>> is_hashed("contraseña_texto_plano")
        False
    """
    return password.startswith("$2b$") or password.startswith("$2a$")
