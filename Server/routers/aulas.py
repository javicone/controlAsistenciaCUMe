from fastapi import APIRouter
from models.aula import DatosAula, ControlRelay
from services.aula_service import actualizar_estado_aula, obtener_estado_aulas, actualizar_relay
from utils.websocket_manager import manager

router = APIRouter(prefix="/aulas", tags=["Aulas"])

@router.post("/datos")
async def recibir_datos_aula(datos: DatosAula):
    """Recibe y actualiza los datos de un aula desde el ESP32"""
    estado = actualizar_estado_aula(datos.aula, datos.dict())
    
    # Broadcast a WebSocket clients
    await manager.broadcast({
        "tipo": "actualizacion_aula",
        "aula": datos.aula,
        **estado
    })
    
    return {"mensaje": "Datos actualizados correctamente"}

@router.get("/estado")
async def obtener_estados():
    """Obtiene el estado de todas las aulas"""
    return obtener_estado_aulas()

@router.post("/relay")
async def controlar_relay_aula(control: ControlRelay):
    """Controla el relay de un aula"""
    estado = actualizar_relay(control.aula, control.relay)
    
    # Broadcast a WebSocket clients
    await manager.broadcast({
        "tipo": "actualizacion_relay",
        "aula": control.aula,
        "relay": control.relay,
        **estado
    })
    
    return {"mensaje": f"Relay en aula {control.aula} actualizado"}