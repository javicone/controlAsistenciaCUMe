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
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, (char*)payload, length);

        if (error) {
          // No es JSON válido, o no es de tu interés
          Serial.print("❌ Error al parsear JSON: ");
          Serial.println(error.f_str());
          return;
        }

        // Ejemplo: esperamos { "tipo": "...", "aula": "...", "relay": true/false }
        if (doc.containsKey("tipo")) {
          String tipoMensaje = doc["tipo"].as<String>();
          if (tipoMensaje == "actualizacion_relay") {
            // Por ejemplo: { "tipo":"actualizacion_relay", "aula":"Aula 101", "relay":true }
            String aulaRecibida = doc["aula"].as<String>();
            bool relayState = doc["relay"];

            // Actuar en consecuencia
            Serial.print("✅ Actualizando relé para ");
            Serial.print(aulaRecibida);
            Serial.print(" => ");
            Serial.println(relayState ? "Encendido" : "Apagado");
            digitalWrite(relayPin, relayState ? HIGH : LOW);
          }
          else if (tipoMensaje == "actualizacion_aula") {
            // Ejemplo: { "tipo":"actualizacion_aula","aula":"Aula 101","temperatura":25,... }
            Serial.println("✅ Mensaje de actualización de datos de aula");
            // Haz lo que necesites con la info
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

connectWS(){
  Serial.println("🌐 Conectando WebSocket...");
  String token = ensureToken();
  String path = "/ws?token=" + token;
  // Usar token en la conexión
  webSocket.beginSSL(wsHost, wsPort, path.c_str());
  webSocket.setInsecure();  // Deshabilitar validación SSL si es necesario
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
  // Configurar heartbeat
  webSocket.enableHeartbeat(15000, 3000, 2);
  Serial.println("WebSocket configurado\n");
  //webSocket.setCACert(server_certificate);
  // no funciona por ahora
}
