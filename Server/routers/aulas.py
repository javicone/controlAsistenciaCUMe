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
    await manager.notify_staff({
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
    # 1. Actualizar base de datos / memoria
    estado = actualizar_relay(control.aula, control.aerotermia, control.iluminacion)
    # 2. ENVIAR ORDEN FÍSICA AL ESP32 (Esto faltaba o se hacía mal con broadcast)
    # Asumimos que el ID del dispositivo es algo como "esp32_aula_X"
    device_id = f"esp32_{control.aula}" 
    exito = await manager.send_to_device(device_id, {
        "tipo": "comando_relay",
        "aerotermia": control.aerotermia,
        "iluminacion": control.iluminacion
    })
    if not exito:
        return {"mensaje": "Estado actualizado en BD, pero el ESP32 está desconectado", "warning": True}
    # 3. ACTUALIZAR PANELES WEB (Solo a humanos)
    await manager.notify_staff({
        "tipo": "actualizacion_relay",
        "aula": control.aula,
        "aerotermia": control.aerotermia,
        "iluminacion": control.iluminacion,
        **estado
    })