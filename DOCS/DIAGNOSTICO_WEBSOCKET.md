# 🔍 DIAGNÓSTICO: WebSocket no recibe datos

## ❌ PROBLEMA ACTUAL
El servidor no recibe mensajes del ESP32 después de los cambios.

---

## 🧪 PASOS DE DIAGNÓSTICO

### **1. VERIFICAR SI EL ESP32 SE CONECTA**

#### En el **Serial Monitor del ESP32** (115200 baud), debes ver:

```
Conectando a WiFi... Conectado!
Hora sincronizada: ...
🔐 Iniciando WebSocket con SSL...
🌐 Host: 10.25.186.94
🔢 Puerto: 5000
📍 Path: /ws
✅ WebSocket configurado.
📩 [WebSocketEvent] Tipo: 2
📥 Mensaje recibido: /ws
✅ WebSocket conectado
📤 Mensaje de conexión enviado
```

#### En el **servidor FastAPI**, debes ver:

```
🔌 Nueva conexión WebSocket desde: 10.x.x.x
✅ WebSocket conectado y añadido al manager
📤 Estado inicial enviado a 10.x.x.x
📩 Mensaje recibido por WS: {"tipo":"conexion","aula":"Aula 101","dispositivo":"ESP32"}
✅ ESP32 conectado desde Aula 101
```

---

### **2. SI NO SE CONECTA (Tipo: 0 = DISCONNECTED)**

#### **CAUSA: Problema con certificado SSL**

**SOLUCIÓN TEMPORAL (SOLO DEBUG):**

En `Device_ESP32_app.ino` línea ~100, **CAMBIA**:

```cpp
// COMENTAR ESTA LÍNEA:
// webSocket.beginSSL(wsHost, wsPort, wsPath, server_certificate);

// DESCOMENTAR ESTAS DOS:
webSocket.beginSSL(wsHost, wsPort, wsPath);
webSocket.setInsecure(); // ⚠️ Desactiva validación SSL temporalmente
```

**Si esto funciona**, el problema es el certificado. **Solución permanente:**

1. **Regenerar certificados** en el servidor:
   ```bash
   cd d:\UEX\ControlAsistencia\Server
   openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365
   ```

2. **Copiar el contenido de `cert.pem`** al archivo `config.h` del ESP32:
   ```cpp
   const char* server_certificate = \
   "-----BEGIN CERTIFICATE-----\n" \
   "... TODO EL CONTENIDO DEL CERT.PEM ...\n" \
   "-----END CERTIFICATE-----\n";
   ```

3. **Recompilar y subir** al ESP32

4. **Quitar el `setInsecure()`** y volver a usar:
   ```cpp
   webSocket.beginSSL(wsHost, wsPort, wsPath, server_certificate);
   ```

---

### **3. SI SE CONECTA PERO NO ENVÍA DATOS**

#### **Verificar que `EnviaValoresAula()` se llama**

En el **Serial Monitor**, cada 30 segundos debes ver:

```
Temperature = 23.45 *C
Light: 450 lx
📤 Datos de aula enviados por WebSocket
```

#### **Si NO se llama**, verifica:

1. **Sensores BME280 y BH1750 funcionan**:
   ```cpp
   // En initSensores() debe tener:
   if (!bme.begin(0x76)) {
     Serial.println("❌ Error: BME280 no encontrado");
   }
   if (!lightMeter.begin()) {
     Serial.println("❌ Error: BH1750 no encontrado");
   }
   ```

2. **Variables `delayTime` y `lastReading2` existen** en `globals.h`:
   ```cpp
   unsigned long lastReading2 = 0;
   unsigned long delayTime = 30000; // 30 segundos
   ```

3. **El loop principal se ejecuta** (añadir debug):
   ```cpp
   void loop() {
     // Añadir al inicio:
     static unsigned long lastDebug = 0;
     if (millis() - lastDebug > 5000) {
       Serial.println("🔄 Loop ejecutándose...");
       lastDebug = millis();
     }
     
     // ... resto del código
   }
   ```

---

### **4. SI ENVÍA PERO SERVIDOR NO RECIBE**

#### **Problema posible: WebSocket no está conectado cuando envía**

**SOLUCIÓN:** Verificar conexión antes de enviar en `api_rest.ino`:

```cpp
void EnviaValoresAula() {
  temperatura = bme.readTemperature();
  iluminacion = lightMeter.readLightLevel();
  
  // ✅ VERIFICAR ESTADO DEL WEBSOCKET
  if (!webSocket.isConnected()) {
    Serial.println("⚠️ WebSocket no conectado, omitiendo envío");
    return;
  }
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi desconectado, omitiendo envío");
    return;
  }
  
  StaticJsonDocument<256> doc;
  doc["tipo"] = "datos_aula";
  doc["aula"] = aula;
  doc["temperatura"] = temperatura;
  doc["luz"] = iluminacion;
  doc["personas"] = personas;
  doc["clase_en_curso"] = clase_en_curso;

  String payload;
  serializeJson(doc, payload);
  
  Serial.print("📤 Enviando: "); Serial.println(payload); // ← DEBUG
  webSocket.sendTXT(payload);
  Serial.println("✅ Datos enviados");
}
```

---

### **5. VERIFICAR ESTRUCTURA DEL MENSAJE JSON**

**Test manual desde ESP32:**

Añade esta función de prueba en `api_rest.ino`:

```cpp
void testEnviarMensaje() {
  StaticJsonDocument<128> doc;
  doc["tipo"] = "test";
  doc["mensaje"] = "Hola desde ESP32";
  
  String payload;
  serializeJson(doc, payload);
  
  Serial.print("🧪 Test enviando: "); Serial.println(payload);
  webSocket.sendTXT(payload);
}
```

Llámala en `setup()` después de conectar el WebSocket:

```cpp
void HiloComunicadorcode(void* pvParameters) {
  // ... WiFi, NTP, WebSocket ...
  
  delay(2000); // Esperar 2s a que conecte
  testEnviarMensaje(); // ← TEST
  
  for(;;) {
    webSocket.loop();
    vTaskDelay(10);
  }
}
```

**Debes ver en el servidor:**
```
📩 Mensaje recibido por WS: {"tipo":"test","mensaje":"Hola desde ESP32"}
```

---

## 🔧 SOLUCIÓN RÁPIDA (SI NADA FUNCIONA)

### **Volver al HTTP POST temporalmente**

Si necesitas que funcione YA mientras debugueas el WebSocket:

En `api_rest.ino`, **comenta la versión WebSocket** y **descomenta la HTTP**:

```cpp
void EnviaValoresAula() {
  temperatura = bme.readTemperature();
  iluminacion = lightMeter.readLightLevel();
  
  // VERSIÓN HTTP (funciona siempre):
  WiFiClientSecure *client = new WiFiClientSecure();
  client->setCACert(server_certificate);
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient https;
    https.begin(*client, String(serverUrl) + "/datos_aula");
    https.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<200> doc;
    doc["aula"] = aula;
    doc["temperatura"] = temperatura;
    doc["luz"] = iluminacion;
    doc["personas"] = personas;
    doc["clase_en_curso"] = clase_en_curso;
    
    String payload;
    serializeJson(doc, payload);
    
    int httpResponseCode = https.POST(payload);
    Serial.print("📡 HTTP POST: "); Serial.println(httpResponseCode);
    
    https.end();
    delete client;
  }
  
  // VERSIÓN WEBSOCKET (debuguear primero):
  /*
  if (webSocket.isConnected()) {
    StaticJsonDocument<256> doc;
    doc["tipo"] = "datos_aula";
    // ... resto del código WebSocket
  }
  */
}
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] ESP32 se conecta a WiFi correctamente
- [ ] NTP sincroniza la hora
- [ ] WebSocket muestra "Tipo: 2" (CONNECTED) en el Serial Monitor
- [ ] ESP32 envía mensaje de conexión (JSON con "tipo":"conexion")
- [ ] Servidor FastAPI recibe el mensaje de conexión
- [ ] `EnviaValoresAula()` se ejecuta cada 30 segundos
- [ ] Sensores BME280 y BH1750 leen datos correctamente
- [ ] WebSocket está conectado (`webSocket.isConnected() == true`)
- [ ] Servidor recibe mensajes con "tipo":"datos_aula"

---

## 🆘 SI TODO FALLA

**Entra en el Discord/Foro del proyecto con:**

1. **Logs completos del Serial Monitor** (desde boot hasta error)
2. **Logs del servidor FastAPI** (consola completa)
3. **Versión de la librería `WebSocketsClient`** (ver en PlatformIO/Arduino IDE)
4. **Resultado de `ping 10.25.186.94`** desde el ordenador del ESP32

---

## 📞 CONTACTO RÁPIDO

Si necesitas ayuda inmediata, proporciona:

```
Serial Monitor: [PEGAR AQUÍ]
Servidor logs: [PEGAR AQUÍ]
IP ESP32: [IP]
IP Servidor: [IP]
Red: [Misma red? Sí/No]
```
