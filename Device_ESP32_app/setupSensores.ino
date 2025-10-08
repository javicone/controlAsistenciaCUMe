void initSensores() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  setupNFC();  //Inicializamos el lector NFC
  setupRadar();  //Inicializamos el radar de presencia
  setupBME();  //Inicializamos el sensor de temperatura, humedad y presión
  setupLightMeter();  //Inicializamos el sensor de luz
  Serial.setDebugOutput(true);
}