import logging
import json
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, HTTPException, status
from config import ALGORITHM, SECRET_KEY
from utils.websocket_manager import manager
from services.aula_service import aulas_estado, actualizar_estado_aula, get_device_id_por_aula, verificar_nombre_aula_disponible
from services.auth_service import decode_access_token
from security.jwt import verify_token
from jose import jwt, JWTError

router = APIRouter()

# ==============================================================================
# 1. HELPERS DE AUTENTICACIÓN (Privados)
# ==============================================================================

async def _obtener_identidad_dispositivo(websocket: WebSocket, token: str) -> str:
    """Valida el token y retorna el device_id o cierra el socket."""
    logging.info(f"🔐 Validando token para WebSocket (len={len(token)})...")
    
    error_hs256 = None
    error_rs256 = None
    
    # Primero intentamos con el sistema HS256 (auth_service) que es el que usa /auth/device
    try:
        token_data = decode_access_token(token)
        logging.info(f"✅ Token HS256 válido para: {token_data.id} (rol: {token_data.rol})")
        return token_data.id
    except Exception as e:
        error_hs256 = str(e)
        logging.info(f"🔄 Token HS256 falló: {error_hs256}")
    
    # Fallback: Intentar con RS256 (security/jwt.py) para tokens de otro origen
    try:
        payload = verify_token(token, required_scope="device")
        device_id = payload.get("sub") or payload.get("device_id") or payload.get("id")
        
        if device_id:
            logging.info(f"✅ Token RS256 válido para device_id: {device_id}")
            return device_id
        else:
            error_rs256 = "Token válido pero sin device_id en payload"
            logging.warning(f"⚠️ {error_rs256}")
            
    except Exception as e:
        error_rs256 = str(e)
        logging.info(f"🔄 Token RS256 falló: {error_rs256}")
    
    # Si llegamos aquí, ambos métodos fallaron
    logging.error(f"❌ Validación de token fallida:")
    logging.error(f"   - HS256: {error_hs256}")
    logging.error(f"   - RS256: {error_rs256}")
    
    # Cerrar conexión - NOTA: El websocket aún no ha sido aceptado
    # Usamos accept() primero para poder cerrar con un código de error apropiado
    try:
        await websocket.accept()
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token inválido")
    except Exception as close_error:
        logging.info(f"Error cerrando websocket: {close_error}")
    
    return None

async def _obtener_identidad_staff(websocket: WebSocket, roles_permitidos: list) -> tuple[str, str]:
    """Valida cookie y rol. Retorna (user_id, rol) o (None, None)."""
    # ✅ PRIMERO aceptar la conexión WebSocket
    await websocket.accept()
    
    token = websocket.cookies.get("access_token")
    if not token:
        logging.warning("❌ Staff: Falta cookie 'access_token'")
        await websocket.send_json({"tipo": "error", "mensaje": "No autenticado. Recarga la página."})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None, None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        rol = payload.get("rol")
        user_id = payload.get("correo") or payload.get("sub") or "staff"

        if rol not in roles_permitidos:
            logging.warning(f"⛔ Rol {rol} no autorizado.")
            await websocket.send_json({"tipo": "error", "mensaje": "Rol no autorizado"})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None, None
            
        logging.info(f"✅ Staff autenticado: {user_id} (rol: {rol})")
        return user_id, rol
    except JWTError as e:
        logging.error(f"❌ Staff: Token inválido - {e}")
        await websocket.send_json({"tipo": "error", "mensaje": "Token inválido. Inicia sesión nuevamente."})
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None, None

# ==============================================================================
# 2. LÓGICA DE NEGOCIO - DISPOSITIVOS (IoT)
# ==============================================================================

async def registrar_vinculacion_aula(device_id: str, mensaje: dict, websocket: WebSocket):
    """Procesa el mensaje inicial 'nodo_conectado'."""
    aula_nombre = mensaje.get("aula")
    logging.info(f"👋 Vinculando {device_id} al aula '{aula_nombre}'")

    try:
        # Verificar si el nombre de aula ya está en uso por OTRO dispositivo
        if aula_nombre:
            disponible, device_en_uso = verificar_nombre_aula_disponible(aula_nombre, device_id)
            if not disponible:
                logging.warning(f"⚠️ Nombre '{aula_nombre}' ya en uso por {device_en_uso}. {device_id} se conectará con nombre conflictivo.")
                # Notificar al staff del conflicto
                await manager.notify_staff({
                    "tipo": "conflicto_nombre_aula",
                    "device_id": device_id,
                    "aula_solicitada": aula_nombre,
                    "device_en_uso": device_en_uso,
                    "mensaje": f"⚠️ El dispositivo {device_id} intentó usar el nombre '{aula_nombre}' que ya usa {device_en_uso}"
                })
        
        actualizar_estado_aula(device_id, {
            "aula": aula_nombre,
            "device_id": device_id,
            "conectado": True,
            "ip": mensaje.get("ip"),
            "uptime": mensaje.get("uptime", 0),
            "relay1": mensaje.get("relay1", False),
            "relay2": mensaje.get("relay2", False)
        })
        logging.debug(f"✅ Estado actualizado para {device_id}")

        # 1. Confirmar al ESP32 (Vital)
        await websocket.send_json({"tipo": "ack_bienvenida", "mensaje": "Conexión establecida"})
        logging.debug(f"✅ ACK enviado a {device_id}")
        
        # 2. Notificar al personal
        await manager.notify_staff({
            "tipo": "estado_dispositivo", "device_id": device_id, "aula": aula_nombre, "estado": "online"
        })
        logging.debug(f"✅ Staff notificado sobre {device_id}")
        
    except Exception as e:
        logging.error(f"❌ Error en registrar_vinculacion_aula para {device_id}: {type(e).__name__}: {e}")

async def procesar_telemetria_ambiental(device_id: str, mensaje: dict, websocket: WebSocket):
    """Procesa 'datos_aula' o 'conexion'."""
    estado = actualizar_estado_aula(device_id, mensaje)
    aula = mensaje.get("aula")

    # Notificación completa para admins (con IP, RSSI, etc.)
    await manager.notify_admins({
        "tipo": "actualizacion_aula", "aula": aula, "device_id": device_id, **estado
    })
    
    # Notificación filtrada para conserjes
    datos_publicos = {k: v for k, v in estado.items() if k not in ['ip', 'rssi', 'uptime']}
    await manager.notify_conserjes({
        "tipo": "actualizacion_aula", "aula": aula, "device_id": device_id, "conectado": True, **datos_publicos
    })

async def sincronizar_estado_reles(device_id: str, mensaje: dict, websocket: WebSocket):
    """Procesa 'confirmacion_relay'."""
    relay_num = mensaje.get("relay_num")
    relay_state = mensaje.get("relay_state")
    aula = mensaje.get("aula")
    
    logging.info(f"🔄 CONFIRMACION RELAY recibida de {device_id}:")
    logging.info(f"   Aula: {aula}")
    logging.info(f"   Relay: {relay_num}")
    logging.info(f"   Estado: {relay_state}")

    if device_id in aulas_estado:
        key = "relay1" if relay_num == 1 else "relay2"
        estado_previo = aulas_estado[device_id].get(key)
        aulas_estado[device_id][key] = relay_state
        logging.info(f"   Estado en servidor actualizado: {estado_previo} → {relay_state}")
    else:
        logging.warning(f"   ⚠️ Device {device_id} no encontrado en aulas_estado")

    logging.info(f"📢 Notificando a staff sobre cambio de relay")
    await manager.notify_staff({
        "tipo": "confirmacion_relay", "aula": aula, "device_id": device_id,
        "relay_num": relay_num, "relay_state": relay_state
    })

async def responder_ping(device_id: str, mensaje: dict, websocket: WebSocket):
    await websocket.send_json({"tipo": "pong"})

async def reenviar_log_admin(device_id: str, mensaje: dict, websocket: WebSocket):
    """Para mensajes de depuración como 'test_respuesta' o 'reset_confirmado'."""
    # Asegurar que el device_id esté en el mensaje
    mensaje["device_id"] = device_id
    
    # Si es test_respuesta, obtener información adicional del estado
    if mensaje.get("tipo") == "test_respuesta":
        if device_id in aulas_estado:
            aula_data = aulas_estado[device_id]
            # Añadir nombre del aula si no viene en el mensaje
            if "aula" not in mensaje:
                mensaje["aula"] = aula_data.get("aula", device_id)
            # Añadir estado de relés del estado guardado si no vienen
            if "relay1" not in mensaje:
                mensaje["relay1"] = aula_data.get("relay1", False)
            if "relay2" not in mensaje:
                mensaje["relay2"] = aula_data.get("relay2", False)
    
    logging.info(f"📡 Reenviando a admins: {mensaje.get('tipo')} de {device_id}")
    await manager.notify_admins(mensaje)

async def procesar_config_confirmada(device_id: str, mensaje: dict, websocket: WebSocket):
    """
    Procesa la confirmación de configuración del ESP32.
    Actualiza aulas_estado con el nuevo nombre si se cambió.
    """
    logging.info(f"⚙️ Config confirmada por {device_id}")
    
    # Verificar si hay configuración pendiente para este dispositivo
    if device_id in _config_pendiente:
        config_data = _config_pendiente[device_id]
        nuevo_nombre = config_data.get("nombre")
        
        if nuevo_nombre and device_id in aulas_estado:
            nombre_anterior = aulas_estado[device_id].get("aula", "desconocido")
            aulas_estado[device_id]["aula"] = nuevo_nombre
            logging.info(f"✅ Aula renombrada: '{nombre_anterior}' → '{nuevo_nombre}' (device: {device_id})")
            
            # Notificar al staff del cambio de nombre
            await manager.notify_staff({
                "tipo": "aula_renombrada",
                "device_id": device_id,
                "nombre_anterior": nombre_anterior,
                "nombre_nuevo": nuevo_nombre
            })
        
        # Limpiar configuración pendiente
        del _config_pendiente[device_id]
    
    # Reenviar a admins también
    mensaje["device_id"] = device_id
    await manager.notify_admins(mensaje)

# Diccionario para guardar configuraciones pendientes de confirmación
_config_pendiente: dict = {}

# --- MAPA DE ACCIONES DISPOSITIVO ---
MAPA_ACCIONES_DISPOSITIVO = {
    "nodo_conectado": registrar_vinculacion_aula,
    "conexion": procesar_telemetria_ambiental, # Reutilizamos lógica si es similar
    "datos_aula": procesar_telemetria_ambiental,
    "confirmacion_relay": sincronizar_estado_reles,
    "ping": responder_ping,
    "test_respuesta": reenviar_log_admin,
    "reset_confirmado": reenviar_log_admin,
    "config_confirmada": procesar_config_confirmada
}

# ==============================================================================
# 3. LÓGICA DE NEGOCIO - STAFF (Admin/Conserje)
# ==============================================================================

async def ejecutar_cambio_relay(usuario_id: str, mensaje: dict, websocket: WebSocket):
    """Busca el dispositivo y envía orden de cambio de relé."""
    logging.info(f"🎛️ Ejecutar cambio relay - Usuario: {usuario_id}, Mensaje: {mensaje}")
    
    # 1. Resolver Device ID
    target_id = mensaje.get("device_id")
    if not target_id and mensaje.get("aula"):
        target_id = get_device_id_por_aula(mensaje.get("aula"))
        logging.info(f"   Device ID resuelto por aula: {target_id}")
    
    if not target_id:
        logging.warning(f"❌ Device ID no encontrado para: {mensaje}")
        await websocket.send_json({"tipo": "error", "mensaje": "Dispositivo no encontrado"})
        return

    # 2. Enviar comando
    r_num = mensaje.get("relay_num", 1)
    r_state = mensaje.get("relay_state", False)
    
    logging.info(f"📤 Enviando a {target_id}: relay{r_num} = {r_state}")
    
    success = await manager.send_to_device(target_id, {
        "tipo": f"actualizacion_relay{r_num}", "device_id": target_id,
        "relay_num": r_num, "relay": r_state
    })
    
    logging.info(f"   Resultado envío: {'✅ Éxito' if success else '❌ Falló'}")
    
    # 3. Feedback al usuario
    await websocket.send_json({
        "tipo": "comando_enviado" if success else "error",
        "mensaje": "Orden enviada" if success else "Dispositivo offline",
        "aula": mensaje.get("aula")
    })

async def listar_dispositivos(usuario_id: str, mensaje: dict, websocket: WebSocket):
    await websocket.send_json({
        "tipo": "lista_dispositivos",
        "dispositivos_conectados": manager.get_connected_devices(),
        "aulas_estado": aulas_estado
    })

# --- Acciones exclusivas Admin ---
async def admin_configurar_aula(usuario_id: str, mensaje: dict, websocket: WebSocket):
    target_id = mensaje.get("device_id")
    config_data = mensaje.get("data", {})
    
    if not target_id:
        await websocket.send_json({"tipo": "error", "mensaje": "Falta device_id"})
        return
    
    # Validar si el nuevo nombre ya está en uso por otro dispositivo
    nuevo_nombre = config_data.get("nombre")
    if nuevo_nombre:
        disponible, device_en_uso = verificar_nombre_aula_disponible(nuevo_nombre, target_id)
        if not disponible:
            await websocket.send_json({
                "tipo": "error", 
                "mensaje": f"El nombre '{nuevo_nombre}' ya está en uso por el dispositivo {device_en_uso}"
            })
            logging.warning(f"⚠️ Intento de renombrar {target_id} a '{nuevo_nombre}' rechazado: ya en uso por {device_en_uso}")
            return
    
    # Guardar la configuración pendiente para aplicarla cuando el ESP32 confirme
    if config_data:
        _config_pendiente[target_id] = config_data
        logging.info(f"📝 Config pendiente guardada para {target_id}: {config_data}")
    
    # Enviar al dispositivo
    success = await manager.send_to_device(target_id, {"tipo": "configurar_aula", "data": config_data})
    
    if success:
        await websocket.send_json({"tipo": "info", "mensaje": "Configuración enviada, esperando confirmación..."})
    else:
        # Si falla el envío, limpiar configuración pendiente
        if target_id in _config_pendiente:
            del _config_pendiente[target_id]
        await websocket.send_json({"tipo": "error", "mensaje": "Dispositivo no conectado"})

async def admin_resetear_nodo(usuario_id: str, mensaje: dict, websocket: WebSocket):
    target_id = mensaje.get("device_id")
    if target_id:
        await manager.send_to_device(target_id, {"tipo": "resetear_nodo"})
        await websocket.send_json({"tipo": "info", "mensaje": "Orden de reset enviada"})

async def admin_solicitar_estado_global(usuario_id: str, mensaje: dict, websocket: WebSocket):
    await manager.broadcast_to_devices({"tipo": "enviar_datos_actuales"})
    await websocket.send_json({"tipo": "info", "mensaje": "Solicitud broadcast enviada"})

# --- MAPAS DE ACCIONES STAFF ---
ACCIONES_COMUNES = {
    "toggle_relay": ejecutar_cambio_relay,
    "listar_dispositivos": listar_dispositivos
}

ACCIONES_ADMIN = {
    **ACCIONES_COMUNES,
    "actualizar_config": admin_configurar_aula,
    "resetear_nodo": admin_resetear_nodo,
    "solicitar_estado": admin_solicitar_estado_global,
    "test_conexion": lambda u, m, w: manager.send_to_device(m.get("device_id"), {"tipo": "test_conexion"})
}

# ==============================================================================
# 4. ENDPOINTS WEBSOCKET (Ruteadores)
# ==============================================================================

@router.websocket("/ws")
async def websocket_endpoint_device(websocket: WebSocket, token: str = Query(...)):
    """Endpoint principal para dispositivos IoT (ESP32)."""
    device_id = await _obtener_identidad_dispositivo(websocket, token)
    if not device_id: return

    client_host = websocket.client.host if websocket.client else "unknown"
    logging.info(f"🔌 Conectando dispositivo: {device_id} ({client_host})")

    await manager.connect(websocket, client_type="device", client_id=device_id)

    # Estado inicial
    await websocket.send_json({"welcome": True, "device_id": device_id, "tipo": "estado_inicial", "data": aulas_estado})

    try:
        while True:
            # Usar receive() genérico para manejar todos los tipos de mensajes
            message = await websocket.receive()
            
            # Log detallado del tipo de mensaje recibido (INFO para depuración)
            msg_type = message.get("type", "unknown")
            logging.info(f"📨 [{device_id}] Mensaje recibido: type={msg_type}, keys={list(message.keys())}")
            
            # Actualizar última actividad
            manager.update_activity(device_id)
            
            # Manejar diferentes tipos de mensajes WebSocket
            if msg_type == "websocket.receive":
                data = message.get("text") or message.get("bytes", b"").decode("utf-8", errors="ignore")
                
                if not data:
                    continue  # Mensaje vacío, continuar
                
                try:
                    mensaje = json.loads(data)
                    tipo = mensaje.get("tipo")
                    
                    # Despacho dinámico de funciones
                    handler = MAPA_ACCIONES_DISPOSITIVO.get(tipo)
                    if handler:
                        await handler(device_id, mensaje, websocket)
                    else:
                        logging.warning(f"⚠️ Comando desconocido de {device_id}: {tipo}")

                except json.JSONDecodeError:
                    logging.error(f"❌ JSON corrupto de {device_id}: {data[:100]}")
                except Exception as e:
                    logging.error(f"❌ Error procesando mensaje de {device_id}: {type(e).__name__}: {e}")
                    
            elif msg_type == "websocket.disconnect":
                logging.info(f"📴 Mensaje de desconexión recibido de {device_id}")
                break
            
            else:
                # Log para cualquier otro tipo de mensaje (ping, pong, etc.)
                logging.debug(f"📡 [{device_id}] Tipo no manejado: {msg_type}")

    except WebSocketDisconnect as wsd:
        logging.info(f"❌ Dispositivo desconectado (WebSocketDisconnect): {device_id}, código: {wsd.code}")
    except Exception as e:
        logging.error(f"❌ Error en WebSocket de {device_id}: {type(e).__name__}: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        # Siempre limpiar la conexión al salir
        manager.disconnect(websocket, client_id=device_id)
        try:
            await manager.notify_staff({"tipo": "estado_dispositivo", "device_id": device_id, "estado": "offline"})
        except:
            pass  # Ignorar errores al notificar


@router.websocket("/ws/admin")
async def websocket_endpoint_admin(websocket: WebSocket):
    """Endpoint para panel de administración."""
    user_id, rol = await _obtener_identidad_staff(websocket, ["administrador"])
    if not user_id: 
        return  # La conexión ya fue cerrada por _obtener_identidad_staff

    await manager.connect(websocket, client_type="admin")
    
    # Bienvenida
    await websocket.send_json({
        "tipo": "admin_bienvenida",
        "dispositivos_conectados": manager.get_connected_devices(),
        "aulas_estado": aulas_estado
    })

    try:
        while True:
            data = await websocket.receive_text()
            mensaje = json.loads(data)
            accion = mensaje.get("action")
            
            # Despacho dinámico
            handler = ACCIONES_ADMIN.get(accion)
            if handler:
                await handler(user_id, mensaje, websocket)
            else:
                await websocket.send_json({"tipo": "error", "mensaje": f"Acción desconocida: {accion}"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"❌ Admin desconectado: {user_id}")


@router.websocket("/ws/conserje")
async def websocket_endpoint_conserje(websocket: WebSocket):
    """Endpoint para panel de conserjería (restringido)."""
    # Permitimos admin también aquí por si quiere probar la vista de conserje
    user_id, rol = await _obtener_identidad_staff(websocket, ["conserje", "administrador"]) 
    if not user_id: 
        return  # La conexión ya fue cerrada por _obtener_identidad_staff

    await manager.connect(websocket, client_type="conserje")
    
    await websocket.send_json({
        "tipo": "conserje_bienvenida",
        "dispositivos_conectados": manager.get_connected_devices(),
        "aulas_estado": aulas_estado
    })

    try:
        while True:
            data = await websocket.receive_text()
            mensaje = json.loads(data)
            accion = mensaje.get("action")

            # Solo permitimos acciones comunes (toggle relay, listar)
            handler = ACCIONES_COMUNES.get(accion)
            if handler:
                await handler(user_id, mensaje, websocket)
            else:
                await websocket.send_json({"tipo": "error", "mensaje": "Acción no autorizada o desconocida"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logging.info(f"❌ Conserje desconectado: {user_id}")