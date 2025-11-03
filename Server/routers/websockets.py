import logging
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from utils.websocket_manager import manager
from services.aula_service import aulas_estado, actualizar_estado_aula
from security.jwt import verify_token
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Validar JWT en query (?token=...)
    payload = verify_token(token, required_scope="device")
    device_id = payload["sub"]

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Cliente WebSocket conectando desde: {client_host} (device_id: {device_id})")

    await manager.connect(websocket)

    # Enviar mensaje de bienvenida y estado inicial
    await websocket.send_json({
        "welcome": True,
        "device_id": device_id,
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
                    logging.info(f"✅ ESP32 conectado: {aula} (device_id: {device_id})")

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
        logging.info(f"❌ Cliente desconectado: {client_host} (device_id: {device_id})")