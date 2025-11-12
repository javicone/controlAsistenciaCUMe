
unsigned long lastWiFiCheck = 0;
const unsigned long WIFI_CHECK_INTERVAL = 10000; // 10 segundos
int wifiReconnectAttempts = 0;
const int MAX_WIFI_ATTEMPTS = 15;

// Manejador de eventos de WiFi
void onWiFiEvent(WiFiEvent_t event) {
  switch(event) {
    case IP_EVENT_STA_GOT_IP:
      Serial.println("✅ WiFi conectado");
      Serial.print("IP: ");
      Serial.println(WiFi.localIP());
      wifiReconnectAttempts = 0;
      // Sincronizar NTP tras reconectar
      configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
      break;
      
    case WIFI_EVENT_STA_DISCONNECTED:
      Serial.println("❌ WiFi desconectado");
      wifiReconnectAttempts++;
      break;
      
    case IP_EVENT_STA_LOST_IP:
      Serial.println("⚠️ IP perdida");
      break;
  }
}
// Configurar eventos de WiFi
void setupWiFiEvents() {
  WiFi.onEvent(onWiFiEvent);
}

// Intentar reconectar WiFi si está desconectado
bool reconnectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  
  Serial.println("⚠️ WiFi desconectado, reconectando...");
  WiFi.reconnect();
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < MAX_WIFI_ATTEMPTS) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi reconectado");
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
    wifiReconnectAttempts = 0;
    return true;
  }
  
  Serial.println("\n❌ No se pudo reconectar WiFi");
  wifiReconnectAttempts++;
  return false;
}

void checkWiFiConnection() {
  if (millis() - lastWiFiCheck >= WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = millis();
    
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("⚠️ WiFi desconectado, intentando reconectar...");
      if (reconnectWiFi()) {
        // Reconnect WebSocket
        connectWS();
      }
    }
  }
}