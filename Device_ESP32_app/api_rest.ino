void registrarAsistencia(String tarjetaUID) {
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
  
  String jsonPayload = "{\"uid\": \"" + tarjetaUID + "\", \"nombre_aula\": \"" + aula + "\"}";
  
  Serial.println("📤 Enviando datos de asistencia...");
  Serial.print("📋 Payload: "); Serial.println(jsonPayload);
  
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

  if (!wsConectado) {
    Serial.println("❌ WebSocket no conectado, no se envían datos");
    return;
  }


  // Leer sensores con validación
  BME280Data bme_data = leerBME280();
  LuzData luz_data = leerLuz();
  RadarData radar_data = leerRadar();

  StaticJsonDocument<256> doc;
  doc["tipo"] = "datos_aula";
  doc["aula"] = aula;
    // Solo enviar datos válidos
  if(bme_data.valido) {
    doc["temperatura"] = bme_data.temperatura;
    doc["humedad"] = bme_data.humedad;
    doc["presion"] = bme_data.presion;
  } else {
    doc["temperatura"] = -999;
    doc["humedad"] = -999;
    doc["presion"] = -999;
  }
  
  if(luz_data.valido) {
    doc["luz"] = luz_data.lux;
  } else {
    doc["luz"] = -999;
  }
  
  if(radar_data.valido) {
    doc["personas"] = radar_data.presenciaDetectada ? 1 : 0;
  } else {
    doc["personas"] = 0;
  }
  
  String json;
  serializeJson(doc, json);
  webSocket.sendTXT(json);
  Serial.println("\n=== ENVÍO DE DATOS DEL AULA ===");
  Serial.println("📤 Enviando datos del aula vía WebSocket...");
  Serial.println("✅ Datos enviados exitosamente");
  Serial.println("===============================\n");
  // Log opcional
  if(!bme_data.valido || !luz_data.valido || !radar_data.valido) {
    Serial.println("⚠️ Algunos sensores enviaron datos inválidos");
  }
}

