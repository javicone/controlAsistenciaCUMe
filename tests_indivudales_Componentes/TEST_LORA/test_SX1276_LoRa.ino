/*
 * TEST SX1276 LoRa Module
 * 
 * Prueba básica del módulo SX1276 LoRa
 * - Inicialización del módulo
 * - Envío de mensajes cada 5 segundos
 * - Recepción de mensajes
 * 
 * Pines de conexión (Bus SPI compartido con PN532):
 * SCK   -> GPIO 18 (compartido, SEGURO)
 * MISO  -> GPIO 19 (compartido, SEGURO)
 * MOSI  -> GPIO 23 (compartido, SEGURO)
 * CS    -> GPIO 13 (dedicado LoRa, SEGURO sin restricciones)
 * RST   -> GPIO 14 (SEGURO, reasignado de LED Amarillo)
 * DIO0  -> GPIO 27 (SEGURO, reasignado de LED Verde)
 * 
 * Librería requerida: LoRa by Sandeep Mistry
 * Instalación: Arduino IDE -> Tools -> Manage Libraries -> Buscar "LoRa"
 */

#include <SPI.h>
#include <LoRa.h>

// Definición de pines (Bus SPI compartido con PN532)
#define LORA_SCK    18  // Compartido con PN532 (GPIO 18)
#define LORA_MISO   19  // Compartido con PN532 (GPIO 19)
#define LORA_MOSI   23  // Compartido con PN532 (GPIO 23)
#define LORA_CS     13  // Dedicado - SEGURO sin restricciones (GPIO 13)
#define LORA_RST    14  // Reset - Reasignado de LED Amarillo (GPIO 14)
#define LORA_DIO0   27  // Interrupt - Reasignado de LED Verde (GPIO 27)

// Frecuencia LoRa (868 MHz para Europa, 915 MHz para América)
#define LORA_FREQUENCY 868E6  // Cambiar a 915E6 si estás en América

int messageCounter = 0;
unsigned long lastSendTime = 0;
const long SEND_INTERVAL = 5000;  // Enviar cada 5 segundos

void setup() {
  // Inicializar Serial
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println("\n=================================");
  Serial.println("  TEST SX1276 LoRa Module");
  Serial.println("=================================\n");

  // Configurar pines SPI
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
  
  // Configurar LoRa
  LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
  
  Serial.println("Iniciando módulo LoRa...");
  
  // Inicializar LoRa con la frecuencia especificada
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("❌ ERROR: No se pudo iniciar el módulo LoRa");
    Serial.println("Verifica las conexiones:");
    Serial.println("  - VCC -> 3.3V");
    Serial.println("  - GND -> GND");
    Serial.println("  - SCK -> GPIO 18 (compartido con PN532)");
    Serial.println("  - MISO -> GPIO 19 (compartido con PN532)");
    Serial.println("  - MOSI -> GPIO 23 (compartido con PN532)");
    Serial.println("  - CS -> GPIO 13 (dedicado - SEGURO)");
    Serial.println("  - RST -> GPIO 14 (reasignado de LED Amarillo)");
    Serial.println("  - DIO0 -> GPIO 27 (reasignado de LED Verde)");
    while (1);  // Detener ejecución
  }
  
  // Configurar parámetros LoRa
  LoRa.setSpreadingFactor(7);        // SF7 a SF12 (mayor = más alcance, menor velocidad)
  LoRa.setSignalBandwidth(125E3);    // 125 kHz
  LoRa.setCodingRate4(5);            // 4/5 coding rate
  LoRa.setPreambleLength(8);         // Preámbulo de 8 símbolos
  LoRa.setSyncWord(0x12);            // Palabra de sincronización
  LoRa.enableCrc();                  // Habilitar CRC
  
  // Configurar potencia de transmisión (2-20 dBm)
  LoRa.setTxPower(17, PA_OUTPUT_PA_BOOST_PIN);
  
  Serial.println("✅ Módulo LoRa iniciado correctamente");
  Serial.print("Frecuencia: ");
  Serial.print(LORA_FREQUENCY / 1E6);
  Serial.println(" MHz");
  Serial.println("Spreading Factor: 7");
  Serial.println("Ancho de banda: 125.0 kHz");
  Serial.println("\n=================================");
  Serial.println("Iniciando prueba de TX/RX...");
  Serial.println("=================================\n");
}

void loop() {
  // Enviar mensaje periódicamente
  if (millis() - lastSendTime > SEND_INTERVAL) {
    sendLoRaMessage();
    lastSendTime = millis();
  }
  
  // Intentar recibir mensajes
  receiveLoRaMessage();
  
  delay(10);  // Pequeño delay para no saturar el CPU
}

void sendLoRaMessage() {
  messageCounter++;
  
  String message = "Mensaje #" + String(messageCounter) + " desde ESP32";
  
  Serial.println("📤 ENVIANDO:");
  Serial.print("   Contenido: ");
  Serial.println(message);
  
  // Comenzar paquete
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();
  
  Serial.println("   ✅ Mensaje enviado");
  Serial.println();
}

void receiveLoRaMessage() {
  // Verificar si hay paquetes disponibles
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    Serial.println("📥 MENSAJE RECIBIDO:");
    Serial.print("   Tamaño: ");
    Serial.print(packetSize);
    Serial.println(" bytes");
    
    // Leer paquete
    String receivedMessage = "";
    while (LoRa.available()) {
      receivedMessage += (char)LoRa.read();
    }
    
    Serial.print("   Contenido: ");
    Serial.println(receivedMessage);
    
    // Obtener RSSI (Received Signal Strength Indicator)
    Serial.print("   RSSI: ");
    Serial.print(LoRa.packetRssi());
    Serial.println(" dBm");
    
    // Obtener SNR (Signal to Noise Ratio)
    Serial.print("   SNR: ");
    Serial.print(LoRa.packetSnr());
    Serial.println(" dB");
    
    // Obtener frecuencia de error
    Serial.print("   Error de frecuencia: ");
    Serial.print(LoRa.packetFrequencyError());
    Serial.println(" Hz");
    
    Serial.println();
  }
}

/*
 * GUÍA DE USO:
 * 
 * 1. Conectar el módulo SX1276 según el diagrama de pines
 *    IMPORTANTE: El bus SPI (SCK, MISO, MOSI) es compartido con el PN532
 *    Solo el pin CS (GPIO 15) es exclusivo para el SX1276
 * 
 * 2. Instalar la librería "LoRa" de Sandeep Mistry:
 *    Arduino IDE -> Tools -> Manage Libraries -> Buscar "LoRa" -> Instalar
 * 
 * 3. Subir este sketch al ESP32
 * 
 * 4. Abrir el Serial Monitor (115200 baud)
 * 
 * 5. Deberías ver:
 *    - Mensaje de inicialización exitosa
 *    - Mensajes enviados cada 5 segundos
 *    - Si tienes otro módulo LoRa cerca, verás mensajes recibidos
 * 
 * PRUEBA CON DOS MÓDULOS:
 * - Sube este mismo sketch a dos ESP32 con módulos LoRa
 * - Cada uno enviará y recibirá mensajes del otro
 * - Verifica el RSSI (señal) y SNR (calidad)
 * 
 * NOTAS IMPORTANTES:
 * - DIO1 y DIO2 NO son necesarios para operación básica
 * - Solo DIO0 se usa para interrupciones de recepción
 * - El bus SPI soporta múltiples dispositivos (PN532 y SX1276)
 * - Cada dispositivo debe tener su propio pin CS
 * 
 * INFORMACIÓN DE PINES:
 * 
 * Los pines elegidos (13, 14, 27) son SEGUROS para ESP32 WROOM:
 * - GPIO 13: Sin restricciones de bootstrap (seguro para CS)
 * - GPIO 14: Usado como LED Amarillo pero reasignable
 * - GPIO 27: Usado como LED Verde pero reasignable
 * - GPIO 18, 19, 23: Bus SPI compartido (seguro con múltiples devices)
 * 
 * SOLUCIÓN DE PROBLEMAS:
 * 
 * "No se pudo iniciar el módulo LoRa":
 *   - Verifica las conexiones (especialmente CS, RST, DIO0)
 *   - Verifica que el módulo tenga 3.3V (NO 5V)
 *   - Verifica que los cables SPI sean cortos (<20cm)
 *   - Si tienes el PN532 conectado, desconéctalo temporalmente
 *   - Los pines elegidos son seguros en ESP32 WROOM Freenove
 * 
 * "No recibo mensajes":
 *   - Verifica que ambos módulos usen la misma frecuencia
 *   - Verifica que ambos usen el mismo Spreading Factor
 *   - Verifica que la antena esté conectada
 *   - Aumenta la potencia de transmisión (setTxPower)
 * 
 * "RSSI muy bajo (<-120 dBm)":
 *   - Acerca los módulos
 *   - Verifica la antena
 *   - Aumenta la potencia de transmisión
 *   - Aumenta el Spreading Factor (mejor sensibilidad)
 */
