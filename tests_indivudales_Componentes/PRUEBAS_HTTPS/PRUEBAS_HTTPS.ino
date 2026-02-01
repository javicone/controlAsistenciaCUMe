#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// 1. Credenciales de Red
const char* ssid = "SERVER";
const char* password = "12345678";

// 2. URL de la API segura (nota el https://)
const char* serverUrl = "https://api.chucknorris.io/jokes/random";

void setup() {
  Serial.begin(115200);

  // Conexión WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a la red WiFi.");
}

void loop() {
  // Comprobar si hay conexión WiFi
  if (WiFi.status() == WL_CONNECTED) {
    
    // 3. Crear el cliente seguro
    WiFiClientSecure client;
    
    // IMPORTANTE: setInsecure() permite conectarse sin validar el certificado.
    // Es útil para pruebas rápidas, pero menos seguro que usar un certificado CA.
    client.setInsecure();

    // 4. Crear el objeto HTTP
    HTTPClient https;

    Serial.print("[HTTPS] Iniciando conexión...\n");

    // Inicializar conexión pasando el cliente seguro y la URL
    if (https.begin(client, serverUrl)) { 
      
      Serial.print("[HTTPS] Haciendo petición GET...\n");
      
      // Ejecutar la petición
      int httpCode = https.GET();

      // httpCode será negativo si hay error
      if (httpCode > 0) {
        // Si el servidor responde (200 = OK)
        if (httpCode == HTTP_CODE_OK) {
          String payload = https.getString();
          Serial.println("Respuesta del servidor:");
          Serial.println(payload);
        }
      } else {
        Serial.printf("[HTTPS] Falló la petición GET, error: %s\n", https.errorToString(httpCode).c_str());
      }

      // Cerrar la conexión
      https.end();
    } else {
      Serial.printf("[HTTPS] No se pudo conectar al servidor\n");
    }
  }

  Serial.println("Esperando 10 segundos antes de la siguiente petición...");
  delay(10000);
}