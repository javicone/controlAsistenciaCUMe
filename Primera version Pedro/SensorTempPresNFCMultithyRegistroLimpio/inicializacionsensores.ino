void initSensores() {

  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  nfc.begin();  //Comienza la comunicación del PN532

  uint32_t versiondata = nfc.getFirmwareVersion();  //Obtiene información de la placa

  if (!versiondata) {  //Si no se encuentra comunicación con la placa --->
    Serial.print("No se encontró la placa PN53x");
    while (1)
      ;  // Detener
  }
  Serial.print("Chip encontrado PN5");
  Serial.println((versiondata >> 24) & 0xFF, HEX);  //Imprime en el serial que version de Chip es el lector
  Serial.print("Firmware ver. ");
  Serial.print((versiondata >> 16) & 0xFF, DEC);  // Imprime que versión de firmware tiene la placa
  Serial.print('.');
  Serial.println((versiondata >> 8) & 0xFF, DEC);

  //Establezca el número máximo de reintentos para leer de una tarjeta.
  //Esto evita que tengamos que esperar eternamente por una tarjeta,
  //que es el comportamiento predeterminado del PN532.
  nfc.setPassiveActivationRetries(0xFF);

  nfc.SAMConfig();  //Configura la placa para realizar la lectura

  Serial.println("Esperando una tarjeta ISO14443A ...");

  RADAR_SERIAL.begin(256000, SERIAL_8N1, RADAR_RX_PIN, RADAR_TX_PIN);  //UART for monitoring the radar
  delay(500);

  Serial.print(F("\nConnect LD2410 radar TX to GPIO:"));
  Serial.println(RADAR_RX_PIN);
  Serial.print(F("Connect LD2410 radar RX to GPIO:"));
  Serial.println(RADAR_TX_PIN);
  Serial.print(F("LD2410 radar sensor initialising: "));


  if (radar.begin(RADAR_SERIAL)) {
    Serial.println(F("OK"));
    Serial.print(F("LD2410 firmware version: "));
    Serial.print(radar.firmware_major_version);
    Serial.print('.');
    Serial.print(radar.firmware_minor_version);
    Serial.print('.');
    Serial.println(radar.firmware_bugfix_version, HEX);
  } else {
    Serial.println(F("not connected"));
  }

  Serial.println(F("BME280 test"));
  status = bme.begin(0x76);
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1)
      ;
  }

  Serial.println("-- Default Test --");

  Serial.println();

  lightMeter.begin();

  Serial.println(F("BH1750 Test begin"));
  Serial.setDebugOutput(true);
}