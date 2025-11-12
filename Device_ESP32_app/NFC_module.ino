#include "globals.h"

bool setupNFC() {
  Serial.println("🔧 Inicializando PN532 (SPI) con diagnóstico...");
  
  // ✅ Inicializar SPI con pines explícitos
  SPI.begin(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);
  
  // Forzar CS HIGH antes de iniciar (PN532 inactivo)
  pinMode(PN532_SS, OUTPUT);
  digitalWrite(PN532_SS, HIGH);
  delay(10);

  // Intentar inicializar varias veces
  const int max_attempts = 4;
  bool ok = false;
  
  for (int attempt = 1; attempt <= max_attempts; ++attempt) {
    Serial.printf("📡 Intento PN532 #%d/%d\n", attempt, max_attempts);
    
    nfc.begin();
    delay(100);  // ← Aumentado a 100ms para dar tiempo al chip

    uint32_t versiondata = nfc.getFirmwareVersion();

    if (versiondata) {
      Serial.print("✅ PN53x detectado! Version: 0x");
      Serial.println(versiondata, HEX);
      Serial.print("   Chip: PN5");
      Serial.println((versiondata >> 24) & 0xFF, HEX);
      Serial.print("   Firmware: ");
      Serial.print((versiondata >> 16) & 0xFF, DEC);
      Serial.print(".");
      Serial.println((versiondata >> 8) & 0xFF, DEC);
      
      // Configurar para leer tarjetas MIFARE
      nfc.SAMConfig();
      
      sensores.pn532_ok = true;
      sensores.pn532_errores = 0;
      ok = true;
      break;
    } else {
      Serial.println("❌ No se encontró la placa PN53x en este intento.");
      
      // Togglear CS para intentar "liberar" el bus SPI
      digitalWrite(PN532_SS, LOW);
      delay(10);
      digitalWrite(PN532_SS, HIGH);
      delay(200);
    }
  }

  if (!ok) {
    Serial.println("❌ ERROR CRÍTICO: PN53x NO detectado tras 4 intentos.");
    Serial.println("📋 Diagnóstico:");
    Serial.printf("   - PN532_SS:   GPIO %d\n", PN532_SS);
    Serial.printf("   - PN532_SCK:  GPIO %d\n", PN532_SCK);
    Serial.printf("   - PN532_MISO: GPIO %d\n", PN532_MISO);
    Serial.printf("   - PN532_MOSI: GPIO %d\n", PN532_MOSI);
    Serial.println("🔍 Verifica:");
    Serial.println("   1. Alimentación 3.3V (NO 5V)");
    Serial.println("   2. Cables firmemente conectados");
    Serial.println("   3. Módulo PN532 en modo SPI (switches/jumpers)");
    Serial.println("   4. Pines SPI correctos según tu placa ESP32");
    
    sensores.pn532_ok = false;
    sensores.pn532_errores++;
    return false;
  }
  
  return true;
}


NFCData leerNFC() {
  NFCData datos = {false, false, ""};
  
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
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid_local, &uidLength, 1000);
  
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