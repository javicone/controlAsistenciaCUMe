void registrarAsistencia() {
  Serial.println("\n=== REGISTRO DE ASISTENCIA ===");
  
  WiFiClientSecure *client = new WiFiClientSecure();
  client->setCACert(server_certificate);
  //client->setInsecure(); // ⚠️ TEMPORAL: Desactiva validación SSL para debugging
  
  Serial.println("🔍 DEBUG: Validación SSL desactivada temporalmente");
  
  HTTPClient https;
  String fullUrl = String(serverUrl) + registro;
  Serial.print("📍 URL: "); Serial.println(fullUrl);
  
  // Timeout para evitar bloqueos
  https.setTimeout(15000); // 15 segundos
  
  https.begin(*client, fullUrl);
  https.addHeader("Content-Type", "application/json");
  
  String tarjetaUID = uidToString(uid, LongitudUID);
  String jsonPayload = "{\"uid\": \"" + tarjetaUID + "\", \"nombre_aula\": \"" + aula + "\"}";
  
  Serial.println("📤 Enviando datos de asistencia...");
  int httpResponseCode = https.POST(jsonPayload);
  
  if (httpResponseCode > 0) {
    String respuesta = https.getString();
    Serial.print("✅ Respuesta HTTP "); Serial.print(httpResponseCode); Serial.println(":");
    Serial.println(respuesta);
    Serial.println("✅ Asistencia registrada correctamente");
  } else {
    Serial.print("❌ Error HTTP: "); Serial.println(httpResponseCode);
    Serial.println("❌ Error registrando asistencia");
  }

  https.end();
  delete client;
  Serial.println("=================================\n");
}

// Función para consultar la próxima clase desde el servidor
void obtenerProximaClase() {
  Serial.println("\n📅 === CONSULTAR PRÓXIMA CLASE ===");
  
  // Verificar protocolo
  String urlStr = String(serverUrl);
  bool usingHTTPS = urlStr.startsWith("https://");
  
  if(usingHTTPS) {
    Serial.println("✅ Usando HTTPS (conexión cifrada)");
  } else {
    Serial.println("⚠️  Usando HTTP (conexión sin cifrar)");
  }
  
  WiFiClientSecure *client=new WiFiClientSecure();
  client->setCACert(server_certificate);
  client->setInsecure(); // ⚠️ TEMPORAL: Desactiva validación SSL para debugging
  
  Serial.println("🔍 DEBUG: Validación SSL desactivada temporalmente");
  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient https;
    // Construir la URL con el parámetro aula (haciendo URL encode si es necesario)
    String url = String(serverUrl) + "/proxima_clase_test?aula=" + urlencode(aula);
    Serial.print("📍 URL: "); Serial.println(url);

    https.setTimeout(15000); // 15 segundos timeout
    https.begin(*client, url);
    Serial.println("📤 Enviando petición GET...");
    int httpResponseCode = https.GET();

    if (httpResponseCode > 0) {
      String payload = https.getString();
      Serial.print("✅ Respuesta HTTP "); Serial.print(httpResponseCode); Serial.println(":");
      Serial.println(payload);

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);
      if (error) {
        Serial.print("❌ Error al parsear JSON: ");
        Serial.println(error.c_str());
      } else {
        const char* asignatura = doc["asignatura"];
        const char* hora_inicio = doc["hora_inicio"];
        const char* hora_fin = doc["hora_fin"];

        Serial.print("Asignatura: ");
        Serial.println(asignatura);
        Serial.print("Inicio: ");
        Serial.println(hora_inicio);
        Serial.print("Fin: ");
        Serial.println(hora_fin);

        // Convertir hora_inicio (cadena) a epoch en segundos.
        unsigned long startEpoch = epochFromString(String(hora_inicio));  // Función a implementar
        // Calcular tiempo objetivo: 5 minutos antes del inicio.
        //unsigned long targetEpoch = startEpoch > (5 * 60) ? (startEpoch - 5 * 60) : startEpoch;
        unsigned long targetEpoch = startEpoch;
        targetTimeMillis = targetEpoch * 1000UL;  // Convertir a milisegundos

        Serial.print("Hora objetivo (epoch): ");
        Serial.println(targetEpoch);

        // Obtener la hora actual desde el sistema (ya sincronizado con NTP)
        struct tm timeinfo;
        if (getLocalTime(&timeinfo)) {
          time_t nowEpoch = mktime(&timeinfo);

          Serial.printf("Inicio clase: %lu | Objetivo: %lu | Ahora: %lu\n", startEpoch, targetEpoch, nowEpoch);

          if (nowEpoch >= (targetEpoch - 300)) {
            // Encender LED rojo
            Serial.printf("Faltan menos de 5 minutos");
                  
            ledRedOn = true;
          }
        }
      }
    } else {
      Serial.print("❌ Error HTTP GET, código: ");
      Serial.println(httpResponseCode);
    }
    https.end();
    delete client;
    Serial.println("====================================\n");
  } else {
    Serial.println("❌ WiFi no conectado");
    Serial.println("====================================\n");
  }
}

void EnviaValoresAula() {

  temperatura = bme.readTemperature();
  Serial.print("Temperature = ");
  Serial.print(temperatura);
  Serial.println(" *C");

  iluminacion = lightMeter.readLightLevel();
  Serial.print("Light: ");
  Serial.print(iluminacion);
  Serial.println(" lx");

  Serial.println("\n📊 === ENVÍO DATOS DE AULA ===");
  Serial.println("✅ WebSocket Seguro (WSS) - Conexión cifrada");
  
  // Verificar estado de conexiones antes de enviar
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi desconectado, no se pueden enviar datos");
    Serial.println("===============================\n");
    return;
  }
  
  if (!webSocket.isConnected()) {
    Serial.println("⚠️  WebSocket NO conectado, omitiendo envío");
    Serial.println("💡 Tip: El WebSocket se reconectará automáticamente");
    Serial.println("===============================\n");
    return;
  }
  
  Serial.println("✅ Conexión WebSocket activa");
  
  // Enviar los datos a través de WebSocket (más eficiente que HTTP POST)
  StaticJsonDocument<256> doc;
  doc["tipo"] = "datos_aula"; // ← Identificador para el servidor
  doc["aula"] = aula;
  doc["temperatura"] = temperatura;
  doc["luz"] = iluminacion;
  doc["personas"] = personas;
  doc["clase_en_curso"] = clase_en_curso;

  String payload;
  serializeJson(doc, payload);
  
  Serial.print("📤 Enviando datos ("); 
  Serial.print(payload.length());
  Serial.println(" bytes):");
  Serial.println(payload);
  
  webSocket.sendTXT(payload);  // ✅ Enviar por WebSocket
  Serial.println("✅ Datos enviados exitosamente");
  Serial.println("===============================\n");
}

