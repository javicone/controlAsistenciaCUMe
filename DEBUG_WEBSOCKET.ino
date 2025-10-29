// 🔍 CÓDIGO DE DEBUG AVANZADO PARA beginSSL()
// Añadir esto ANTES de webSocket.beginSSL() en Device_ESP32_app.ino
public void debugWebSocketSSL() {
// 1. Verificar WiFi
Serial.println("\n🔍 === DIAGNÓSTICO WEBSOCKET ===");
Serial.print("📶 WiFi conectado: ");
Serial.println(WiFi.status() == WL_CONNECTED ? "SÍ ✅" : "NO ❌");
Serial.print("📶 Señal WiFi (RSSI): ");
Serial.print(WiFi.RSSI());
Serial.println(" dBm");
Serial.print("🌐 IP local: ");
Serial.println(WiFi.localIP());

// 2. Verificar DNS/conectividad
Serial.print("🔍 Resolviendo host: ");
Serial.println(wsHost);
IPAddress serverIP;
if (WiFi.hostByName(wsHost, serverIP)) {
  Serial.print("✅ IP resuelta: ");
  Serial.println(serverIP);
} else {
  Serial.println("❌ No se pudo resolver DNS");
}

// 3. Test de conectividad TCP básica
WiFiClient testClient;
Serial.print("🔍 Probando conexión TCP a ");
Serial.print(wsHost);
Serial.print(":");
Serial.println(wsPort);
if (testClient.connect(wsHost, wsPort)) {
  Serial.println("✅ Conexión TCP exitosa");
  testClient.stop();
} else {
  Serial.println("❌ No se puede conectar por TCP");
}

// 4. Verificar certificado (si se usa)
Serial.println("🔍 Certificado SSL:");
Serial.print("  - Tamaño: ");
Serial.print(strlen(server_certificate));
Serial.println(" bytes");
Serial.print("  - Comienza con: ");
Serial.println(String(server_certificate).substring(0, 30));

// 5. Verificar memoria
Serial.print("🧠 Memoria libre: ");
Serial.print(ESP.getFreeHeap());
Serial.println(" bytes");
Serial.println("🔍 === FIN DIAGNÓSTICO ===\n");

// AHORA SÍ, llamar a beginSSL()...
}