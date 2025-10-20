from typing import Dict, Any
from fastapi import HTTPException

# Estado en memoria (podría moverse a Redis en producción)
aulas_estado: Dict[str, Any] = {}

def actualizar_estado_aula(aula: str, datos: dict) -> dict:
    """Actualiza el estado de un aula en memoria"""
    aulas_estado[aula] = {
        "temperatura": datos.get("temperatura"),
        "luz": datos.get("luz"),
        "personas": datos.get("personas"),
        "clase_en_curso": datos.get("clase_en_curso"),
        "relay": aulas_estado.get(aula, {}).get("relay", False),
    }
    return aulas_estado[aula]

def obtener_estado_aulas() -> dict:
    """Obtiene el estado de todas las aulas"""
    return aulas_estado

def actualizar_relay(aula: str, estado: bool) -> dict:
    """Actualiza el estado del relay de un aula"""
    if aula not in aulas_estado:
        raise HTTPException(status_code=404, detail="Aula no encontrada")
    
    aulas_estado[aula]["relay"] = estado
    return aulas_estado[aula]