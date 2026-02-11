# 🏗️ Arquitectura WebSocket - Sistema de Control de Asistencia

## 📊 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WebSocket Manager (Singleton)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  • device_connections: Dict[str, WebSocket]                              │
│    └─> Mapeo de device_id → WebSocket (ESP32 nodes)                     │
│                                                                           │
│  • admin_websockets: List[WebSocket]                                     │
│    └─> Lista de conexiones WebSocket de administradores                 │
│                                                                           │
│  • conserje_websockets: List[WebSocket]                                  │
│    └─> Lista de conexiones WebSocket de conserjes                       │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│   ESP32 Devices      │    │   Administradores    │    │     Conserjes        │
│   (Nodos IoT)        │    │   (Control Total)    │    │   (Control Parcial)  │
└──────────────────────┘    └──────────────────────┘    └──────────────────────┘
         │                            │                            │
         │ JWT scope="device"         │ JWT scope="admin"         │ JWT scope="conserje"
         │                            │                            │
         ▼                            ▼                            ▼
  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐
  │   /ws       │            │  /ws/admin  │            │ /ws/conserje│
  └─────────────┘            └─────────────┘            └─────────────┘
         │                            │                            │
         └────────────────────────────┴────────────────────────────┘
                                      │
                                      ▼
                        ┌──────────────────────────────┐
                        │   Connection Manager         │
                        │   - connect()                │
                        │   - disconnect()             │
                        │   - send_to_device()         │
                        │   - notify_admins()          │
                        │   - notify_conserjes()       │
                        │   - notify_staff()           │
                        │   - broadcast()              │
                        └──────────────────────────────┘
```

---

## 🔐 Matriz de Permisos por Rol

| Acción                        | 🔧 Admin | 👷 Conserje | 📟 Device |
|-------------------------------|----------|-------------|-----------|
| **Ver estado de aulas**       | ✅       | ✅          | ❌        |
| **Recibir actualizaciones RT**| ✅       | ✅          | ❌        |
| **Toggle relay (calefacción)**| ✅       | ✅*         | ❌        |
| **Toggle relay (luces)**      | ✅       | ✅*         | ❌        |
| **Configurar aula**           | ✅       | ❌          | ❌        |
| **Resetear nodo**             | ✅       | ❌          | ❌        |
| **Test de conexión**          | ✅       | ❌          | ❌        |
| **Listar dispositivos**       | ✅       | ✅          | ❌        |
| **Enviar datos sensores**     | ❌       | ❌          | ✅        |
| **Recibir comandos**          | ❌       | ❌          | ✅        |

\* *Sujeto a habilitación por admin (puede implementarse validación adicional)*

---

## 📡 Endpoints WebSocket

### 1️⃣ `/ws` - ESP32 Devices
**Autenticación:** JWT con `scope="device"`, `sub=device_id`

**Mensajes que ENVÍA (device → server):**
```json
// Conexión inicial
{ "tipo": "conexion", "aula": "Aula A-101" }

// Datos de sensores (periódico)
{
  "tipo": "datos_aula",
  "aula": "Aula A-101",
  "temperatura": 22.5,
  "humedad": 45,
  "luz": 450,
  "personas": 15,
  "clase_en_curso": true,
  "relay1": true,
  "relay2": false
}

// Respuesta a test de conexión
{
  "tipo": "test_respuesta",
  "device_id": "ESP32_AULA_A101",
  "estado": "online",
  "wifi_rssi": -45,
  "uptime": 3600,
  "free_heap": 123456
}

// Confirmación de reset
{ "tipo": "reset_confirmado", "device_id": "ESP32_AULA_A101" }

// Confirmación de configuración
{ "tipo": "config_confirmada", "device_id": "ESP32_AULA_A101" }

// Ping/Pong para keep-alive
{ "tipo": "ping" }
```

**Mensajes que RECIBE (server → device):**
```json
// Estado inicial (al conectar)
{
  "welcome": true,
  "device_id": "ESP32_AULA_A101",
  "tipo": "estado_inicial",
  "data": { ... }
}

// Control de relés
{
  "tipo": "actualizacion_relay1",
  "device_id": "ESP32_AULA_A101",
  "relay": true
}

// Configurar aula
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

// Resetear nodo
{ "tipo": "resetear_nodo", "device_id": "ESP32_AULA_A101" }

// Test de conexión
{ "tipo": "test_conexion", "device_id": "ESP32_AULA_A101" }

// Pong
{ "tipo": "pong" }
```

---

### 2️⃣ `/ws/admin` - Administradores
**Autenticación:** JWT con `scope="admin"`, `sub=email`

**Mensajes que ENVÍA (admin → server):**
```json
// Actualizar configuración de aula
{
  "action": "actualizar_config",
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

// Resetear nodo
{
  "action": "resetear_nodo",
  "device_id": "ESP32_AULA_A101"
}

// Test de conexión
{
  "action": "test_conexion",
  "device_id": "ESP32_AULA_A101"
}

// Toggle relay
{
  "action": "toggle_relay",
  "device_id": "ESP32_AULA_A101",
  "relay_num": 1,
  "relay_state": true
}

// Listar dispositivos conectados
{ "action": "listar_dispositivos" }
```

**Mensajes que RECIBE (server → admin):**
```json
// Bienvenida (al conectar)
{
  "tipo": "admin_bienvenida",
  "dispositivos_conectados": ["ESP32_AULA_A101", "ESP32_LAB_C105"],
  "aulas_estado": { ... }
}

// Confirmación de comando enviado
{
  "tipo": "comando_enviado",
  "accion": "resetear_nodo",
  "device_id": "ESP32_AULA_A101"
}

// Error
{
  "tipo": "error",
  "mensaje": "Dispositivo no conectado"
}

// Actualizaciones en tiempo real de aulas
{
  "tipo": "actualizacion_aula",
  "aula": "Aula A-101",
  "temperatura": 22.5,
  "personas": 15,
  ...
}

// Respuesta de test de conexión (desde ESP32)
{
  "tipo": "test_respuesta",
  "device_id": "ESP32_AULA_A101",
  "estado": "online",
  "wifi_rssi": -45,
  ...
}

// Confirmaciones de ESP32
{ "tipo": "reset_confirmado", "device_id": "..." }
{ "tipo": "config_confirmada", "device_id": "..." }
```

---

### 3️⃣ `/ws/conserje` - Conserjes
**Autenticación:** JWT con `scope="conserje"`, `sub=email`

**Mensajes que ENVÍA (conserje → server):**
```json
// Toggle relay (calefacción/luces)
{
  "action": "toggle_relay",
  "device_id": "ESP32_AULA_A101",
  "relay_num": 1,
  "relay_state": true
}

// Listar dispositivos conectados
{ "action": "listar_dispositivos" }
```

**Mensajes que RECIBE (server → conserje):**
```json
// Bienvenida (al conectar)
{
  "tipo": "conserje_bienvenida",
  "dispositivos_conectados": ["ESP32_AULA_A101", "ESP32_LAB_C105"],
  "aulas_estado": { ... }
}

// Confirmación de comando enviado
{
  "tipo": "comando_enviado",
  "accion": "toggle_relay",
  "device_id": "ESP32_AULA_A101"
}

// Error (comando no permitido o dispositivo no conectado)
{
  "tipo": "error",
  "mensaje": "Acción no permitida para conserjes"
}

// Actualizaciones en tiempo real de aulas
{
  "tipo": "actualizacion_aula",
  "aula": "Aula A-101",
  "temperatura": 22.5,
  "personas": 15,
  "relay1": true,
  "relay2": false,
  ...
}

// Lista de dispositivos
{
  "tipo": "lista_dispositivos",
  "dispositivos_conectados": [...],
  "aulas_estado": { ... }
}
```

---

## 🔄 Flujos de Comunicación

### 📤 Flujo 1: Admin cambia configuración de aula
```
Admin Panel (JS)
  → enviarComando("actualizar_config", "ESP32_AULA_A101", {...config})
    → WS /ws/admin
      → manager.send_to_device("ESP32_AULA_A101", {tipo: "configurar_aula", ...})
        → ESP32 webSocketEvent()
          → Valida device_id ✅
          → Aplica configuración
          → Responde {tipo: "config_confirmada", device_id: "..."}
        ← manager.notify_admins({tipo: "config_confirmada", ...})
      ← Admin recibe confirmación
```

### 📤 Flujo 2: Conserje enciende calefacción
```
Conserje Panel (JS)
  → cambiarRelay("Aula A-101", 1, true)
    → WS /ws/conserje
      → manager.send_to_device("ESP32_AULA_A101", {tipo: "actualizacion_relay1", relay: true})
        → ESP32 webSocketEvent()
          → Valida device_id ✅
          → digitalWrite(relayPin1, HIGH)
        ← manager.broadcast({tipo: "actualizacion_aula", aula: "...", relay1: true})
      ← Conserje recibe actualización
      ← Admin también recibe actualización
```

### 📤 Flujo 3: ESP32 envía datos de sensores
```
ESP32 (loop principal)
  → Envía cada 30s: {tipo: "datos_aula", temperatura: 22.5, ...}
    → WS /ws
      → actualizar_estado_aula(aula, datos)
      → manager.broadcast({tipo: "actualizacion_aula", aula: "...", ...})
        ← Admin recibe actualización
        ← Conserje recibe actualización
```

---

## 🛠️ Métodos del ConnectionManager

### `connect(websocket, client_type, client_id=None)`
Registra una nueva conexión WebSocket según su tipo:
- `client_type="device"` → Añade a `device_connections[client_id]`
- `client_type="admin"` → Añade a `admin_websockets`
- `client_type="conserje"` → Añade a `conserje_websockets`

### `disconnect(websocket, client_id=None)`
Desconecta y limpia la conexión de las listas correspondientes.

### `send_to_device(device_id, message) → bool`
Envía mensaje a un dispositivo ESP32 específico. Retorna `True` si se envió correctamente.

### `notify_admins(message)`
Envía mensaje solo a todos los administradores conectados.

### `notify_conserjes(message)`
Envía mensaje solo a todos los conserjes conectados.

### `notify_staff(message)`
Envía mensaje a **todos** los usuarios staff (admins + conserjes).

### `broadcast(message)`
Envía mensaje a **todos** los clientes (devices + admins + conserjes).

### `get_connected_devices() → List[str]`
Retorna lista de `device_id` de ESP32s conectados.

### `is_device_connected(device_id) → bool`
Verifica si un dispositivo específico está conectado.

---

## ⚙️ Validación de device_id en ESP32

El ESP32 **siempre valida** que los mensajes sean para él:

```cpp
if (doc.containsKey("device_id")) {
  String targetDeviceId = doc["device_id"].as<String>();
  
  if (targetDeviceId != deviceId) {
    Serial.println("⏭️ Mensaje no destinado a este nodo, ignorando.");
    return;  // Salir sin procesar
  }
  
  Serial.println("✅ Mensaje confirmado para este nodo");
}
```

Esto evita que un ESP32 ejecute comandos destinados a otro dispositivo.

---

## 🔒 Seguridad

### Autenticación JWT
- **Tokens firmados con RS256** (clave privada en `keys/jwt_priv.pem`)
- **Scopes diferenciados**: `device`, `admin`, `conserje`
- **Subject (`sub`)**: 
  - Devices: `device_id` (ej: `ESP32_AULA_A101`)
  - Users: `email` (ej: `admin@universidad.es`)

### Validación de permisos
- Endpoint `/ws/conserje` **rechaza** acciones administrativas:
  - ❌ `actualizar_config`
  - ❌ `resetear_nodo`
  - ❌ `test_conexion`
  - ✅ `toggle_relay` (permitido)
  - ✅ `listar_dispositivos` (permitido)

### Filtrado de notificaciones
- `test_respuesta`, `reset_confirmado`, `config_confirmada` → Solo a `admin_websockets`
- `actualizacion_aula` → A `admin_websockets` + `conserje_websockets` (vía `broadcast`)

---

## 📝 TODOs Pendientes

1. ✅ **Implementar scope="admin" y scope="conserje"** en generación de tokens JWT
2. ⚠️ **Validación de permisos para relés**: Añadir flag `relay_control_habilitado` que admin pueda toggle
3. ⚠️ **Rate limiting**: Evitar spam de comandos desde conserjes/admins
4. ⚠️ **Persistencia de configuración**: ESP32 debe guardar config en NVS al recibir `configurar_aula`
5. ⚠️ **Logs de auditoría**: Registrar quién (admin/conserje) realizó qué acción sobre qué dispositivo
6. ⚠️ **Heartbeat monitoring**: Detectar devices "zombies" que no responden a ping

---

## 🎯 Resumen

### Cambios Implementados
1. ✅ Añadido `conserje_websockets: List[WebSocket]` al `ConnectionManager`
2. ✅ Creado endpoint `/ws/conserje` con permisos restringidos
3. ✅ Métodos `notify_conserjes()` y `notify_staff()` para broadcast selectivo
4. ✅ JavaScript `conserjes.js` con WebSocket client y auto-reconnect
5. ✅ HTML actualizado con indicador de estado WS y botones de control
6. ✅ Validación de acciones: conserjes solo pueden `toggle_relay` y `listar_dispositivos`

### Arquitectura Final
- **3 tipos de clientes**: ESP32 devices, Admins, Conserjes
- **3 endpoints WebSocket**: `/ws`, `/ws/admin`, `/ws/conserje`
- **Routing inteligente**: `send_to_device()`, `notify_admins()`, `notify_conserjes()`, `notify_staff()`, `broadcast()`
- **Permisos granulares**: Admins control total, Conserjes solo relés + lectura
- **Actualizaciones en tiempo real**: Todos reciben cambios de estado de aulas

### Ventajas
- ✅ **Separación de responsabilidades**: Cada rol tiene su endpoint y permisos
- ✅ **Seguridad**: Validación de JWT con scopes, rechazo de acciones no autorizadas
- ✅ **Escalabilidad**: Listas/dicts simples, sin complejidad innecesaria
- ✅ **Tiempo real**: WebSocket bidireccional para todos los roles
- ✅ **Mantenibilidad**: Código limpio, sin over-engineering
