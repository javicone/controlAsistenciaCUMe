void initSensores() {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  setupNFC();  //Inicializamos el lector NFC
  setupRadar();  //Inicializamos el radar de presencia
  setupBME();  //Inicializamos el sensor de temperatura, humedad y presión
  lightMeter.begin();
  Serial.println(F("BH1750 Test begin"));
  Serial.setDebugOutput(true);
}