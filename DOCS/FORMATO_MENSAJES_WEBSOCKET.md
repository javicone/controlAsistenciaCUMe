# 📡 Formato de Mensajes WebSocket

Este documento define el formato de los mensajes JSON que se intercambian entre el servidor FastAPI y los nodos ESP32 a través de WebSocket.

## 🔐 Validación de Device ID

**IMPORTANTE**: Todos los mensajes enviados desde el servidor hacia los nodos ESP32 **DEBEN** incluir el campo `device_id` para especificar el destinatario.

El ESP32 **validará** que el mensaje está destinado a él comparando el `device_id` recibido con su propio identificador. Si no coincide, el mensaje será ignorado.

---

## 📤 Mensajes del Servidor → ESP32

### 1. Actualizar Relé 1 (Calefacción)

```json
{
  "tipo": "actualizacion_relay1",
  "device_id": "ESP32_AULA_A101",
  "relay": true
}
```

**Campos:**
- `tipo`: `"actualizacion_relay1"`
- `device_id`: ID del nodo destinatario (obligatorio)
- `relay`: `true` para encender, `false` para apagar

---

### 2. Actualizar Relé 2 (Iluminación)

```json
{
  "tipo": "actualizacion_relay2",
  "device_id": "ESP32_AULA_A101",
  "relay": false
}
```

**Campos:**
- `tipo`: `"actualizacion_relay2"`
- `device_id`: ID del nodo destinatario (obligatorio)
- `relay`: `true` para encender, `false` para apagar

---

### 3. Configurar Aula (Panel Admin)

```json
{
  "tipo": "configurar_aula",
  "device_id": "ESP32_AULA_A101",
  "data": {
    "nombre": "Aula A-101",
    "edificio": "Edificio A",
    "planta": 1,
    "capacidad": 30,
    "calefaccion": true,
    "iluminacion": true
  }
}
```

**Campos:**
- `tipo`: `"configurar_aula"`
- `device_id`: ID del nodo destinatario (obligatorio)
- `data`: Objeto con configuración del aula
  - `nombre`: Nombre del aula
  - `edificio`: Edificio donde está ubicada
  - `planta`: Número de planta
  - `capacidad`: Aforo máximo
  - `calefaccion`: Habilitación del control de calefacción
  - `iluminacion`: Habilitación del control de iluminación

---

### 4. Resetear Nodo (Comando Admin)

```json
{
  "tipo": "resetear_nodo",
  "device_id": "ESP32_AULA_A101"
}
```

**Campos:**
- `tipo`: `"resetear_nodo"`
- `device_id`: ID del nodo a resetear (obligatorio)

**Comportamiento ESP32:**
1. Envía confirmación al servidor
2. Espera 500ms
3. Ejecuta `ESP.restart()`

---

### 5. Test de Conexión (Comando Admin)

```json
{
  "tipo": "test_conexion",
  "device_id": "ESP32_AULA_A101"
}
```

**Campos:**
- `tipo`: `"test_conexion"`
- `device_id`: ID del nodo a testear (obligatorio)

**Respuesta ESP32:** Ver sección de mensajes ESP32 → Servidor

---

### 6. Mensajes Broadcast (Sin device_id)

Los mensajes que **NO** incluyan el campo `device_id` se consideran **broadcasts** y serán procesados por todos los nodos conectados.

```json
{
  "tipo": "estado_inicial",
  "data": {
    "timestamp": "2025-11-06T10:30:00Z"
  }
}
```

---

## 📥 Mensajes del ESP32 → Servidor

### 1. Confirmación de Reset

```json
{
  "tipo": "reset_confirmado",
  "device_id": "ESP32_AULA_A101"
}
```

Enviado **antes** de ejecutar el reinicio del nodo.

---

### 2. Respuesta de Test de Conexión

```json
{
  "tipo": "test_respuesta",
  "device_id": "ESP32_AULA_A101",
  "estado": "online",
  "wifi_rssi": -52,
  "uptime": 3600,
  "free_heap": 215648
}
```

**Campos:**
- `tipo`: `"test_respuesta"`
- `device_id`: ID del nodo (obligatorio)
- `estado`: Siempre `"online"` si el nodo responde
- `wifi_rssi`: Intensidad de señal WiFi (dBm)
- `uptime`: Segundos desde el último boot
- `free_heap`: Memoria RAM libre (bytes)

---

### 3. Confirmación de Configuración

```json
{
  "tipo": "config_confirmada",
  "device_id": "ESP32_AULA_A101"
}
```

Enviado después de actualizar la configuración del aula.

---

### 4. Registro de Asistencia

```json
{
  "tipo": "asistencia",
  "device_id": "ESP32_AULA_A101",
  "uid": "A1B2C3D4",
  "timestamp": "2025-11-06T10:30:15Z"
}
```

**Campos:**
- `tipo`: `"asistencia"`
- `device_id`: ID del nodo (obligatorio)
- `uid`: UID de la tarjeta NFC leída
- `timestamp`: Fecha y hora de la lectura (ISO 8601)

---

### 5. Envío de Valores de Sensores

```json
{
  "tipo": "sensores",
  "device_id": "ESP32_AULA_A101",
  "temperatura": 22.5,
  "humedad": 45.2,
  "luz": 450,
  "personas": 15,
  "timestamp": "2025-11-06T10:30:00Z"
}
```

**Campos:**
- `tipo`: `"sensores"`
- `device_id`: ID del nodo (obligatorio)
- `temperatura`: Temperatura en °C (BME280)
- `humedad`: Humedad relativa en % (BME280)
- `luz`: Iluminación en lux (BH1750)
- `personas`: Cantidad detectada por radar (LD2410)
- `timestamp`: Fecha y hora de la lectura (ISO 8601)

---

## 🔄 Flujo de Validación en ESP32

```cpp
// 1. Parsear JSON
StaticJsonDocument<512> doc;
deserializeJson(doc, payload);

// 2. Validar device_id
if (doc.containsKey("device_id")) {
    String targetDeviceId = doc["device_id"].as<String>();
    
    if (targetDeviceId != deviceId) {
        // Mensaje no es para este nodo, ignorar
        return;
    }
    
    // Mensaje confirmado para este nodo, procesar
}

// 3. Procesar según tipo
String tipo = doc["tipo"].as<String>();
if (tipo == "actualizacion_relay1") {
    // ...
}
```

---

## 🛡️ Seguridad

### Recomendaciones:

1. **Siempre incluir `device_id`** en mensajes unicast (servidor → nodo específico)
2. **Validar JWT** en la conexión WebSocket inicial
3. **Usar WSS** (WebSocket Secure) en producción
4. **Limitar broadcasts** para evitar procesamiento innecesario en todos los nodos
5. **Validar campos obligatorios** antes de procesar acciones críticas

---

## 📊 Ejemplo de Implementación Backend

### FastAPI - Enviar comando a nodo específico

```python
from utils.websocket_manager import websocket_manager

async def enviar_comando_a_nodo(device_id: str, tipo: str, data: dict = None):
    """
    Envía un comando WebSocket a un nodo ESP32 específico.
    """
    mensaje = {
        "tipo": tipo,
        "device_id": device_id
    }
    
    if data:
        mensaje["data"] = data
    
    # Enviar solo al nodo específico
    await websocket_manager.send_to_device(device_id, mensaje)
```

### Uso desde el panel admin:

```python
# Actualizar configuración
await enviar_comando_a_nodo(
    device_id="ESP32_AULA_A101",
    tipo="configurar_aula",
    data={
        "nombre": "Aula A-101",
        "capacidad": 30,
        "calefaccion": True
    }
)

# Resetear nodo
await enviar_comando_a_nodo(
    device_id="ESP32_AULA_A101",
    tipo="resetear_nodo"
)
```

---

## ✅ Checklist de Implementación

- [x] ESP32 valida `device_id` en mensajes recibidos
- [x] ESP32 responde a comandos admin (reset, test)
- [x] ESP32 confirma configuración recibida
- [ ] Backend implementa `send_to_device()` en WebSocketManager
- [ ] Panel admin envía comandos con `device_id` correcto
- [ ] Backend valida que `device_id` existe antes de enviar mensajes
- [ ] Logs de seguridad para mensajes rechazados por `device_id`

---

**Última actualización:** 6 de noviembre de 2025
