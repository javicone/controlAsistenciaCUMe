#ifndef GLOBALS_H
#define GLOBALS_H

#include <Arduino.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <Adafruit_PN532.h> 
#include <ld2410.h>
#include <WebSocketsClient.h>

// ============================================
// DECLARACIONES EXTERNAS (definidas en globals.cpp)
// ============================================

// Configuración del dispositivo
extern String deviceId;
extern String apiKey;

// WiFi y servidor
extern const char* ssid;
extern const char* password;
extern const char* wsHost;
extern const int wsPort;
extern const char* wsPath;
extern const char* serverUrl;
extern const char* datos_aula;
extern const char* registro;
extern const char* server_certificate;
extern const char* tzInfo;
extern const char* aula;

// ============================================
// CONSTANTES DE TIEMPO
// ============================================
#define QUEUE_PROCESS_INTERVAL 30000  // 30 segundos
#define SENSOR_READ_INTERVAL   5000   // 5 segundos 
#define CLASS_CHECK_INTERVAL   5000 // 5 minutos 



// ============================================
// ESTRUCTURAS DE DATOS
// ============================================

// Estructura para estado de sensores
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

struct BME280Data {
  bool valido = false;
  float temperatura = 0.0;
  float humedad = 0.0;
  float presion = 0.0;
};

struct LuzData {
  bool valido = false;
  float lux = 0.0;
};

struct NFCData {
  bool valido = false;
  bool tarjetaDetectada = false;
  String uid = "";
};

struct RadarData {
  bool valido = false;
  int distanciaEstatico = 0;
  int distanciaMovil = 0;
  bool presenciaDetectada = false;
};

// ============================================
// OBJETOS DE SENSORES (definidos en globals.cpp)
// ============================================
extern Adafruit_BME280 bme;
extern BH1750 lightMeter;
extern ld2410 radar;
extern Adafruit_PN532 nfc;
extern WebSocketsClient webSocket;

// ============================================
// VARIABLES DE ESTADO (definidas en globals.cpp)
// ============================================
extern SensorStatus sensores;
extern unsigned long lastReading;
extern unsigned long lastReading2;
extern unsigned long lastReading3;
extern unsigned long lastQueueProcess;
extern int DistanciaEstatico;
extern int DistanciaMovil;
extern const long gmtOffset_sec;
extern const int daylightOffset_sec;
extern const char* ntpServer;
extern unsigned long targetTimeMillis;
extern bool ledRedOn;
extern bool wsConectado;

extern volatile bool nfcCardDetected;

// ============================================
// ESTADOS DE LEDs
// ============================================
enum EstadoLED {
  NORMAL,
  ADVERTENCIA,
  ERROR,
  CRITICO
};

// Token JWT expiracion
extern unsigned long tokenExpirationTime;



// ============================================
// FUNCIONES DE INDICADORES (implementadas en indicators.ino)
// ============================================
void setupIndicators();
void testIndicadores();
void indicarEstado(EstadoLED estado);
void parpadearLED(int pin, int veces, int duracion_ms);

// Control del relé
void activarRele1(bool estado);
void activarRele2(bool estado);
bool estadoRele1();
bool estadoRele2();
// Estados de los relés
extern bool relay1Estado;
extern bool relay2Estado;

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