// ...existing code...
void setupNFC() {
  Serial.println("Inicializando PN532 (SPI) con diagnóstico...");
  boolean nfc_present;
  // Asegúrate de inicializar SPI con los pines correctos si usas pines no por defecto
  // SPI.begin(SCK, MISO, MOSI); // Descomenta y ajusta si usas pines distintos

  // Forzar CS HIGH antes de iniciar
  pinMode(PN532_SS, OUTPUT);
  digitalWrite(PN532_SS, HIGH);
  delay(10);

  // Intentar inicializar varias veces
  const int max_attempts = 4;
  bool ok = false;
  for (int attempt = 1; attempt <= max_attempts; ++attempt) {
    Serial.printf("Intento PN532 #%d\n", attempt);
    // Llamada de inicialización de la librería
    nfc.begin();        // si tu lib no tiene begin, ajusta según la librería
    delay(50);

    // Intentar leer versión/firmware (método típico Adafruit)
    uint32_t versiondata = 0;
    // Si tu librería usa otro método, reemplaza esta línea
    versiondata = nfc.getFirmwareVersion();

    if (versiondata) {
      Serial.print("PN53x detectado. Version: 0x");
      Serial.println(versiondata, HEX);
      // Configuración SAM (si existe)
      #ifdef UNIT_PN532_HAS_SAMCONFIG
      nfc.SAMConfig();
      #endif
      ok = true;
      break;
    } else {
      Serial.println("No se encontró la placa PN53x en este intento.");
      // togglear CS para intentar "liberar" el bus
      digitalWrite(PN532_SS, LOW);
      delay(10);
      digitalWrite(PN532_SS, HIGH);
      delay(200);
    }
  }

  if (!ok) {
    Serial.println("ERROR: PN53x NO detectado tras varios intentos.");
    Serial.print("PN532_SS definido como: ");
    Serial.println(PN532_SS);
    Serial.println("Verifica wiring, alimentación 3.3V y pines SPI. Comentando NFC temporalmente para continuar.");
    // opcional: establecer flag para saltar lecturas NFC en loop
    nfc_present = false; // declara bool nfc_present globalmente y úsalo en leerNFC()
  } else {
    nfc_present = true;
  }
}
// ...existing code...

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