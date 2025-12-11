import logging
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, HTTPException
from config import ALGORITHM, SECRET_KEY
from utils.websocket_manager import manager
from services.aula_service import aulas_estado, actualizar_estado_aula, get_device_id_por_aula
from services.auth_service import decode_access_token
import json
from security.jwt import verify_token
from jose import jwt, JWTError

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    # Validar JWT - puede ser device o usuario
    try:
        payload = verify_token(token, required_scope="device")
        
        # ✅ FIX: Intentar múltiples campos para device_id
        device_id = payload.get("sub") or payload.get("device_id") or payload.get("id")
        
        if not device_id:
            logging.error(f"❌ Token válido pero sin identificador. Payload: {payload}")
            await websocket.close(code=1008, reason="Token sin device_id")
            return
            
        logging.info(f"✅ Token válido para device_id: {device_id}")

    except Exception as e:
        logging.error(f"❌ Error validando token device: {e}")
        
        # Fallback: probar con el sistema de usuarios
        try:
            token_data = decode_access_token(token)
            device_id = token_data.id
            logging.info(f"✅ Token de usuario válido: {device_id}")
        except Exception as e2:
            logging.error(f"❌ Error validando token usuario: {e2}")
            await websocket.close(code=1008, reason="Invalid token")
            return

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
                if tipo == "nodo_conectado":
                    aula_nombre = mensaje.get("aula")
                    uptime = mensaje.get("uptime", 0)
                    
                    logging.info(f"👋 Saludo inicial recibido del dispositivo {device_id}: aula='{aula_nombre}'")
                    
                    # ✅ REGISTRAR EL MAPEO: device_id → aula_nombre
                    actualizar_estado_aula(device_id, {
                        "aula": aula_nombre,
                        "device_id": device_id,
                        "conectado": True,
                        "uptime": uptime,
                        "relay1": mensaje.get("relay1", False),
                        "relay2": mensaje.get("relay2", False)
                    })
                    
                    # 1. RESPONDER AL ESP32 (Vital para que no se desconecte)
                    await websocket.send_json({
                        "tipo": "ack_bienvenida",
                        "mensaje": "Conexión establecida correctamente"
                    })
                    
                    # 2. Avisar a los paneles web (Admin/Conserje)
                    await manager.notify_staff({
                        "tipo": "estado_dispositivo",
                        "device_id": device_id,
                        "aula": aula_nombre,
                        "estado": "online"
                    })
                elif tipo == "confirmacion_relay":
                    # ✅ NUEVO: El ESP32 confirma que cambió el relé
                    aula = mensaje.get("aula")
                    relay_num = mensaje.get("relay_num")
                    relay_state = mensaje.get("relay_state")
                    
                    logging.info(f"✅ Confirmación relay{relay_num}={relay_state} de {device_id} (aula: {aula})")
                    
                    # Actualizar estado local usando device_id como clave
                    if device_id in aulas_estado:
                        if relay_num == 1:
                            aulas_estado[device_id]["relay1"] = relay_state
                        elif relay_num == 2:
                            aulas_estado[device_id]["relay2"] = relay_state
                    
                    # Notificar a todos los paneles web (admin y conserje)
                    confirm_msg = {
                        "tipo": "confirmacion_relay",
                        "aula": aula,
                        "device_id": device_id,
                        "relay_num": relay_num,
                        "relay_state": relay_state
                    }
                    logging.info(f"📤 Enviando confirmación a staff: {confirm_msg}")
                    await manager.notify_staff(confirm_msg)
                elif tipo == "conexion":
                    device_id = mensaje.get("device_id")
                    aula = mensaje.get("aula")
                    ip = mensaje.get("ip")
                    rssi = mensaje.get("rssi")
                    uptime = mensaje.get("uptime")
                    
                    estado = actualizar_estado_aula(device_id, {
                        "aula": aula,
                        "device_id": device_id,
                        "conectado": True,
                        "ip": ip,
                        "rssi": rssi,
                        "uptime": uptime
                    })

                    # ✅ Solo admins reciben IP y datos técnicos
                    await manager.notify_admins({
                        "tipo": "dispositivo_conectado",
                        "device_id": device_id,
                        "aula": aula,
                        "ip": ip,
                        "rssi": rssi,
                        "uptime": uptime
                    })
                    
                    # ✅ Conserjes solo saben que el dispositivo se conectó
                    await manager.notify_conserjes({
                        "tipo": "dispositivo_conectado",
                        "aula": aula,
                        "conectado": True
                    })
                    
                    logging.info(f"✅ ESP32 conectado: {aula} (device_id: {device_id}, ip: {ip})")

                elif tipo == "datos_aula":
                    aula = mensaje.get("aula")
                    # Usar device_id como clave, pero guardar el nombre del aula en los datos
                    estado = actualizar_estado_aula(device_id, mensaje)

                    # ✅ Mensaje completo para admins (incluye IP y datos sensibles)
                    mensaje_admin = {
                        "tipo": "actualizacion_aula",
                        "aula": aula,
                        "device_id": device_id,
                        **estado  # Incluye todo: ip, rssi, uptime, etc.
                    }
                    
                    # ✅ Mensaje filtrado para conserjes (sin IP ni datos técnicos)
                    mensaje_conserje = {
                        "tipo": "actualizacion_aula",
                        "aula": aula,
                        "device_id": device_id,
                        "temperatura": estado.get("temperatura"),
                        "humedad": estado.get("humedad"),
                        "presion": estado.get("presion"),
                        "luz": estado.get("luz"),
                        "personas": estado.get("personas"),
                        "relay1": estado.get("relay1"),
                        "relay2": estado.get("relay2"),
                        "conectado": estado.get("conectado"),
                        # ❌ NO incluir: ip, rssi, uptime
                    }
                    
                    # Enviar según el rol
                    await manager.notify_admins(mensaje_admin)
                    await manager.notify_conserjes(mensaje_conserje)
                    
                    logging.debug(f"📊 Datos actualizados para device_id '{device_id}' (aula: {aula})")

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

                elif tipo == "solicitar_estado":
                    # Comando desde panel admin: solicitar actualización de datos a todos los ESP32
                    logging.info(f"🔃 Solicitando actualización de estado a todos los dispositivos")
                    
                    # Enviar comando a todos los ESP32 conectados
                    solicitud_msg = {
                        "tipo": "enviar_datos_actuales",
                        "timestamp": mensaje.get("timestamp", 0)
                    }
                    
                    await manager.broadcast_to_devices(solicitud_msg)
                    
                    # Confirmar al admin que se envió la solicitud
                    await websocket.send_json({
                        "tipo": "solicitud_enviada",
                        "mensaje": "Solicitud de actualización enviada a todos los dispositivos"
                    })
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
        # Avisar a los paneles web (Admin/Conserje)
        await manager.notify_staff({
            "tipo": "estado_dispositivo",
            "device_id": device_id,
            "estado": "offline"
        })


@router.websocket("/ws/admin")
async def admin_websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para administradores"""
    # Definimos user_id por defecto
    user_id = "desconocido"

    # ✅ 1. Intentar obtener el token de la cookie
    token = websocket.cookies.get("access_token")
    
    if not token:
        logging.warning("❌ WS Admin: Intento de conexión sin cookie 'access_token'")
        await websocket.close(code=1008, reason="No token")
        return
    
    try:
        # 2. Validar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        rol = payload.get("rol")
        user_id = payload.get("correo") or payload.get("sub") or payload.get("id") or "admin"
        
        logging.info(f"🔐 WS Admin: Token decodificado - rol={rol}, user={user_id}")
        
        # 3. Verificar permisos (solo admin)
        if rol != "administrador":
            logging.warning(f"⛔ WS Admin: Rol no autorizado ({rol}) para user {user_id}")
            await websocket.close(code=1008, reason="Unauthorized role")
            return
        
        logging.info(f"✅ WS Admin autorizado: {user_id}")

    except JWTError as e:
        logging.error(f"❌ WS Admin: Token inválido: {e}")
        await websocket.close(code=1008, reason="Invalid token")
        return
    except Exception as e:
        logging.error(f"❌ WS Admin: Error inesperado: {e}")
        await websocket.close(code=1008, reason="Server error")
        return

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Admin WebSocket conectando desde: {client_host}")

    # ✅ Registrar conexión de admin
    await manager.connect(websocket, client_type="admin")

    # ✅ Enviar estado inicial con LOGS
    dispositivos = manager.get_connected_devices()
    estado_aulas = dict(aulas_estado)  # Copia del diccionario
    
    mensaje_bienvenida = {
        "tipo": "admin_bienvenida",
        "dispositivos_conectados": dispositivos,
        "aulas_estado": estado_aulas
    }
    
    logging.info(f"📤 Enviando bienvenida a admin {user_id}:")
    logging.info(f"   - Dispositivos conectados: {dispositivos}")
    logging.info(f"   - Aulas estado keys: {list(estado_aulas.keys())}")
    
    await websocket.send_json(mensaje_bienvenida)

    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"📩 Mensaje admin WS recibido de {user_id}: {data[:200]}...")

            try:
                mensaje = json.loads(data)
                accion = mensaje.get("action")
                target_device_id = mensaje.get("device_id")
                
                logging.info(f"🎬 Admin acción: {accion}, target: {target_device_id}")

                # Procesar acciones del admin
                if accion == "actualizar_config":
                    config_data = mensaje.get("data", {})
                    
                    if not target_device_id:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": "Falta device_id"
                        })
                        continue
                    
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": "configurar_aula",
                        "device_id": target_device_id,
                        "data": config_data
                    })
                    
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id,
                        "mensaje": "Comando enviado" if success else "Dispositivo no conectado"
                    })
                    
                    logging.info(f"🔧 Config actualizada: {target_device_id} - success={success}")

                elif accion == "resetear_nodo":
                    if not target_device_id:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": "Falta device_id"
                        })
                        continue
                    
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": "resetear_nodo",
                        "device_id": target_device_id
                    })
                    
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id,
                        "mensaje": "Reset enviado" if success else "Dispositivo no conectado"
                    })
                    
                    logging.info(f"🔄 Reset enviado a: {target_device_id} - success={success}")

                elif accion == "test_conexion":
                    if not target_device_id:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": "Falta device_id"
                        })
                        continue
                    
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": "test_conexion",
                        "device_id": target_device_id
                    })
                    
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id,
                        "mensaje": "Test enviado" if success else "Dispositivo no conectado"
                    })
                    
                    logging.info(f"🧪 Test enviado a: {target_device_id} - success={success}")

                elif accion == "toggle_relay":
                    if not target_device_id:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": "Falta device_id"
                        })
                        continue
                    
                    relay_num = mensaje.get("relay_num", 1)
                    relay_state = mensaje.get("relay_state", False)
                    
                    success = await manager.send_to_device(target_device_id, {
                        "tipo": f"actualizacion_relay{relay_num}",
                        "device_id": target_device_id,
                        "relay_num": relay_num,
                        "relay": relay_state
                    })
                    
                    await websocket.send_json({
                        "tipo": "comando_enviado" if success else "error",
                        "accion": accion,
                        "device_id": target_device_id,
                        "relay_num": relay_num,
                        "relay_state": relay_state,
                        "mensaje": "Relay actualizado" if success else "Dispositivo no conectado"
                    })
                    
                    logging.info(f"🔧 Toggle relay{relay_num}={relay_state} en {target_device_id} - success={success}")

                elif accion == "listar_dispositivos":
                    dispositivos_actuales = manager.get_connected_devices()
                    estado_aulas_actual = dict(aulas_estado)
                    
                    await websocket.send_json({
                        "tipo": "lista_dispositivos",
                        "dispositivos_conectados": dispositivos_actuales,
                        "aulas_estado": estado_aulas_actual
                    })
                    
                    logging.info(f"📋 Lista dispositivos enviada a admin: {dispositivos_actuales}")

                else:
                    logging.warning(f"⚠️ Admin {user_id} intentó acción desconocida: {accion}")
                    await websocket.send_json({
                        "tipo": "error",
                        "mensaje": f"Acción desconocida: {accion}"
                    })

            except json.JSONDecodeError:
                logging.error(f"❌ JSON inválido del admin: {data[:100]}")
                await websocket.send_json({
                    "tipo": "error",
                    "mensaje": "JSON inválido"
                })
            except Exception as e:
                logging.error(f"❌ Error procesando mensaje admin: {e}")
                await websocket.send_json({
                    "tipo": "error",
                    "mensaje": f"Error: {str(e)}"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"❌ Admin desconectado: {client_host} (user: {user_id})")


@router.websocket("/ws/conserje")
async def conserje_websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket para conserjes - Solo control de relés"""
    
    user_id = "desconocido"

    token = websocket.cookies.get("access_token")
    
    if not token:
        logging.warning("❌ WS: Intento de conexión sin cookie 'access_token'")
        await websocket.close()
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        rol = payload.get("rol")
        user_id = payload.get("correo") or payload.get("sub") or "conserje"
        
        if rol != "conserje" and rol != "admin":
            logging.warning(f"⛔ WS: Rol no autorizado ({rol}) intentando conectar")
            await websocket.close()
            return
        
        logging.info(f"✅ WS Conserje autorizado: {user_id}")

    except JWTError as e:
        logging.error(f"❌ WS: Token inválido: {e}")
        await websocket.close()
        return
    except Exception as e:
        logging.error(f"❌ WS: Error inesperado: {e}")
        await websocket.close()
        return

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Conserje WebSocket conectando desde: {client_host}")

    await manager.connect(websocket, client_type="conserje")

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

                if accion == "toggle_relay":
                    # ✅ FIX: Recibir por nombre de aula y resolver device_id
                    aula_nombre = mensaje.get("aula")
                    relay_num = mensaje.get("relay_num", 1)
                    relay_state = mensaje.get("relay_state", False)
                    
                    if not aula_nombre:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": "Falta el nombre del aula"
                        })
                        continue
                    
                    # Buscar el device_id asociado al aula
                    device_id = get_device_id_por_aula(aula_nombre)
                    
                    if not device_id:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": f"No se encontró dispositivo para '{aula_nombre}'"
                        })
                        continue
                    
                    # ✅ Enviar comando al ESP32 con estructura consistente
                    success = await manager.send_to_device(device_id, {
                        "tipo": f"actualizacion_relay{relay_num}",
                        "device_id": device_id,
                        "aula": aula_nombre,
                        "relay_num": relay_num,
                        "relay": relay_state
                    })
                    
                    if success:
                        await websocket.send_json({
                            "tipo": "comando_enviado",
                            "accion": accion,
                            "aula": aula_nombre,
                            "relay_num": relay_num,
                            "relay_state": relay_state
                        })
                        logging.info(f"🔧 Conserje {user_id} cambió relay{relay_num}={relay_state} en {aula_nombre} (device: {device_id})")
                    else:
                        await websocket.send_json({
                            "tipo": "error",
                            "mensaje": f"Dispositivo '{device_id}' no está conectado"
                        })

                elif accion == "listar_dispositivos":
                    await websocket.send_json({
                        "tipo": "lista_dispositivos",
                        "dispositivos_conectados": manager.get_connected_devices(),
                        "aulas_estado": aulas_estado
                    })

                else:
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
