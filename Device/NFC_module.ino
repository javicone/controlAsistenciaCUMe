void setupNFC() {
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
}

void leerNFC() {
  //Recepción y detección de los datos de la tarjeta y almacenamiento en la variable "LeeTarjeta"
  LeeTarjeta = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, &uid[0], &LongitudUID, 1000);

  //Se detecto un tarjeta RFID
  if (LeeTarjeta) {
    Serial.println("Tarjeta encontrada!");
    Serial.print("Longitud del UID: ");
    Serial.print(LongitudUID, DEC);  //Imprime la longitud de los datos de la tarjeta en decimal
    Serial.println(" bytes");
    Serial.print("Valor del UID: ");
    // Imprime los datos almacenados en la tarjeta en Hexadecimal
    for (uint8_t i = 0; i < LongitudUID; i++) {
      Serial.print(" 0x");
      Serial.print(uid[i], HEX);
    }
    Serial.println("");
    registrarAsistencia();
    //delay (1000); // Espera de 1 segundo
  }

  //Si no se detecta tarjeta
  else {
    Serial.println("Se agotó el tiempo de espera de una tarjeta");
  }
}