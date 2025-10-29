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
struct NFCData {
  String uid;
  bool tarjetaDetectada;
  bool valido;
};

NFCData leerNFC() {
  NFCData datos = {"", false, false};
  
  // Verificar si el sensor está disponible
  if(!sensores.pn532_ok) {
    Serial.println("⚠️ PN532 no disponible, reintentando...");
    if(!setupNFC()) {
      return datos;
    }
  }
  
  uint8_t success;
  uint8_t uid_local[] = {0, 0, 0, 0, 0, 0, 0};
  uint8_t uidLength;
  
  // Leer tarjeta (timeout 500ms - balance entre responsividad y detección)
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid_local, &uidLength, 500);
  
  if(success) {
    // Validar longitud de UID (típicamente 4 o 7 bytes)
    if(uidLength != 4 && uidLength != 7) {
      Serial.printf("❌ UID longitud inválida: %d bytes\n", uidLength);
      return datos;
    }
    
    // Log detallado
    Serial.print("✅ Tarjeta detectada - UID (");
    Serial.print(uidLength);
    Serial.print(" bytes): ");
    for(uint8_t i = 0; i < uidLength; i++) {
      Serial.print("0x");
      if(uid_local[i] < 0x10) Serial.print("0");
      Serial.print(uid_local[i], HEX);
      Serial.print(" ");
    }
    Serial.println();
    
    // Convertir UID a String
    datos.uid = uidToString(uid_local, uidLength);
    
    // Validar que no esté vacío
    if(datos.uid.length() == 0) {
      Serial.println("❌ UID vacío tras conversión");
      return datos;
    }
    
    datos.tarjetaDetectada = true;
    datos.valido = true;
    
    Serial.println("UID String: " + datos.uid);
  }
  
  return datos;
}