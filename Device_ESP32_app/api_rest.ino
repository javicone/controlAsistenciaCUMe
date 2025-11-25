// Versión original (mantener para compatibilidad)
void registrarAsistencia(String tarjetaUID) {
  registrarAsistenciaConTimestamp(tarjetaUID, 0);  // 0 = usar timestamp actual
}

// Nueva versión con timestamp
bool registrarAsistenciaConTimestamp(String tarjetaUID, unsigned long eventTimestamp) {
  Serial.println("\n=== REGISTRO DE ASISTENCIA ===");
  
  WiFiClientSecure client;
  client.setCACert(server_certificate);
  //
  // client.setInsecure(); // ⚠️ TEMPORAL: Desactiva validación SSL para debugging
  
  Serial.println("🔍 DEBUG: Validación SSL desactivada temporalmente");
  
  HTTPClient https;
  String fullUrl = String(serverUrl) + registro;
  Serial.print("📍 URL: "); Serial.println(fullUrl);
  
  https.setTimeout(15000);
  https.begin(client, fullUrl);
  https.addHeader("Content-Type", "application/json");
  
  // Preparar JSON con timestamp
  StaticJsonDocument<256> doc;
  doc["uid"] = tarjetaUID;
  doc["nombre_aula"] = aula;
  
  // Si eventTimestamp es 0, usar timestamp actual
  if (eventTimestamp == 0) {
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      char timestamp[25];
      strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);
      doc["timestamp"] = timestamp;
    }
  } else {
    // Convertir eventTimestamp (millis) a formato ISO
    time_t t = eventTimestamp / 1000;
    struct tm *timeinfo = localtime(&t);
    char timestamp[25];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", timeinfo);
    doc["timestamp"] = timestamp;
  }
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.println("📤 Enviando datos de asistencia...");
  Serial.print("📋 Payload: "); Serial.println(jsonPayload);
  
  int httpResponseCode = https.POST(jsonPayload);
  bool exito = false;
  
  if (httpResponseCode > 0) {
    if (httpResponseCode == 200) {
      String respuesta = https.getString();
      Serial.print("✅ Respuesta HTTP "); Serial.print(httpResponseCode); Serial.println(":");
      Serial.println(respuesta);
      Serial.println("✅ Asistencia registrada correctamente");
      exito = true;
    } else if (httpResponseCode == 403) {
      Serial.println("❌ Acceso denegado: Tarjeta no autorizada");
    } else if (httpResponseCode == 404) {
      Serial.println("❌ Error 404: Tarjeta desconocida");
    } else if (httpResponseCode == 500) {
      Serial.println("❌ Error 500: Error interno del servidor");
    } else {
      Serial.print("❌ Error HTTP inesperado: "); Serial.println(httpResponseCode);
      if (eventTimestamp == 0) {  // Solo guardar en cola si es un evento nuevo
        saveToQueue("fichaje", jsonPayload, millis());
        Serial.println("⚠️ Asistencia guardada en cola para reintento");
      }
    }
  } else {
    Serial.print("❌ Error HTTP: "); Serial.println(httpResponseCode);
    if (eventTimestamp == 0) {  // Solo guardar en cola si es un evento nuevo
      saveToQueue("fichaje", jsonPayload, millis());
      Serial.println("⚠️ Asistencia guardada en cola para reintento");
    }
  }

  https.end();
  Serial.println("=================================\n");
  
  return exito;
}

// Función para consultar la próxima clase desde el servidor
void obtenerProximaClase() {
  Serial.println("\n📅 === CONSULTAR PRÓXIMA CLASE ===");
  
  // Verificar protocolo
  String urlStr = String(serverUrl);
  bool usingHTTPS = urlStr.startsWith("https://");
  
  if(usingHTTPS) {
  WiFiClientSecure client;
  client.setCACert(server_certificate);
  //client.setInsecure(); // ⚠️ TEMPORAL: Desactiva validación SSL para debugging
  
  Serial.println("🔍 DEBUG: Validación SSL desactivada temporalmente");
  
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient https;
    // Construir la URL con el parámetro aula (haciendo URL encode si es necesario)
    String url = String(serverUrl) + "/proxima_clase_test?aula=" + urlencode(aula);
    Serial.print("📍 URL: "); Serial.println(url);

    https.setTimeout(15000); // 15 segundos timeout
    https.begin(client, url);
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
    Serial.println("====================================\n");
  } else {
    Serial.println("❌ WiFi no conectado");
    Serial.println("====================================\n");
  }
    Serial.println("====================================\n");
  } else {
    Serial.println("❌ WiFi no conectado");
    Serial.println("====================================\n");
  }
}



// Versión original (mantener para compatibilidad)
void EnviaValoresAula() {
  enviarValoresConTimestamp(0, 0, 0, 0, 0);  // 0 = leer sensores y usar timestamp actual
}

// Nueva versión con timestamp y valores como parámetros
bool enviarValoresConTimestamp(float temp, float hum, float lux, int personas, unsigned long eventTimestamp) {
  if (!wsConectado) {
    Serial.println("❌ WebSocket no conectado, no se envían datos");
    return false;
  }

  StaticJsonDocument<256> doc;
  doc["tipo"] = "datos_aula";
  doc["aula"] = aula;
  
  // Si los valores son 0, leer de sensores (modo normal)
  if (temp == 0 && hum == 0 && lux == 0 && personas == 0) {
    BME280Data bme_data = leerBME280();
    LuzData luz_data = leerLuz();
    RadarData radar_data = leerRadar();
    
    if (bme_data.valido) {
      doc["temperatura"] = bme_data.temperatura;
      doc["humedad"] = bme_data.humedad;
      doc["presion"] = bme_data.presion;
    } else {
      doc["temperatura"] = -999;
      doc["humedad"] = -999;
      doc["presion"] = -999;
    }
    
    if (luz_data.valido) {
      doc["luz"] = luz_data.lux;
    } else {
      doc["luz"] = -999;
    }
    
    if (radar_data.valido) {
      doc["personas"] = radar_data.presenciaDetectada ? 1 : 0;
    } else {
      doc["personas"] = 0;
    }
  } else {
    // Usar valores pasados como parámetros (desde cola)
    doc["temperatura"] = temp;
    doc["humedad"] = hum;
    doc["luz"] = lux;
    doc["personas"] = personas;
  }
  
  // Añadir timestamp
  if (eventTimestamp == 0) {
    struct tm timeinfo;
    if (getLocalTime(&timeinfo)) {
      char timestamp[25];
      strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", &timeinfo);
      doc["timestamp"] = timestamp;
    }
  } else {
    time_t t = eventTimestamp / 1000;
    struct tm *timeinfo = localtime(&t);
    char timestamp[25];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", timeinfo);
    doc["timestamp"] = timestamp;
  }
  
  String json;
  serializeJson(doc, json);
  
  bool exito = webSocket.sendTXT(json);
  
  if (exito) {
    Serial.println("\n=== ENVÍO DE DATOS DEL AULA ===");
    Serial.println("📤 Enviando datos del aula vía WebSocket...");
    Serial.println("✅ Datos enviados exitosamente");
    Serial.println("===============================\n");
  } else {
    Serial.println("❌ Error enviando datos por WebSocket");
    if (eventTimestamp == 0) {  // Solo guardar en cola si es evento nuevo
      saveToQueue("sensores", json, millis());
      Serial.println("⚠️ Datos guardados en cola para reintento");
    }
  }
  
  return exito;
}