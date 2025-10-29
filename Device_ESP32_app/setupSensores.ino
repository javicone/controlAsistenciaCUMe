void initSensores() {
  Serial.println("\n╔════════════════════════════════╗");
  Serial.println("║  INICIALIZACIÓN DE SENSORES    ║");
  Serial.println("╚════════════════════════════════╝\n");

  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  setupNFC();  //Inicializamos el lector NFC
  setupRadar();  //Inicializamos el radar de presencia
  setupBME();  //Inicializamos el sensor de temperatura, humedad y presión
  setupLightMeter();  //Inicializamos el sensor de luz
  Serial.setDebugOutput(false); // Desactivar salida de depuración para evitar interferencias I2C

    // Mostrar resumen
  Serial.println("\n=== RESUMEN INICIALIZACIÓN ===");
  Serial.printf("BME280: %s\n", sensores.bme280_ok ? "✅" : "❌");
  Serial.printf("BH1750: %s\n", sensores.bh1750_ok ? "✅" : "❌");
  Serial.printf("LD2410: %s\n", sensores.ld2410_ok ? "✅" : "❌");
  Serial.printf("PN532:  %s\n", sensores.pn532_ok ? "✅" : "❌");
  Serial.println("==============================\n");
  
  // Indicar estado inicial
  if(sensores.bme280_ok && sensores.bh1750_ok && 
     sensores.ld2410_ok && sensores.pn532_ok) {
    indicarEstado(NORMAL);
  } else {
    indicarEstado(ADVERTENCIA);
  }
}