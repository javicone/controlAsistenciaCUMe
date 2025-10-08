
#ifndef CONFIG_H
#define CONFIG_H

// WiFi y servidor
const char* ssid = "Nothing";
const char* password = "12345678";
const char* wsHost = "10.39.217.94";
const int wsPort = 5678;
const char* wsPath = "/";
const char* serverUrl = "http://10.39.217.94:5000";
const char* datos_aula = "/datos_aula";
const char* registro = "/registro";

// Zona horaria
const char* tzInfo = "CET-1CEST,M3.5.0/2,M10.5.0/3";

// Aula y pines
const char* aula = "Aula 101";
const int relayPin = 26;

// Constantes de sensores
#define SEALEVELPRESSURE_HPA (1013.25)
#define RADAR_RX_PIN 16
#define RADAR_TX_PIN 17
#define RADAR_SERIAL Serial1

// Conexiones SPI del ESP32
#define PN532_SCK (18)
#define PN532_MOSI (23)
#define PN532_SS (5)

#endif // CONFIG_H