#include <Preferences.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <time.h> // Necesario para time()

Preferences prefs;
String jwtToken = "";

// Variable para almacenar el timestamp absoluto de expiración (Unix Time)
// Ejemplo: 1715095600 (equivale a una fecha/hora concreta)
uint64_t tokenExpirationTimestamp = 0; 

// Función auxiliar para verificar si el reloj está sincronizado
bool isTimeSet() {
  time_t now;
  time(&now);
  struct tm timeinfo;
  localtime_r(&now, &timeinfo);
  // Si el año es menor a 2020, asumimos que no se ha sincronizado (está en 1970)
  return timeinfo.tm_year > (2020 - 1900);
}

// Función para obtener el token JWT desde el servidor
bool fetchDeviceToken() {
  Serial.println("\n╔════════════════════════════════════╗");
  Serial.println("║ 🔐 OBTENIENDO TOKEN JWT            ║");
  Serial.println("╚════════════════════════════════════╝");
  
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi no conectado");
    return false;
  }

  // 1. IMPORTANTE: Verificar que tenemos la hora antes de pedir token
  // Si no tenemos hora, los cálculos de expiración serán erróneos
  if (!isTimeSet()) {
    Serial.println("⚠️ Hora no sincronizada. Intentando sincronizar NTP...");
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    delay(2000); // Dar un poco de tiempo
    if(!isTimeSet()) {
       Serial.println("❌ Error: No se pudo sincronizar la hora. No se puede calcular expiración.");
       // Podrías decidir continuar sin guardar persistencia o retornar false
    }
  }
  
  WiFiClientSecure client;
  client.setInsecure(); 
  HTTPClient https;
  
  String url = String(serverUrl) + "/auth/device";
  
  if (!https.begin(client, url)) {
    Serial.println("❌ Error de conexión");
    return false;
  }
  
  https.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  doc["device_id"] = deviceId;
  doc["api_key"] = apiKey;
  String body;
  serializeJson(doc, body);
  
  int code = https.POST(body);
  
  if (code == 200) {
    String payload = https.getString();
    DynamicJsonDocument res(1024); // Aumentado un poco el buffer por seguridad
    deserializeJson(res, payload);
    
    if (res.containsKey("access_token")) {
      jwtToken = res["access_token"].as<String>();
      
      // 2. CÁLCULO DE EXPIRACIÓN ABSOLUTA
      if (res.containsKey("expires_in")) {
        unsigned long expiresInSeconds = res["expires_in"].as<unsigned long>();
        
        // Obtenemos la hora actual (Unix timestamp)
        time_t now;
        time(&now);
        
        // Calculamos el momento exacto en el futuro donde caduca
        tokenExpirationTimestamp = (uint64_t)now + expiresInSeconds;
        
        Serial.printf("⏰ Token válido por: %lu segundos\n", expiresInSeconds);
        Serial.printf("📅 Fecha actual (Unix): %lld\n", (uint64_t)now);
        Serial.printf("📅 Fecha expiración (Unix): %lld\n", tokenExpirationTimestamp);
        
      } else {
        // Fallback si no viene expires_in
        time_t now; 
        time(&now);
        tokenExpirationTimestamp = (uint64_t)now + 86400; // 24 horas
      }

      // 3. GUARDADO EN NVS
      // Usamos putULong64 si tu versión de ESP32 board lo soporta (recomendado para timestamps)
      // O guardamos como String si no quieres líos con tipos de datos, o putULong (cuidado año 2038)
      prefs.begin("auth", false);
      prefs.putString("jwt", jwtToken);
      prefs.putULong64("exp_ts", tokenExpirationTimestamp); // Guardamos el timestamp absoluto
      prefs.end();
      
      Serial.println("✅ Token y expiración guardados correctamente");
      https.end();
      return true;
    }
  } 
  
  Serial.printf("❌ Error obteniendo token: %d\n", code);
  https.end();
  return false;
}

String ensureToken() {
  Serial.println("\n🔍 Verificando estado del token...");

  // 1. Obtener hora actual
  if (!isTimeSet()) {
      Serial.println("⚠️ Reloj no sincronizado. Sincronizando NTP...");
      configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
      // Pequeña espera bloqueante o lógica para reintentar luego
      delay(1000); 
  }

  time_t now;
  time(&now);
  uint64_t currentTimestamp = (uint64_t)now;

  // 2. Verificar variable en memoria RAM primero
  // Añadimos un margen de seguridad (buffer) de 60 segundos
  if (jwtToken.length() > 0 && currentTimestamp < (tokenExpirationTimestamp - 60)) {
     Serial.println("✅ Token en RAM válido.");
     return jwtToken;
  }

  // 3. Si no está en RAM o expiró, miramos NVS
  prefs.begin("auth", true);
  String storedToken = prefs.getString("jwt", "");
  uint64_t storedExp = prefs.getULong64("exp_ts", 0);
  prefs.end();

  if (storedToken.length() > 0) {
    // Verificamos contra la hora actual REAL
    if (storedExp > 0 && currentTimestamp < (storedExp - 60)) {
       Serial.printf("📦 Token recuperado de NVS válido.\n");
       Serial.printf("   Expira en %lld segundos\n", (storedExp - currentTimestamp));
       
       // Restauramos a variables globales
       jwtToken = storedToken;
       tokenExpirationTimestamp = storedExp;
       return jwtToken;
    } else {
       Serial.println("⌛ El token guardado en NVS ha expirado (según fecha real).");
    }
  } else {
    Serial.println("⚠️ No hay token en NVS.");
  }

  // 4. Si llegamos aquí, necesitamos uno nuevo
  Serial.println("🔄 Solicitando NUEVO token...");
  if (fetchDeviceToken()) {
    return jwtToken;
  }
  
  return "";
}

void invalidateToken() {
  Serial.println("🗑️ Invalidando token...");
  jwtToken = "";
  tokenExpirationTimestamp = 0;
  
  prefs.begin("auth", false);
  prefs.clear();
  prefs.end();
}