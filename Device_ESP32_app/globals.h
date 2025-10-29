#ifndef GLOBALS_H
#define GLOBALS_H

#include <Arduino.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <ld2410.h>
#include "UNIT_PN532.h"
#include <WebSocketsClient.h>

// ============================================
// TIMERS
// ============================================
extern unsigned long lastReading;
extern unsigned long lastReading2;
extern unsigned long lastReading3;
extern const unsigned long delayTime;
extern const unsigned long delayTime2;

// ============================================
// ESTADO DE SENSORES
// ============================================
struct SensorStatus {
  bool bme280_ok = false;
  bool bh1750_ok = false;
  bool ld2410_ok = false;
  bool pn532_ok = false;
  uint8_t bme280_errores = 0;
  uint8_t bh1750_errores = 0;
  uint8_t ld2410_errores = 0;
  uint8_t pn532_errores = 0;
};

extern SensorStatus sensores;

// ============================================
// WEBSOCKET
// ============================================
extern bool wsConectado;
extern WebSocketsClient webSocket;

// ============================================
// INSTANCIAS DE SENSORES
// ============================================
extern Adafruit_BME280 bme;
extern BH1750 lightMeter;
extern ld2410 radar;
extern UNIT_PN532 nfc;

// ============================================
// PINES
// ============================================
extern const int ledRojoPin;
extern const int ledVerdePin;
extern const int ledAmarilloPin;
extern const int buzzerPin;
extern const int relayPin;

// ============================================
// ESTADOS DE LEDs
// ============================================
enum EstadoLED {
  NORMAL,
  ADVERTENCIA,
  ERROR,
  CRITICO
};

// ============================================
// FUNCIONES DE INDICADORES (implementadas en indicators.ino)
// ============================================
void setupIndicators();
void testIndicadores();
void indicarEstado(EstadoLED estado);
void parpadearLED(int pin, int veces, int duracion_ms);

// Control del relé
void activarRele(bool estado);
bool estadoRele();

// Control individual de LEDs
void ledVerde(bool estado);
void ledAmarillo(bool estado);
void ledRojo(bool estado);

// Funciones de buzzer
void beep(int frecuencia, int duracion);
void beepCorto();
void beepLargo();
void beepError();

// Secuencias especiales
void secuenciaInicio();
void secuenciaError();
void secuenciaExito();
void apagarTodosLosIndicadores();

#endif