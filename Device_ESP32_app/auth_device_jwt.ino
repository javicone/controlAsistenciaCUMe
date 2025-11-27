#include <Preferences.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

Preferences prefs;
String jwtToken = "";
unsigned long tokenExpirationTime = 0;

// Función para obtener el token JWT desde el servidor
bool fetchDeviceToken() {
  Serial.println("\n╔════════════════════════════════════╗");
  Serial.println("║ 🔐 OBTENIENDO TOKEN JWT           ║");
  Serial.println("╚════════════════════════════════════╝");
  
  // Verificar WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi no conectado");
    return false;
  }
  Serial.printf("✅ WiFi conectado: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("   RSSI: %d dBm\n", WiFi.RSSI());
  
  // Configurar cliente HTTPS
  WiFiClientSecure client;
  //client.setCACert(server_certificate);
  client.setInsecure(); // TODO: usar CA real con client.setCACert(...)
  Serial.println("⚠️ Validación SSL deshabilitada (certificado autofirmado)");
  
  HTTPClient https;
  
  // Construir URL
  String url = String(serverUrl) + "/auth/device";
  Serial.println("\n📋 Configuración de petición:");
  Serial.printf("   URL: %s\n", url.c_str());
  Serial.printf("   Device ID: %s\n", deviceId.c_str());
  Serial.printf("   API Key: %s...\n", apiKey.substring(0, 10).c_str());
  
  // Iniciar conexión
  Serial.println("\n🔌 Conectando al servidor...");
  if (!https.begin(client, url)) {
    Serial.println("❌ https.begin() falló");
    return false;
  }
  Serial.println("✅ Conexión HTTP iniciada");
  
  // Headers
  https.addHeader("Content-Type", "application/json");
  Serial.println("📝 Header 'Content-Type: application/json' añadido");

  // Crear JSON payload
  StaticJsonDocument<256> doc;
  doc["device_id"] = deviceId;
  doc["api_key"] = apiKey;
  String body;
  serializeJson(doc, body);
  
  Serial.println("\n📤 Enviando petición POST:");
  Serial.println("┌────────────────────────────────────┐");
  serializeJsonPretty(doc, Serial);
  Serial.println();
  Serial.println("└────────────────────────────────────┘");

  // Enviar petición
  Serial.println("\n⏳ Esperando respuesta del servidor...");
  int code = https.POST(body);
  
  Serial.printf("\n📊 Código HTTP: %d", code);
  
  if (code == 200) {
    Serial.println(" ✅ (OK)");
  } else if (code == 401) {
    Serial.println(" ❌ (UNAUTHORIZED - credenciales inválidas)");
    https.end();
    return false;
  } else if (code == 404) {
    Serial.println(" ❌ (NOT FOUND - endpoint no existe)");
    https.end();
    return false;
  } else if (code == 500) {
    Serial.println(" ❌ (SERVER ERROR - error del servidor)");
    https.end();
    return false;
  } else if (code < 0) {
    Serial.println(" ❌ (ERROR DE CONEXIÓN)");
    Serial.printf("   Detalle: %s\n", https.errorToString(code).c_str());
    https.end();
    return false;
  } else {
    Serial.printf(" ⚠️ (código inesperado)\n");
    https.end();
    return false;
  }
  
  // Obtener respuesta
  String payload = https.getString();
  https.end();
  
  Serial.println("\n📥 Respuesta recibida:");
  Serial.printf("   Longitud: %d bytes\n", payload.length());
  Serial.println("┌────────────────────────────────────┐");
  Serial.println(payload);
  Serial.println("└────────────────────────────────────┘");
  
  // Parsear JSON
  DynamicJsonDocument res(512);
  DeserializationError err = deserializeJson(res, payload);
  
  if (err) {
    Serial.println("❌ Error parseando JSON de respuesta:");
    Serial.printf("   %s\n", err.c_str());
    return false;
  }
  Serial.println("✅ JSON parseado correctamente");

  // Extraer token
  if (res.containsKey("access_token")) {
    jwtToken = res["access_token"].as<String>();
    Serial.printf("🎟️ Token obtenido (longitud: %d chars)\n", jwtToken.length());
    Serial.printf("   Primeros 30 chars: %s...\n", jwtToken.substring(0, min(30, (int)jwtToken.length())).c_str());
  } else {
    Serial.println("❌ Respuesta no contiene campo 'access_token'");
    Serial.println("   Campos disponibles:");
    for (JsonPair kv : res.as<JsonObject>()) {
      Serial.printf("   - %s\n", kv.key().c_str());
    }
    return false;
  }
  
  // Extraer expiración
  if (res.containsKey("expires_in")) {
    unsigned long expiresIn = res["expires_in"].as<unsigned long>();
    tokenExpirationTime = millis() + (expiresIn * 1000); // Convertir a ms
    Serial.printf("⏰ Token expira en: %lu segundos\n", expiresIn);
    Serial.printf("   Timestamp expiración: %lu ms\n", tokenExpirationTime);
  } else {
    Serial.println("⚠️ Respuesta no contiene 'expires_in', usando 24h por defecto");
    tokenExpirationTime = millis() + (24UL * 60UL * 60UL * 1000UL);
  }
  
  // Guardar en NVS
  Serial.println("\n💾 Guardando en NVS...");
  prefs.begin("auth", false);
  prefs.putString("jwt", jwtToken);
  prefs.putULong("exp", tokenExpirationTime);
  prefs.end();
  Serial.println("✅ Token guardado en NVS");
  
  Serial.println("\n╚════════════════════════════════════╝\n");
  return true;
}


// Función que asegura tener un token JWT válido
String ensureToken() {
  Serial.println("\n🔍 Verificando token JWT...");
  // Verificar si el token existe y no ha expirado
  if (jwtToken.length() > 0 && millis() < tokenExpirationTime) {
    unsigned long timeLeft = (tokenExpirationTime - millis()) / 1000;
    Serial.printf("✅ Token válido (expira en %lu segundos)\n", timeLeft);
    return jwtToken;
  }
  
  if (jwtToken.length() > 0) {
    Serial.println("⚠️ Token expirado, renovando...");
  } else {
    Serial.println("⚠️ No hay token en memoria, verificando NVS...");
  }
  
  // Intentar cargar desde NVS
  prefs.begin("auth", true);
  String storedToken = prefs.getString("jwt", "");
  unsigned long storedExp = prefs.getULong("exp", 0);
  prefs.end();
  
  if (storedToken.length() > 0) {
    Serial.println("📦 Token encontrado en NVS");
    Serial.printf("   Longitud: %d chars\n", storedToken.length());
    Serial.printf("   Expira en timestamp: %lu ms\n", storedExp);
    
    if (millis() < storedExp) {
      unsigned long timeLeft = (storedExp - millis()) / 1000;
      Serial.printf("✅ Token de NVS válido (expira en %lu segundos)\n", timeLeft);
      jwtToken = storedToken;
      tokenExpirationTime = storedExp;
      return jwtToken;
    } else {
      Serial.println("⚠️ Token de NVS expirado");
    }
  } else {
    Serial.println("⚠️ No hay token en NVS");
  }
  
  // Obtener nuevo token
  Serial.println("🔄 Solicitando nuevo token al servidor...");
  if (fetchDeviceToken()) {
    Serial.println("✅ Token obtenido exitosamente");
    return jwtToken;
  }
  
  Serial.println("❌ No se pudo obtener token");
  return "";
}