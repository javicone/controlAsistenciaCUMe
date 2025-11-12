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