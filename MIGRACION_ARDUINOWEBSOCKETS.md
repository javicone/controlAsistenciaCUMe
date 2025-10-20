# 🔄 MIGRACIÓN A ArduinoWebsockets

## 📋 RESUMEN DE CAMBIOS

Se ha migrado de la librería `WebSocketsClient` a `ArduinoWebsockets` para mejorar el soporte de WebSocket Seguro (WSS).

---

## 🆚 DIFERENCIAS PRINCIPALES

### **Librería Anterior: WebSocketsClient**

```cpp
#include <WebSocketsClient.h>

WebSocketsClient webSocket;

// Conectar
webSocket.beginSSL(wsHost, wsPort, wsPath, server_certificate);
webSocket.setInsecure(); // Para desactivar validación
webSocket.onEvent(webSocketEvent);
webSocket.setReconnectInterval(5000);

// Loop
void loop() {
  webSocket.loop();
}

// Enviar
webSocket.sendTXT(mensaje);

// Verificar conexión
webSocket.isConnected()

// Evento (callback complejo)
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_CONNECTED: ...
    case WStype_DISCONNECTED: ...
    case WStype_TEXT: ...
  }
}
```

### **Librería Nueva: ArduinoWebsockets**

```cpp
#include <ArduinoWebsockets.h>

using namespace websockets;
WebsocketsClient wsClient;

// Conectar
wsClient.onMessage(onMessageCallback);
wsClient.onEvent(onEventsCallback);
wsClient.setCACert(server_certificate);
bool connected = wsClient.connect(wss_server); // URL completa

// Loop
void loop() {
  if(wsClient.available()) {
    wsClient.poll();
  }
}

// Enviar
wsClient.send(mensaje);

// Verificar conexión
wsClient.available()

// Callbacks (más simples y claros)
void onMessageCallback(WebsocketsMessage message) {
  Serial.println(message.data());
}

void onEventsCallback(WebsocketsEvent event, String data) {
  if(event == WebsocketsEvent::ConnectionOpened) {
    // Conectado
  }
}
```

---

## ✅ VENTAJAS DE ArduinoWebsockets

1. **✅ Mejor soporte WSS** - Manejo nativo de certificados SSL/TLS
2. **✅ API más moderna** - Callbacks separados para mensajes y eventos
3. **✅ Menos memoria** - Implementación más eficiente
4. **✅ Más estable** - Menos problemas de reconexión
5. **✅ URL completa** - Más fácil de configurar (`wss://host:port/path`)
6. **✅ Mejor documentación** - Más ejemplos y comunidad activa

---

## 📝 CAMBIOS REALIZADOS EN TU CÓDIGO

### **1. config.h**

**ANTES:**
```cpp
const char* wsHost = "10.25.186.94";
const int wsPort = 5000;
const char* wsPath = "/ws";
```

**AHORA:**
```cpp
const char* wss_server = "wss://10.25.186.94:5000/ws";  // ✅ URL completa
// (wsHost, wsPort, wsPath se mantienen para funciones HTTP)
```

---

### **2. Device_ESP32_app.ino**

**ANTES:**
```cpp
#include <WebSocketsClient.h>
WebSocketsClient webSocket;

webSocket.beginSSL(wsHost, wsPort, wsPath);
webSocket.setInsecure();
webSocket.onEvent(webSocketEvent);

for(;;) {
  webSocket.loop();
  vTaskDelay(10);
}
```

**AHORA:**
```cpp
#include <ArduinoWebsockets.h>
using namespace websockets;
WebsocketsClient wsClient;

wsClient.onMessage(onMessageCallback);
wsClient.onEvent(onEventsCallback);
wsClient.setCACert(server_certificate);
bool connected = wsClient.connect(wss_server);

for(;;) {
  if(wsClient.available()) {
    wsClient.poll();
  }
  vTaskDelay(10);
}
```

---

### **3. webSocketEvent.ino**

**ANTES:**
```cpp
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_CONNECTED:
      webSocket.sendTXT(mensaje);
      break;
    case WStype_TEXT:
      deserializeJson(doc, (char*)payload, length);
      break;
  }
}
```

**AHORA:**
```cpp
void onMessageCallback(WebsocketsMessage message) {
  Serial.println(message.data());
  deserializeJson(doc, message.data());
  // Procesar JSON...
}

void onEventsCallback(WebsocketsEvent event, String data) {
  if(event == WebsocketsEvent::ConnectionOpened) {
    wsClient.send(mensaje);
  }
  else if(event == WebsocketsEvent::ConnectionClosed) {
    // Reconectar...
  }
}
```

---

### **4. api_rest.ino**

**ANTES:**
```cpp
if (!webSocket.isConnected()) {
  return;
}
webSocket.sendTXT(payload);
```

**AHORA:**
```cpp
if (!wsClient.available()) {
  return;
}
wsClient.send(payload);
```

---

## 🔧 INSTALACIÓN DE LA LIBRERÍA

### **Arduino IDE:**
1. Ir a **Sketch → Include Library → Manage Libraries**
2. Buscar **"ArduinoWebsockets"** por **Gil Maimon**
3. Instalar la versión más reciente

### **PlatformIO:**
Añadir en `platformio.ini`:
```ini
lib_deps = 
    gilmaimon/ArduinoWebsockets @ ^0.5.3
```

### **Verificar instalación:**
```cpp
#include <ArduinoWebsockets.h>
// Si compila sin errores, está instalada
```

---

## 🧪 PRUEBAS

### **1. Verificar conexión:**
```
🔐 Configurando WebSocket Seguro (WSS)...
🌐 Servidor: wss://10.25.186.94:5000/ws
🔌 Intentando conectar a WSS...
✅ Conectado exitosamente a WSS!
📤 Mensaje de identificación enviado
🔔 [WebSocket] Evento: ConnectionOpened
✅ Conexión WSS establecida exitosamente!
```

### **2. Recibir mensajes:**
```
📩 [WebSocket] Mensaje recibido
📜 Longitud: 45
📥 Contenido: {"tipo":"estado_inicial","data":{}}
📦 Estado inicial del servidor recibido
```

### **3. Enviar datos:**
```
Temperature = 23.45 *C
Light: 450 lx
📤 Enviando datos aula: {"tipo":"datos_aula","aula":"Aula 101",...}
✅ Datos enviados por WebSocket
```

---

## 🐛 TROUBLESHOOTING

### **Error: "ArduinoWebsockets.h: No such file"**
**Solución:** Instalar la librería (ver sección Instalación)

### **Error: "WebsocketsClient was not declared"**
**Solución:** Añadir `using namespace websockets;` después del include

### **No conecta (sin errores)**
**Solución:** 
- Verificar que `wss_server` tenga el formato correcto: `wss://IP:PUERTO/PATH`
- Verificar certificado SSL coincide con el servidor
- Probar sin certificado temporalmente (comentar `setCACert()`)

### **Se desconecta constantemente**
**Solución:**
- Verificar que `wsClient.poll()` se ejecuta regularmente
- Aumentar intervalo de ping: `wsClient.ping()`
- Verificar memoria disponible: `ESP.getFreeHeap()`

---

## 📊 COMPARACIÓN DE RENDIMIENTO

| Métrica | WebSocketsClient | ArduinoWebsockets |
|---------|------------------|-------------------|
| **Memoria RAM** | ~12 KB | ~8 KB |
| **Conexión SSL** | Compleja | Simple |
| **Reconexión** | Manual | Más fácil |
| **API** | Callback único | Callbacks separados |
| **Documentación** | Limitada | Completa |

---

## 🔒 SEGURIDAD

### **Validación de certificado (Producción):**
```cpp
wsClient.setCACert(server_certificate);  // ✅ USAR SIEMPRE
bool connected = wsClient.connect(wss_server);
```

### **Sin validación (Solo DEBUG):**
```cpp
// NO usar setCACert() - acepta cualquier certificado
// ⚠️ INSEGURO - Solo para desarrollo
bool connected = wsClient.connect(wss_server);
```

---

## 📚 RECURSOS

- **GitHub oficial:** https://github.com/gilmaimon/ArduinoWebsockets
- **Ejemplos:** https://github.com/gilmaimon/ArduinoWebsockets/tree/master/examples
- **Documentación API:** https://github.com/gilmaimon/ArduinoWebsockets/wiki

---

## ✅ CHECKLIST POST-MIGRACIÓN

- [ ] Librería `ArduinoWebsockets` instalada
- [ ] Código compilado sin errores
- [ ] ESP32 conecta a WSS exitosamente
- [ ] Mensajes se reciben correctamente
- [ ] Mensajes se envían correctamente
- [ ] Relay responde a comandos del servidor
- [ ] Datos de sensores llegan al servidor cada 30s
- [ ] Reconexión automática funciona
- [ ] Certificado SSL validado (producción)

---

## 🎯 PRÓXIMOS PASOS

1. **Compilar y subir** el código actualizado al ESP32
2. **Verificar logs** en Serial Monitor (115200 baud)
3. **Confirmar conexión WSS** (debe mostrar "ConnectionOpened")
4. **Probar envío de datos** (temperatura, luz cada 30s)
5. **Probar control relay** desde el servidor/frontend
6. **Si funciona:** Habilitar validación de certificado para producción
7. **Documentar** cualquier cambio adicional necesario

---

¿Necesitas ayuda con algún paso específico? 🚀
