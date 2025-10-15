void registrarAsistencia() {

  HTTPClient http;
  http.begin(String(serverUrl) + registro);
  http.addHeader("Content-Type", "application/json");
  //http.addHeader("Authorization", jwtToken);
  //String jsonPayload = "{\"uid\": \"ABC123456\", \"nombre_aula\": \"Aula 101\"}";
  String tarjetaUID = uidToString(uid, LongitudUID);  // Función que crearemos a continuación
  String jsonPayload = "{\"uid\": \"" + tarjetaUID + "\", \"nombre_aula\": \"" + aula + "\"}";
  int httpResponseCode = http.POST(jsonPayload);
  if (httpResponseCode > 0) {
    String respuesta = http.getString();
    Serial.println("Respuesta obtenida: " + respuesta);
    Serial.println("Asistencia registrada");
    //digitalWrite(LED_VERDE, HIGH);
    //delay(2000);
    //digitalWrite(LED_VERDE, LOW);
  } else {
    Serial.println("Error registrando asistencia");
  }

  http.end();
}

// Función para consultar la próxima clase desde el servidor
void obtenerProximaClase() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    // Construir la URL con el parámetro aula (haciendo URL encode si es necesario)
    String url = String(serverUrl) + "/proxima_clase_test?aula=" + urlencode(aula);
    Serial.println("Consultando: " + url);

    http.begin(url);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println("Respuesta: " + payload);

      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);
      if (error) {
        Serial.print("Error al parsear JSON: ");
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
      Serial.print("Error en GET, código: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("Error: WiFi no conectado");
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

  Serial.println();

  // Enviar los datos a través de la API REST
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(String(serverUrl) + datos_aula);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["aula"] = aula;
    doc["temperatura"] = temperatura;
    doc["luz"] = iluminacion;
    doc["personas"] = personas;
    doc["clase_en_curso"] = clase_en_curso;

    String payload;
    serializeJson(doc, payload);

    int httpResponseCode = http.POST(payload);
    Serial.print("Código de respuesta: ");
    Serial.println(httpResponseCode);

    http.end();
  }
}

// Obtener token al iniciar la conexión
void obtenerToken() {
  HTTPClient http;
  http.begin(String(serverUrl) + "/login_aula");
  http.addHeader("Content-Type", "application/json");

  String jsonPayload = "{\"nombre_aula\": \"Aula 101\", \"password_aula\": \"pass321\"}";
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Respuesta completa: " + response);
    
    // Parsear JSON para extraer el token
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (error) {
      Serial.print("Error parseando JSON: ");
      Serial.println(error.f_str());
    } else {
      if (doc.containsKey("token")) {
        jwtToken = doc["token"].as<String>();
        Serial.println("✅ Token JWT obtenido correctamente");
        Serial.println("Token: " + jwtToken.substring(0, 20) + "...");
      } else {
        Serial.println("❌ No se encontró el campo 'token' en la respuesta");
      }
    }
  } else {
    Serial.print("❌ Error obteniendo token. Código: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}