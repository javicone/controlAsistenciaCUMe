#include "globals.h"
#include "config.h"

// ============================================
// DEFINICIONES REALES (aquí existe la variable única)
// ============================================

// ID del dispositivo y API Key segura
String deviceId = "node-001";
String apiKey = "A2fP7zU4tD1sH6kE9wR0mN3cQ5vB8xYgO";

// WiFi y servidor
const char* ssid = "SERVER";
const char* password = "12345678";

// Configuración WebSocket Seguro (WSS)
const char* wsHost = "192.168.137.1";
const int wsPort = 5000;
const char* wsPath = "/ws/device";

// Configuración para HTTP
const char* serverUrl = "https://192.168.137.1:5000";
const char* datos_aula = "/datos_aula";
const char* registro = "/asistencias/registro";

// Certificado del Servidor (Root CA Certificate)
const char* server_certificate = \
"-----BEGIN CERTIFICATE-----\n" \
"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\n" \
"hVPNShtnpg==\n" \
"-----END CERTIFICATE-----\n";

// Zona horaria
const char* tzInfo = "CET-1CEST,M3.5.0/2,M10.5.0/3";

// Aula
const char* aula = "Aula 209";

// ============================================
// OBJETOS DE SENSORES
// ============================================
Adafruit_BME280 bme;
BH1750 lightMeter;
ld2410 radar;
Adafruit_PN532 nfc(PN532_SS);  // Solo necesita CS, SPI ya inicializado
WebSocketsClient webSocket;

// ============================================
// VARIABLES DE ESTADO
// ============================================
SensorStatus sensores;

unsigned long lastTokenCheck = 0;


volatile bool nfcCardDetected = false; 

// ============================================
// VARIABLES NFC PARA POLLING (estilo ejemplo oficial)
// ============================================
int nfcIrqCurr = HIGH;
int nfcIrqPrev = HIGH;
bool nfcReaderDisabled = false;
unsigned long nfcTimeLastCardRead = 0;
unsigned long nfcCooldown = 0;

unsigned long lastReading = 0;
unsigned long lastReading2 = 0;
unsigned long lastReading3 = 0;
unsigned long lastQueueProcess = 0;

// Variables de radar
int DistanciaEstatico = 0;
int DistanciaMovil = 0;

// Configuración NTP
const long gmtOffset_sec = 3600;        // GMT+1 (España)
const int daylightOffset_sec = 3600;    // Horario de verano
const char* ntpServer = "pool.ntp.org";

// Variables de tiempo
unsigned long targetTimeMillis = 0;
bool ledRedOn = false;

// WebSocket
bool wsConectado = false;

// Estado de los reles
bool relay1Estado = false;
bool relay2Estado = false;
