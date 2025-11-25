import logging
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, HTTPException
from utils.websocket_manager import manager
from services.aula_service import aulas_estado, actualizar_estado_aula
from services.auth_service import decode_access_token
import json
from security.jwt import verify_token

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Validar JWT - puede ser device o usuario
    try:

        payload = verify_token(token, required_scope="device")
        device_id = payload["sub"]
    except:
        # Fallback: probar con el sistema de usuarios
        token_data = decode_access_token(token)
        device_id = token_data.id

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Cliente WebSocket conectando desde: {client_host} (device_id: {device_id})")

    # Registrar conexión con device_id
    await manager.connect(websocket, client_type="device", client_id=device_id)

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
            logging.debug(f"📩 Mensaje WS recibido de {device_id}: {data[:100]}...")

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

                elif tipo == "ping":
                    await websocket.send_json({"tipo": "pong"})
                    logging.debug(f"🏓 Pong enviado a {device_id}")

                elif tipo == "test_respuesta":
                    # Respuesta del ESP32 al comando test_conexion
                    logging.info(f"🧪 Test response recibido de {device_id}: {mensaje}")
                    # Reenviar solo a admins (no a conserjes)
                    await manager.notify_admins(mensaje)

                elif tipo == "reset_confirmado":
                    # Confirmación de reset del ESP32
                    logging.info(f"🔄 Reset confirmado por {device_id}")
                    # Reenviar solo a admins (no a conserjes)
                    await manager.notify_admins(mensaje)

                elif tipo == "config_confirmada":
                    # Confirmación de configuración del ESP32
                    logging.info(f"⚙️ Configuración confirmada por {device_id}")
                    # Reenviar solo a admins (no a conserjes)
                    await manager.notify_admins(mensaje)

                elif tipo == "administrador":
                    comando = mensaje.get("comando")
                    logging.info(f"🛠 Comando administrador recibido: {comando} (device_id: {device_id})")
                    # Aquí se podrían procesar comandos específicos
                    if comando == "test_conexion":
                        await websocket.send_json({"tipo": "test_conexion", "device_id": device_id, "status": "ok"})
                        logging.info(f"🔄 Comando test_conexion enviado a {device_id}")
                    elif comando == "resetear_nodo":
                        # Lógica para resetear nodo (si aplica)
                        await websocket.send_json({"tipo": "resetear_nodo", "device_id": device_id, "status": "resetting"})
                        logging.info(f"🔄 Comando resetear_nodo recibido para {device_id}")

                    elif comando == "configurar_aula":
                        nueva_config = mensaje.get("data", {})
                        # Lógica para configurar aula (si aplica)
                        # comprobar que no se repitan los valores, etc.

                        await websocket.send_json({"tipo": "configurar_aula", "device_id": device_id, "status": "configuring", "data": nueva_config})
                        logging.info(f"🔄 Comando configurar_aula recibido con config {nueva_config} para {device_id}")

                else:
                    logging.warning(f"⚠️ Tipo desconocido: {tipo}")

            except json.JSONDecodeError:
                logging.error(f"❌ JSON inválido: {data}")
            except Exception as e:
                logging.error(f"❌ Error procesando mensaje: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id=device_id)
        logging.info(f"❌ Cliente desconectado: {client_host} (device_id: {device_id})")


@router.websocket("/ws/admin")
async def admin_websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """Endpoint WebSocket para administradores"""
    # Validar token y verificar que sea admin
    token_data = decode_access_token(token)
    if token_data.rol != "administrador":
        raise HTTPException(status_code=403, detail="Solo administradores")
    
    user_id = token_data.id

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Admin WebSocket conectando desde: {client_host} (user: {user_id})")

    # Registrar conexión de admin (sin client_id)
    await manager.connect(websocket, client_type="admin")

    # Enviar estado inicial (lista de dispositivos conectados)
    await websocket.send_json({
        "tipo": "admin_bienvenida",
        "dispositivos_conectados": manager.get_connected_devices(),
        "aulas_estado": aulas_estado
    })

    try:
        while True:
            data = await websocket.receive_text()
            logging.debug(f"📩 Mensaje admin WS recibido de {user_id}: {data[:100]}...")

            try:
                mensaje = json.loads(data)
                accion = mensaje.get("action")
                target_device_id = mensaje.get("device_id")

                # Procesar acciones del admin
                if accion == "actualizar_config":
                    config_data = mensaje.get("data", {})
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": "configurar_aula",
                        "device_id": target_device_id,
                        "data": config_data
                    })
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id
                    })

                elif accion == "resetear_nodo":
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": "resetear_nodo",
                        "device_id": target_device_id
                    })
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id
                    })

                elif accion == "test_conexion":
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": "test_conexion",
                        "device_id": target_device_id
                    })
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id
                    })

                elif accion == "toggle_relay":
                    relay_num = mensaje.get("relay_num", 1)
                    relay_state = mensaje.get("relay_state", False)
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": f"actualizacion_relay{relay_num}",
                        "device_id": target_device_id,
                        "relay": relay_state
                    })
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id
                    })

                elif accion == "listar_dispositivos":
                    await websocket.send_json({
                        "tipo": "lista_dispositivos",
                        "dispositivos_conectados": manager.get_connected_devices()
                    })

            except json.JSONDecodeError:
                logging.error(f"❌ JSON inválido del admin")
            except Exception as e:
                logging.error(f"❌ Error procesando mensaje admin: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"❌ Admin desconectado: {client_host} (user: {user_id})")


@router.websocket("/ws/conserje")
async def conserje_websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """Endpoint WebSocket para conserjes - Solo control de relés"""
    # Validar token y verificar que sea conserje
    token_data = decode_access_token(token)
    if token_data.rol != "conserje":
        raise HTTPException(status_code=403, detail="Solo conserjes")
    
    user_id = token_data.id

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Conserje WebSocket conectando desde: {client_host} (user: {user_id})")

    # Registrar conexión de conserje
    await manager.connect(websocket, client_type="conserje")

    # Enviar estado inicial (lista de dispositivos + estado de aulas)
    await websocket.send_json({
        "tipo": "conserje_bienvenida",
        "dispositivos_conectados": manager.get_connected_devices(),
        "aulas_estado": aulas_estado
    })

    try:
        while True:
            data = await websocket.receive_text()
            logging.debug(f"📩 Mensaje conserje WS recibido de {user_id}: {data[:100]}...")

            try:
                mensaje = json.loads(data)
                accion = mensaje.get("action")
                target_device_id = mensaje.get("device_id")

                # SOLO permitir toggle_relay (control de calefacción/luces)
                if accion == "toggle_relay":
                    relay_num = mensaje.get("relay_num", 1)
                    relay_state = mensaje.get("relay_state", False)
                    
                    # TODO: Aquí podrías añadir validación de permisos
                    # Por ejemplo, verificar si el admin ha habilitado el control manual
                    # if not relay_control_habilitado:
                    #     await websocket.send_json({"tipo": "error", "mensaje": "Control de relés deshabilitado"})
                    #     continue
                    
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": f"actualizacion_relay{relay_num}",
                        "device_id": target_device_id,
                        "relay": relay_state
                    })
                    
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id
                    })
                    
                    logging.info(f"🔧 Conserje {user_id} cambió relay{relay_num}={relay_state} en {target_device_id}")

                elif accion == "listar_dispositivos":
                    await websocket.send_json({
                        "tipo": "lista_dispositivos",
                        "dispositivos_conectados": manager.get_connected_devices(),
                        "aulas_estado": aulas_estado
                    })

                else:
                    # Rechazar cualquier otro comando (resetear, configurar, test)
                    logging.warning(f"⚠️ Conserje {user_id} intentó acción no permitida: {accion}")
                    await websocket.send_json({
                        "tipo": "error",
                        "mensaje": "Acción no permitida para conserjes"
                    })

            except json.JSONDecodeError:
                logging.error(f"❌ JSON inválido del conserje")
            except Exception as e:
                logging.error(f"❌ Error procesando mensaje conserje: {e}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"❌ Conserje desconectado: {client_host} (user: {user_id})")