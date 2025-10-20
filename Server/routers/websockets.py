import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.websocket_manager import manager
from services.aula_service import aulas_estado, actualizar_estado_aula
import json
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Cliente WebSocket conectando desde: {client_host}")
    
    await manager.connect(websocket)
    
    # Enviar estado inicial
    await websocket.send_json({
        "tipo": "estado_inicial",
        "data": aulas_estado
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            logging.debug(f"📩 Mensaje WS recibido: {data[:100]}...")
            
            try:
                mensaje = json.loads(data)
                tipo = mensaje.get("tipo")
                
                if tipo == "conexion":
                    aula = mensaje.get("aula")
                    logging.info(f"✅ ESP32 conectado: {aula}")
                
                elif tipo == "datos_aula":
                    aula = mensaje.get("aula")
                    estado = actualizar_estado_aula(aula, mensaje)
                    
                    # Broadcast a todos los clientes
                    await manager.broadcast({
                        "tipo": "actualizacion_aula",
                        "aula": aula,
                        **estado
                    })
                    logging.debug(f"📊 Datos actualizados: {aula}")
                
                else:
                    logging.warning(f"⚠️ Tipo desconocido: {tipo}")
                    
            except json.JSONDecodeError:
                logging.error(f"❌ JSON inválido: {data}")
            except Exception as e:
                logging.error(f"❌ Error procesando mensaje: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"❌ Cliente desconectado: {client_host}")