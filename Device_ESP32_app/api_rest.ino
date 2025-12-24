// Versión original (mantener para compatibilidad) - ahora devuelve bool
bool registrarAsistencia(String tarjetaUID) {
  return registrarAsistenciaConTimestamp(tarjetaUID, 0);  // 0 = usar timestamp actual
}

// Nueva versión con timestamp
bool registrarAsistenciaConTimestamp(String tarjetaUID, unsigned long eventTimestamp) {
  Serial.println("\n=== REGISTRO DE ASISTENCIA ===");
  
  WiFiClientSecure client;
  client.setCACert(server_certificate);
  //
   client.setInsecure(); // ⚠️ TEMPORAL: Desactiva validación SSL para debugging
  
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
      ledVerde(true); // Encender LED verde al registrar asistencia correctamente
      String respuesta = https.getString();
      Serial.print("✅ Respuesta HTTP "); Serial.print(httpResponseCode); Serial.println(":");
      Serial.println(respuesta);
      Serial.println("✅ Asistencia registrada correctamente");
      exito = true;
      delay(500);
      ledVerde(false); // Apagar LED verde
    } else if (httpResponseCode == 403) {
      ledRojo(true); // Encender LED rojo al error de acceso denegado
      delay(1000);
      ledRojo(false); // Apagar LED rojo
      Serial.println("❌ Acceso denegado: Tarjeta no autorizada");
    } else if (httpResponseCode == 404) {
      ledRojo(true); // Encender LED rojo al error de acceso denegado
      delay(1000);
      Serial.println("❌ Error 404: Tarjeta desconocida");
    } else if (httpResponseCode == 500) {
      ledRojo(true); // Encender LED rojo al error de acceso denegado
      delay(1000);
      Serial.println("❌ Error 500: Error interno del servidor");
    } else {
      ledRojo(true); // Encender LED rojo al error de acceso denegado
      delay(1000);
      Serial.print("❌ Error HTTP inesperado: "); Serial.println(httpResponseCode);
      if (eventTimestamp == 0) {  // Solo guardar en cola si es un evento nuevo
        saveToQueue("fichaje", jsonPayload, millis());
        Serial.println("⚠️ Asistencia guardada en cola para reintento");
      }
    }
  } else {
    ledRojo(true); // Encender LED rojo al error de acceso denegado
      delay(1000);
    Serial.print("❌ Error HTTP: "); Serial.println(httpResponseCode);
    if (eventTimestamp == 0) {  // Solo guardar en cola si es un evento nuevo
      saveToQueue("fichaje", jsonPayload, millis());
      Serial.println("⚠️ Asistencia guardada en cola para reintento");
    }
  }
  ledRojo(false); // Apagar LED rojo
  ledAmarillo(false); // Apagar LED amarillo
  https.end();
  Serial.println("=================================\n");
  
  return exito;
}



// Versión original (mantener para compatibilidad)
void EnviaValoresAula() {
  enviarValoresConTimestamp(0, 0, 0, 0, 0);  // 0 = leer sensores y usar timestamp actual
}

// Nueva versión con timestamp y valores como parámetros
bool enviarValoresConTimestamp(float temp, float hum, float lux, int personas, unsigned long eventTimestamp) {
  // ✅ Usar webSocket.isConnected() en lugar de variable wsConectado
  if (!webSocket.isConnected()) {
    Serial.println("❌ WebSocket no conectado, no se envían datos");
    return false;
  }

  StaticJsonDocument<256> doc;
  doc["tipo"] = "datos_aula";
  doc["aula"] = aula;
  doc["ip"]= WiFi.localIP().toString();
  
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


void obtenerProximaClase() {
  Serial.println("\n📅 === ACTUALIZANDO DATOS DE CLASE ===");
  
  // Verificar conexión WiFi
  if (WiFi.status() == WL_CONNECTED) {    
    WiFiClientSecure client;
    client.setInsecure(); // SSL sin verificación (para desarrollo)
    HTTPClient https;
    String url = String(serverUrl) + String(clases_actual) + "?aula=" + urlencode(aula);
    https.setTimeout(10000); 
    // Iniciar conexión HTTPS
    if (https.begin(client, url)) {
      int httpResponseCode = https.GET();
      // Verificar respuesta HTTP
      if (httpResponseCode == HTTP_CODE_OK) { 
        String payload = https.getString();
        // Parsear JSON
        StaticJsonDocument<512> doc;
        DeserializationError error = deserializeJson(doc, payload);
        if (!error) {
          // LÓGICA PRINCIPAL:
          // Comprobamos si el JSON tiene el campo "asignatura".
          // Si lo tiene, es una clase. Si no, asumimos que es el mensaje de aviso.
          if (doc.containsKey("asignatura")) {
            // --- CASO 1: HAY CLASE ---
            claseActual = doc["asignatura"].as<String>();
            horaInicioClase = doc["hora_inicio"].as<String>();
            horaFinClase = doc["hora_fin"].as<String>();
            claseEnCurso = true; 
            // Marcamos que hay una clase en curso
            Serial.println("✅ Clase detectada y guardada:");
            Serial.println("   Asignatura: " + claseActual);
            Serial.println("   Horario: " + horaInicioClase + " - " + horaFinClase);

          } else {
            // --- CASO 2: MENSAJE DE "NO HAY CLASE" ---
            String msgServidor = "";
            if (doc.containsKey("mensaje")) msgServidor = doc["mensaje"].as<String>();
            else if (doc.containsKey("message")) msgServidor = doc["message"].as<String>();
            
            Serial.print("ℹ️ Info del servidor: ");
            Serial.println(msgServidor.length() > 0 ? msgServidor : "No hay clase próxima");

            // IMPORTANTE: Limpiar variables globales
            claseActual = "";
            horaInicioClase = "";
            horaFinClase = "";
            claseEnCurso = false;
          }

        } else {
          Serial.print("❌ Error al parsear JSON: "); Serial.println(error.c_str());
        }
      } else {
        Serial.printf("❌ Error HTTP: %d\n", httpResponseCode);
      }
      https.end();
    } else {
      Serial.println("❌ Fallo de conexión (https.begin)");
    }
  } else {
    Serial.println("❌ WiFi desconectado");
  }
}