
#ifndef CONFIG_H
#define CONFIG_H

// ============================================
// DECLARACIONES (solo "extern" - definidas en globals.cpp)
// ============================================

// ID del dispositivo y API Key segura
extern String deviceId;
extern String apiKey;

// WiFi y servidor
extern const char* ssid;
extern const char* password;

// Configuración WebSocket Seguro (WSS) - Librería WebSocketsClient
extern const char* wsHost;
extern const int wsPort;
extern const char* wsPath;

// Configuración para HTTP (usado en algunas funciones)
extern const char* serverUrl;
extern const char* datos_aula;
extern const char* registro;
extern const char* clases_actual;

// --- Certificado del Servidor (Root CA Certificate) ---
extern const char* server_certificate;

// Zona horaria
extern const char* tzInfo;

// Aula
extern String aula;

// ============================================
// CONSTANTES DE TIEMPO
// ============================================
#define QUEUE_PROCESS_INTERVAL 30000  // 30 segundos
#define TOKEN_CHECK_INTERVAL  43200000 // 12 horas (12 * 60 * 60 * 1000 ms)

// ============================================
// PINES (constantes que NO cambian - usamos #define)
// ============================================
#define RELAY_PIN_1         26
#define RELAY_PIN_2         32
#define BUZZER_PIN          33

#define LED_ROJO_PIN        25
#define LED_VERDE_PIN       27
#define LED_AMARILLO_PIN    14

#define OLED_SDA_PIN        21
#define OLED_SCL_PIN        22
#define OLED_RESET_PIN      -1  // -1 si no tiene pin RESET (compartido con ESP32)
// Dirección I2C de la pantalla (típicamente 0x3C o 0x3D)
#define OLED_I2C_ADDRESS    0x3C

// Constantes de sensores
#define SEALEVELPRESSURE_HPA (1013.25)
#define RADAR_RX_PIN 16
#define RADAR_TX_PIN 17

// Conexiones SPI del ESP32
#define PN532_SCK           (18)
#define PN532_MOSI          (23)
#define PN532_MISO          (19)  
#define PN532_SS            (5)
#define PN532_IRQ           (34)

// ============================================
// COMPATIBILIDAD (para código antiguo que use const int)
// ============================================
const int relayPin1 = RELAY_PIN_1;
const int relayPin2 = RELAY_PIN_2;
const int buzzerPin = BUZZER_PIN;
const int ledRojoPin = LED_ROJO_PIN;
const int ledVerdePin = LED_VERDE_PIN;
const int ledAmarilloPin = LED_AMARILLO_PIN;

#endif // CONFIG_H