void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  Serial.print("📩 [WebSocketEvent] Tipo: ");
  Serial.println(type);
  Serial.print("📜 Longitud del payload: ");
  Serial.println(length);

  /*// Convertir 'payload' a cadena de texto para inspeccionar
  // (Útil si WStype_TEXT, pero ojo que 'payload' no siempre es texto)
  if (length > 0) {
    Serial.print("📥 Mensaje recibido: ");
    Serial.write(payload, length);
    Serial.println();
  }*/

  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("❌ WebSocket desconectado");
      break;

    case WStype_CONNECTED:
      {
        Serial.println("✅ WebSocket conectado");
        // Si quieres mandar un mensaje al servidor al conectar:
        // webSocket.sendTXT("Hola, servidor!");
      }
      break;

    case WStype_TEXT:
      {
        // Mensaje de texto (posiblemente JSON)
        if (length == 0) {
          Serial.println("⚠️ Mensaje de texto vacío, ignorando.");
          return;
        }

        // Intentar parsear como JSON
        StaticJsonDocument<512> doc;  // Aumentado de 256 a 512 para device_id
        DeserializationError error = deserializeJson(doc, (char*)payload, length);

        if (error) {
          // No es JSON válido, o no es de tu interés
          Serial.print("❌ Error al parsear JSON: ");
          Serial.println(error.f_str());
          return;
        }

        // ⚠️ VALIDACIÓN CRÍTICA: Verificar que el mensaje es para este nodo
        if (doc.containsKey("device_id")) {
          String targetDeviceId = doc["device_id"].as<String>();
          
          // Comparar con el device_id de este nodo
          if (targetDeviceId != deviceId) {
            Serial.print("⏭️ Mensaje no destinado a este nodo (destino: ");
            Serial.print(targetDeviceId);
            Serial.print(", este nodo: ");
            Serial.print(deviceId);
            Serial.println("), ignorando.");
            return;  // Salir sin procesar el mensaje
          }
          
          Serial.print("✅ Mensaje confirmado para este nodo: ");
          Serial.println(deviceId);
        } else {
          // Mensajes sin device_id se consideran broadcasts (opcional)
          Serial.println("📢 Mensaje sin device_id (broadcast), procesando...");
        }

        // Ejemplo: esperamos { "tipo": "...", "device_id": "...", "data": {...} }
        if (doc.containsKey("tipo")) {
          String tipoMensaje = doc["tipo"].as<String>();
          
          if (tipoMensaje == "actualizacion_relay1") {
            // Formato esperado: { "tipo":"actualizacion_relay1", "device_id":"ESP32_xxx", "relay":true }
            bool relayState = doc["relay"];

            // Actuar en consecuencia
            Serial.print("✅ Actualizando relé 1 => ");
            Serial.println(relayState ? "Encendido" : "Apagado");
            digitalWrite(relayPin1, relayState ? HIGH : LOW);
          }
          else if (tipoMensaje == "actualizacion_relay2") {
            // Formato esperado: { "tipo":"actualizacion_relay2", "device_id":"ESP32_xxx", "relay":true }
            bool relayState = doc["relay"];

            // Actuar en consecuencia
            Serial.print("✅ Actualizando relé 2 => ");
            Serial.println(relayState ? "Encendido" : "Apagado");
            digitalWrite(relayPin2, relayState ? HIGH : LOW);
          }
          else if (tipoMensaje == "actualizacion_aula") {
            // ... tu código existente
          }
          else if (tipoMensaje == "resetear_nodo") {
            // Comando administrativo: resetear el ESP32
            Serial.println("🔄 Comando RESET recibido del servidor");
            
            // Enviar confirmación antes de resetear
            StaticJsonDocument<128> respuesta;
            respuesta["tipo"] = "reset_confirmado";
            respuesta["device_id"] = deviceId;
            String jsonStr;
            serializeJson(respuesta, jsonStr);
            webSocket.sendTXT(jsonStr);
            
            delay(500);  // Dar tiempo para enviar el mensaje
            Serial.println("🔄 Reiniciando ESP32...");
            ESP.restart();
          }
          else if (tipoMensaje == "test_conexion") {
            // Comando administrativo: test de conectividad
            Serial.println("🧪 Test de conexión recibido");
            
            // Responder con estado del nodo
            StaticJsonDocument<256> respuesta;
            respuesta["tipo"] = "test_respuesta";
            respuesta["device_id"] = deviceId;
            respuesta["estado"] = "online";
            respuesta["wifi_rssi"] = WiFi.RSSI();
            respuesta["uptime"] = millis() / 1000;  // segundos desde boot
            respuesta["free_heap"] = ESP.getFreeHeap();
            
            String jsonStr;
            serializeJson(respuesta, jsonStr);
            webSocket.sendTXT(jsonStr);
            
            Serial.println("✅ Respuesta de test enviada");
          }
          
          // ... (resto de tus else if) ...

          // AÑADE ESTE BLOQUE
          else if (tipoMensaje == "configurar_aula") {
            Serial.println("⚙️ Recibido comando 'configurar_aula' del servidor");
            
            // El servidor envía los datos dentro de un objeto "data"
            JsonObject data = doc["data"];

            if (!data) {
              Serial.println("❌ Error: 'configurar_aula' no contenía el objeto 'data'");
              return;
            }

            // Ahora, extraemos los valores del objeto 'data'
            // y los guardamos en nuestras variables globales o configuración
            
            if (data.containsKey("nombre")) {
              // Asumiendo que tienes una variable global como 'config.nombreAula'
              // config.nombreAula = data["nombre"].as<String>();
              Serial.print("  - Nuevo Nombre: ");
              Serial.println(data["nombre"].as<String>());
            }
            if (data.containsKey("edificio")) {
              // config.edificio = data["edificio"].as<String>();
              Serial.print("  - Nuevo Edificio: ");
              Serial.println(data["edificio"].as<String>());
            }
            if (data.containsKey("planta")) {
              // config.planta = data["planta"].as<int>();
              Serial.print("  - Nueva Planta: ");
              Serial.println(data["planta"].as<int>());
            }
            if (data.containsKey("capacidad")) {
              // config.capacidad = data["capacidad"].as<int>();
              Serial.print("  - Nueva Capacidad: ");
              Serial.println(data["capacidad"].as<int>());
            }
            if (data.containsKey("calefaccion")) {
              // config.calefaccionEnabled = data["calefaccion"].as<bool>();
              Serial.print("  - Calefacción Habilitada: ");
              Serial.println(data["calefaccion"].as<bool>());
            }
            if (data.containsKey("iluminacion")) {
              // config.iluminacionEnabled = data["iluminacion"].as<bool>();
              Serial.print("  - Iluminación Habilitada: ");
              Serial.println(data["iluminacion"].as<bool>());
            }

            // TODO IMPORTANTE:
            // Aquí deberías guardar esta configuración en la memoria
            // persistente (EEPROM, NVS o SPIFFS) para que sobreviva
            // a un reinicio.
            // Ejemplo: saveConfigurationToNVS(config);
            
            Serial.println("✅ Configuración de aula actualizada en el nodo.");
            
            // Enviar confirmación al servidor
            StaticJsonDocument<128> respuesta;
            respuesta["tipo"] = "config_confirmada";
            respuesta["device_id"] = deviceId;
            String jsonStr;
            serializeJson(respuesta, jsonStr);
            webSocket.sendTXT(jsonStr);
          }
          else if (tipoMensaje == "estado_inicial") {
            // { "tipo":"estado_inicial", "data": { "Aula 101": {...}, "Aula 102": {...} } }
            Serial.println("📦 Estado inicial recibido");
            // ...
          }
          else {
            Serial.print("⚠️ Tipo de mensaje no reconocido: ");
            Serial.println(tipoMensaje);
          }
        } 
        else {
          Serial.println("⚠️ Mensaje JSON no contiene 'tipo', ignorando.");
        }
      }
      break;

    case WStype_BIN:
      Serial.println("📦 Mensaje binario recibido, longitud:");
      Serial.println(length);
      // Aquí podrías procesar datos binarios si tu app lo necesita
      break;

    case WStype_PING:
      Serial.println("🔸 Ping recibido");
      break;

    case WStype_PONG:
      Serial.println("🔹 Pong recibido");
      break;

    default:
      Serial.println("⚠️ Evento no manejado");
      break;
  }
}

void connectWS(){
  Serial.println("🌐 Conectando WebSocket...");
  String token = ensureToken();
  String path = "/ws?token=" + token;
  // Usar token en la conexión
  webSocket.beginSSL(wsHost, wsPort, path.c_str());
  // No hay setInsecure() en esta versión de la librería
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  // Configurar heartbeat
  webSocket.enableHeartbeat(15000, 3000, 2);
  Serial.println("WebSocket configurado\n");
  //webSocket.setCACert(server_certificate);
  // no funciona por ahora
}
