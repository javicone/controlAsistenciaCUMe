// Usamos Preferences para persistencia de configuración
#include <Preferences.h>

// Contador de intentos de reconexión fallidos
static int wsReconnectAttempts = 0;
const int MAX_RECONNECT_ATTEMPTS = 5;  // Después de 5 intentos, invalidar token

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  // ✅ Log inicial con timestamp
  unsigned long timestamp = millis();
  Serial.println("\n╔════════════════════════════════════╗");
  Serial.printf("║ 📩 WebSocket Event [%lu ms]\n", timestamp);
  Serial.println("╚════════════════════════════════════╝");
  
  Serial.printf("📌 Tipo de evento: %d", type);
  
  // ✅ Traducir tipo de evento a texto legible
  switch(type) {
    case WStype_DISCONNECTED: Serial.println(" (DISCONNECTED)"); break;
    case WStype_CONNECTED:    Serial.println(" (CONNECTED)"); break;
    case WStype_TEXT:         Serial.println(" (TEXT)"); break;
    case WStype_BIN:          Serial.println(" (BINARY)"); break;
    case WStype_PING:         Serial.println(" (PING)"); break;
    case WStype_PONG:         Serial.println(" (PONG)"); break;
    case WStype_ERROR:        Serial.println(" (ERROR)"); break;
    default:                  Serial.printf(" (UNKNOWN: %d)\n", type); break;
  }
  
  Serial.printf("📏 Longitud payload: %d bytes\n", length);
  
  // ✅ Mostrar payload en hexadecimal si es binario o muy corto
  if (length > 0 && length <= 64) {
    Serial.print("🔍 Payload (hex): ");
    for(size_t i = 0; i < length; i++) {
      if(payload[i] < 0x10) Serial.print("0");
      Serial.print(payload[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
  }
  
  // ✅ Mostrar payload como texto si es razonable
  if (type == WStype_TEXT && length > 0 && length < 1024) {
    Serial.println("📄 Payload (texto):");
    Serial.println("┌────────────────────────────────────┐");
    Serial.write(payload, length);
    Serial.println();
    Serial.println("└────────────────────────────────────┘");
  }

  switch (type) {
    case WStype_DISCONNECTED:
      {
        wsReconnectAttempts++;
        Serial.println("❌ WebSocket DESCONECTADO");
        Serial.printf("   WiFi estado: %s\n", WiFi.status() == WL_CONNECTED ? "Conectado" : "Desconectado");
        Serial.printf("   RSSI: %d dBm\n", WiFi.RSSI());
        Serial.printf("   IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("   Intento de reconexión: %d/%d\n", wsReconnectAttempts, MAX_RECONNECT_ATTEMPTS);
        
        wsConectado = false;
        
        // 🔍 DIAGNÓSTICO: Solo invalidar token después de varios intentos fallidos
        if (WiFi.status() == WL_CONNECTED) {
           if (wsReconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
              Serial.println("⚠️ Demasiados intentos fallidos - Invalidando token");
              invalidateToken();
              wsReconnectAttempts = 0;  // Reset contador
           } else {
              Serial.println("   Manteniendo token, reconexión automática en 5s...");
           }
        }
      }
      break;

    case WStype_CONNECTED:
      {
        Serial.println("✅ WebSocket CONECTADO");
        Serial.printf("   URL: %s\n", payload);  // La URL a la que se conectó
        Serial.printf("   Servidor: %s:%d\n", wsHost, wsPort);
        Serial.printf("   WiFi RSSI: %d dBm\n", WiFi.RSSI());
        Serial.printf("   Free heap: %d bytes\n", ESP.getFreeHeap());
        
        // Reset contador de reconexiones al conectar exitosamente
        wsReconnectAttempts = 0;
        wsConectado = true;
        
        // Enviar mensaje de vinculación al servidor
        StaticJsonDocument<200> hello;
        hello["tipo"] = "nodo_conectado";
        hello["device_id"] = deviceId;
        hello["aula"] = aula;
        hello["ip"] = WiFi.localIP().toString();
        hello["uptime"] = millis() / 1000;
        hello["relay1"] = relay1Estado;
        hello["relay2"] = relay2Estado;
        String helloMsg;
        serializeJson(hello, helloMsg);
        
        Serial.printf("📤 Enviando saludo: %s\n", helloMsg.c_str());
        webSocket.sendTXT(helloMsg);
      }
      break;

    case WStype_TEXT:
      {
        Serial.println("📨 Procesando mensaje de TEXTO");
        
        if (length == 0) {
          Serial.println("⚠️ Mensaje vacío, ignorando");
          return;
        }

        // Intentar parsear JSON
        StaticJsonDocument<512> doc;
        DeserializationError error = deserializeJson(doc, (char*)payload, length);

        if (error) {
          Serial.println("❌ ERROR al parsear JSON:");
          Serial.printf("   Código: %s\n", error.f_str());
          Serial.printf("   Longitud: %d bytes\n", length);
          Serial.println("   Contenido:");
          Serial.write(payload, min(length, (size_t)256));
          Serial.println();
          return;
        }
        
        Serial.println("✅ JSON parseado correctamente");
        
        // ✅ Log del JSON parseado (pretty print)
        Serial.println("📋 Contenido JSON:");
        serializeJsonPretty(doc, Serial);
        Serial.println();

        // Validación de device_id
        if (doc.containsKey("device_id")) {
          String targetDeviceId = doc["device_id"].as<String>();
          
          Serial.printf("🎯 Device ID destino: %s\n", targetDeviceId.c_str());
          Serial.printf("🆔 Este nodo: %s\n", deviceId.c_str());
          
          if (targetDeviceId != deviceId) {
            Serial.println("⏭️ Mensaje NO es para este nodo, IGNORANDO");
            return;
          }
          
          Serial.println("✅ Mensaje confirmado para ESTE nodo");
        } else {
          Serial.println("📢 Mensaje SIN device_id (broadcast)");
        }

        // Procesar tipo de mensaje
        if (!doc.containsKey("tipo")) {
          Serial.println("⚠️ JSON no contiene campo 'tipo', ignorando");
          return;
        }
        
        String tipoMensaje = doc["tipo"].as<String>();
        Serial.printf("📂 Tipo de mensaje: '%s'\n", tipoMensaje.c_str());
        // ✅ Verificar que el mensaje es para este dispositivo
        // ════════════════════════════════════════
        // RELAY 1
        // ════════════════════════════════════════
        // ✅ Manejar actualización de Relay 1 (Calefacción)
        if (tipoMensaje == "actualizacion_relay1") {
            bool relayState = doc["relay"];
            int relayNum = doc["relay_num"] | 1;
            
            Serial.println("╔════════════════════════════════════╗");
            Serial.println("║ 🔥 ACTUALIZACION RELAY 1           ║");
            Serial.println("╚════════════════════════════════════╝");
            Serial.printf("   Estado solicitado: %s\n", relayState ? "ON" : "OFF");
            Serial.printf("   Estado previo: %s\n", relay1Estado ? "ON" : "OFF");
            Serial.printf("   Pin: %d\n", RELAY_PIN_1);
            
            digitalWrite(RELAY_PIN_1, relayState ? HIGH : LOW);
            relay1Estado = relayState;
            
            Serial.printf("✅ Relay 1 aplicado: %s\n", relayState ? "ENCENDIDO" : "APAGADO");
            
            // Confirmar al servidor
            enviarConfirmacionRelay(1, relayState);
        }
        
        // ════════════════════════════════════════
        // RELAY 2
        // ════════════════════════════════════════
        // ✅ Manejar actualización de Relay 2 (Iluminación)
        else if (tipoMensaje == "actualizacion_relay2") {
            bool relayState = doc["relay"];
            int relayNum = doc["relay_num"] | 2;
            
            Serial.println("╔════════════════════════════════════╗");
            Serial.println("║ 💡 ACTUALIZACION RELAY 2           ║");
            Serial.println("╚════════════════════════════════════╝");
            Serial.printf("   Estado solicitado: %s\n", relayState ? "ON" : "OFF");
            Serial.printf("   Estado previo: %s\n", relay2Estado ? "ON" : "OFF");
            Serial.printf("   Pin: %d\n", RELAY_PIN_2);
            
            digitalWrite(RELAY_PIN_2, relayState ? HIGH : LOW);
            relay2Estado = relayState;

            Serial.printf("✅ Relay 2 aplicado: %s\n", relayState ? "ENCENDIDO" : "APAGADO");
            
            // Confirmar al servidor
            enviarConfirmacionRelay(2, relayState);
        }
        // Manejar mensaje genérico de relay (compatibilidad)
                else if (tipoMensaje == "actualizacion_relay") {
                    int relayNum = doc["relay_num"] | 1;
                    bool relayState = doc["relay"];
                    
                    if (relayNum == 1) {
                        digitalWrite(RELAY_PIN_1, relayState ? HIGH : LOW);
                        relay1Estado = relayState;
                    } else if (relayNum == 2) {
                        digitalWrite(RELAY_PIN_2, relayState ? HIGH : LOW);
                        relay2Estado = relayState;
                    }
                    
                    enviarConfirmacionRelay(relayNum, relayState);
                }
        // ════════════════════════════════════════
        // RESET NODO
        // ════════════════════════════════════════
        else if (tipoMensaje == "resetear_nodo") {
          Serial.println("🔄 Comando RESET recibido");
          
          // Enviar confirmación
          StaticJsonDocument<128> respuesta;
          respuesta["tipo"] = "reset_confirmado";
          respuesta["device_id"] = deviceId;
          String jsonStr;
          serializeJson(respuesta, jsonStr);
          
          Serial.printf("📤 Enviando confirmación: %s\n", jsonStr.c_str());
          webSocket.sendTXT(jsonStr);
          
          delay(500);
          Serial.println("🔄 REINICIANDO ESP32 en 3 segundos...");
          delay(3000);
          ESP.restart();
        }
        
        // ════════════════════════════════════════
        // TEST CONEXIÓN
        // ════════════════════════════════════════
        else if (tipoMensaje == "test_conexion") {
          Serial.println("🧪 Test de conexión recibido");
          
          StaticJsonDocument<256> respuesta;
          respuesta["tipo"] = "test_respuesta";
          respuesta["device_id"] = deviceId;
          respuesta["estado"] = "online";
          respuesta["wifi_rssi"] = WiFi.RSSI();
          respuesta["uptime"] = millis() / 1000;
          respuesta["free_heap"] = ESP.getFreeHeap();
          respuesta["sensores"]["nfc"] = sensores.pn532_ok;
          respuesta["sensores"]["radar"] = sensores.ld2410_ok;
          respuesta["sensores"]["bme280"] = sensores.bme280_ok;
          respuesta["sensores"]["bh1750"] = sensores.bh1750_ok;
          
          String jsonStr;
          serializeJson(respuesta, jsonStr);
          
          Serial.println("📤 Enviando respuesta de test:");
          serializeJsonPretty(respuesta, Serial);
          Serial.println();
          
          webSocket.sendTXT(jsonStr);
          Serial.println("✅ Respuesta enviada");
        }
        
        // ════════════════════════════════════════
        // CONFIGURAR AULA
        // ════════════════════════════════════════
        else if (tipoMensaje == "configurar_aula") {
          Serial.println("⚙️ Procesando configuración de aula");
          
          JsonObject data = doc["data"];
          
          if (!data) {
            Serial.println("❌ Falta objeto 'data'");
            return;
          }
          
          Serial.println("📝 Nuevos valores:");
          bool nombreCambiado = false;
          
          if (data.containsKey("nombre")) {
            String nombre = data["nombre"].as<String>();
            Serial.printf("   📌 Nombre: %s\n", nombre.c_str());
            // Guardar en NVS (Preferences) y actualizar variable global
            Preferences preferences;
            preferences.begin("config", false);
            preferences.putString("aula", nombre);
            preferences.end();
            aula = nombre;
            nombreCambiado = true;
            Serial.printf("💾 Nombre de aula persistido en NVS: %s\n", nombre.c_str());
          }
          if (data.containsKey("edificio")) {
            String edificio = data["edificio"].as<String>();
            Serial.printf("   🏢 Edificio: %s\n", edificio.c_str());
          }
          if (data.containsKey("planta")) {
            int planta = data["planta"].as<int>();
            Serial.printf("   🔢 Planta: %d\n", planta);
          }
          if (data.containsKey("capacidad")) {
            int capacidad = data["capacidad"].as<int>();
            Serial.printf("   👥 Capacidad: %d personas\n", capacidad);
          }
          if (data.containsKey("calefaccion")) {
            bool calefaccion = data["calefaccion"].as<bool>();
            Serial.printf("   🔥 Calefacción: %s\n", calefaccion ? "Habilitada" : "Deshabilitada");
          }
          if (data.containsKey("iluminacion")) {
            bool iluminacion = data["iluminacion"].as<bool>();
            Serial.printf("   💡 Iluminación: %s\n", iluminacion ? "Habilitada" : "Deshabilitada");
          }
          
          // Confirmar configuración
          StaticJsonDocument<128> respuesta;
          respuesta["tipo"] = "config_confirmada";
          respuesta["device_id"] = deviceId;
          String jsonStr;
          serializeJson(respuesta, jsonStr);
          
          Serial.printf("📤 Enviando confirmación: %s\n", jsonStr.c_str());
          webSocket.sendTXT(jsonStr);
          
          // 🔄 Si cambió el nombre, re-registrar el nodo para sincronizar con el servidor
          if (nombreCambiado) {
            Serial.println("🔄 Nombre de aula cambiado, re-registrando nodo...");
            delay(100); // Pequeño delay para asegurar que la confirmación llegue primero
            
            StaticJsonDocument<200> reregistro;
            reregistro["tipo"] = "nodo_conectado";
            reregistro["device_id"] = deviceId;
            reregistro["aula"] = aula;
            reregistro["ip"] = WiFi.localIP().toString();
            reregistro["uptime"] = millis() / 1000;
            reregistro["relay1"] = relay1Estado;
            reregistro["relay2"] = relay2Estado;
            
            String reregistroJson;
            serializeJson(reregistro, reregistroJson);
            Serial.printf("📤 Re-registrando con nuevo nombre: %s\n", reregistroJson.c_str());
            webSocket.sendTXT(reregistroJson);
          }
          
          Serial.println("✅ Configuración aplicada");
        }
        
        // ════════════════════════════════════════
        // ESTADO INICIAL
        // ════════════════════════════════════════
        else if (tipoMensaje == "estado_inicial") {
          Serial.println("📦 Estado inicial recibido del servidor");
          wsConectado = true;  // Marcar como conectado
          
          if (doc.containsKey("data")) {
            JsonObject data = doc["data"];
            Serial.printf("   Aulas en el servidor: %d\n", data.size());
            
            // Opcional: mostrar las aulas
            for (JsonPair kv : data) {
              Serial.printf("   - %s\n", kv.key().c_str());
            }
          }
        }
        
        // ════════════════════════════════════════
        // ACK BIENVENIDA (confirmación del servidor)
        // ════════════════════════════════════════
        else if (tipoMensaje == "ack_bienvenida") {
          Serial.println("✅ Servidor confirmó vinculación de aula");
          wsConectado = true;  // Confirmar conexión establecida
          if (doc.containsKey("mensaje")) {
            Serial.printf("   Mensaje: %s\n", doc["mensaje"].as<const char*>());
          }
        }
        
        // ════════════════════════════════════════
        // MENSAJE DESCONOCIDO
        // ════════════════════════════════════════
        else {
          Serial.printf("⚠️ Tipo de mensaje no reconocido: '%s'\n", tipoMensaje.c_str());
        }
      }
      break;

    case WStype_BIN:
      {
        Serial.println("📦 Mensaje BINARIO recibido");
        Serial.printf("   Longitud: %d bytes\n", length);
        
        if (length > 0 && length <= 128) {
          Serial.print("   Contenido (hex): ");
          for(size_t i = 0; i < length; i++) {
            if(payload[i] < 0x10) Serial.print("0");
            Serial.print(payload[i], HEX);
            Serial.print(" ");
          }
          Serial.println();
        }
        
        Serial.println("⚠️ Procesamiento de binarios no implementado");
      }
      break;

    case WStype_PING:
      Serial.println("🔸 PING recibido del servidor");
      Serial.println("   (PONG enviado automáticamente)");
      break;

    case WStype_PONG:
      Serial.println("🔹 PONG recibido del servidor");
      break;
      
    case WStype_ERROR:
      {
        Serial.println("❌ ERROR de WebSocket");
        if (length > 0) {
          Serial.print("   Mensaje: ");
          Serial.write(payload, length);
          Serial.println();
          
          // Convertir payload a string para análisis
          String errorMsg = String((char*)payload);
          errorMsg.toLowerCase();
          
          // Si es error de autenticación, invalidar token
          if (errorMsg.indexOf("401") >= 0 || 
              errorMsg.indexOf("403") >= 0 || 
              errorMsg.indexOf("unauthorized") >= 0 ||
              errorMsg.indexOf("forbidden") >= 0 ||
              errorMsg.indexOf("invalid token") >= 0) {
            Serial.println("🔑 Error de autenticación detectado - Invalidando token");
            invalidateToken();
          }
        }
        wsConectado = false;
      }
      break;

    default:
      Serial.printf("⚠️ Evento NO MANEJADO (tipo %d)\n", type);
      break;
  }
  
  Serial.println("╚════════════════════════════════════╝\n");
}

// ════════════════════════════════════════════════════════
// FUNCIÓN DE CONEXIÓN CON LOGS
// ════════════════════════════════════════════════════════
void connectWS(){
  Serial.println("\n╔════════════════════════════════════╗");
  Serial.println("║ 🌐 CONECTANDO WEBSOCKET            ║");
  Serial.println("╚════════════════════════════════════╝");
  
  // ✅ Verificar si ya está conectado
  if (webSocket.isConnected()) {
    Serial.println("⚠️ WebSocket ya está conectado - omitiendo reconexión");
    return;
  }
  
  // ✅ Verificar conexión WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ ERROR: WiFi no conectado");
    Serial.println("   No se puede conectar WebSocket sin WiFi");
    return;
  }
  
  // ✅ Desconectar WebSocket anterior si existe
  Serial.println("🔌 Cerrando conexión anterior (si existe)...");
  webSocket.disconnect();
  delay(500);
  
  // ✅ Obtener token
  Serial.println("🔐 Solicitando token JWT...");
  String token = ensureToken();
  
  if (token.length() == 0) {
    Serial.println("❌ ERROR: No se pudo obtener token");
    Serial.println("   El WebSocket NO se conectará");
    return;
  }
  
  Serial.printf("✅ Token obtenido (longitud: %d caracteres)\n", token.length());
  Serial.printf("   Primeros 20 chars: %s...\n", token.substring(0, 20).c_str());
  
  // ✅ Construir path
  String path = "/ws?token=" + token;
  
  Serial.println("\n📋 Configuración de conexión:");
  Serial.printf("   Host:     %s\n", wsHost);
  Serial.printf("   Puerto:   %d\n", wsPort);
  Serial.printf("   Path:     %s\n", path.c_str());
  Serial.printf("   Protocolo: WSS (SSL/TLS)\n");
  Serial.printf("   WiFi:     %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("   RSSI:     %d dBm\n", WiFi.RSSI());
  
  // ✅ Conectar
  Serial.println("\n🔌 Iniciando conexión SSL...");
  webSocket.beginSSL(wsHost, wsPort, path.c_str());
  //webSocket.beginSSL(wsHost, wsPort, path.c_str());
  //webSocket.setCACert(server_certificate);
  //webSocket.setInsecure(); // Aceptar certificados no válidos
  
  // ✅ Configurar eventos
  Serial.println("📡 Configurando event handler...");
  webSocket.onEvent(webSocketEvent);
  
  // ✅ Configurar reconexión automática
  Serial.println("🔄 Configurando reconexión automática (5s)...");
  webSocket.setReconnectInterval(5000);
  
  // ✅ Configurar heartbeat
  Serial.println("💓 Configurando heartbeat: Ping cada 15s, Timeout: 3s, Reintentos: 2");
  webSocket.enableHeartbeat(15000, 3000, 2);
  
  // ⚠️ Certificado SSL (comentado)
  Serial.println("\n⚠️ Certificado SSL:");
  if (strlen(server_certificate) > 0) {
    Serial.println("   Certificado configurado pero comentado");
    Serial.println("   Usando conexión SSL sin validación");
    // webSocket.setCACert(server_certificate);
  } else {
    Serial.println("   Sin certificado (conexión insegura)");
  }
  
  Serial.println("\n✅ WebSocket configurado correctamente");
  Serial.println("   Esperando evento CONNECTED...\n");
  Serial.println("╚════════════════════════════════════╝\n");
}


// ✅ NUEVA FUNCIÓN: Confirmar cambio de relé al servidor
void enviarConfirmacionRelay(int relayNum, bool relayState) {
    Serial.println("╔════════════════════════════════════╗");
    Serial.println("║ 📤 ENVIANDO CONFIRMACION RELAY     ║");
    Serial.println("╚════════════════════════════════════╝");
    
    StaticJsonDocument<256> doc;
    doc["tipo"] = "confirmacion_relay";
    doc["device_id"] = deviceId;
    doc["aula"] = aula;
    doc["relay_num"] = relayNum;
    doc["relay_state"] = relayState;
    doc["timestamp"] = millis();

    String jsonString;
    serializeJson(doc, jsonString);
    
    Serial.printf("   Relay: %d\n", relayNum);
    Serial.printf("   Estado: %s\n", relayState ? "ON" : "OFF");
    Serial.printf("   JSON: %s\n", jsonString.c_str());
    
    webSocket.sendTXT(jsonString);
    
    Serial.println("✅ Confirmación enviada al servidor");
    Serial.println("╚════════════════════════════════════╝\n");
}

void enviarSaludoInicial() {
    StaticJsonDocument<256> doc;
    doc["tipo"] = "nodo_conectado";
    doc["device_id"] = deviceId;
    doc["aula"] = aula;
    doc["uptime"] = millis();

    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);
}

void enviarTestRespuesta() {
    StaticJsonDocument<256> doc;
    doc["tipo"] = "test_respuesta";
    doc["device_id"] = deviceId;
    doc["status"] = "ok";
    doc["uptime"] = millis();

    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);
}

void enviarConfirmacionReset() {
    StaticJsonDocument<128> doc;
    doc["tipo"] = "reset_confirmado";
    doc["device_id"] = deviceId;

    String jsonString;
    serializeJson(doc, jsonString);
    webSocket.sendTXT(jsonString);
}

