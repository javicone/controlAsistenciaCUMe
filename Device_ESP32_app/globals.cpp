#include "globals.h"
#include "config.h"

// ============================================
// TIMERS
// ============================================
unsigned long lastReading = 0;
unsigned long lastReading2 = 0;
unsigned long lastReading3 = 0;
const unsigned long delayTime = 5000;      // 5 segundos - envío de datos
const unsigned long delayTime2 = 300000;   // 5 minutos - próxima clase

// ============================================
// ESTADO DE SENSORES
// ============================================
SensorStatus sensores;

// ============================================
// WEBSOCKET
// ============================================
bool wsConectado = false;
WebSocketsClient webSocket;

// ============================================
// INSTANCIAS DE SENSORES
// ============================================
Adafruit_BME280 bme;
BH1750 lightMeter;
ld2410 radar;
UNIT_PN532 nfc(PN532_SS);

// ============================================
// PINES (desde config.h)
// ============================================
const int ledRojoPin = LED_ROJO_PIN;
const int ledVerdePin = LED_VERDE_PIN;
const int ledAmarilloPin = LED_AMARILLO_PIN;
const int buzzerPin = BUZZER_PIN;
const int relayPin = RELAY_PIN;