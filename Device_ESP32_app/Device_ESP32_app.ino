/*********
 Proyecto IoT de sistema de registro de presencia y variables ambientales con fines de registro, seguridad, control domótico...
*********/

//Librerías necesarias
#include <WiFi.h>
#include <WiFiClientSecure.h>  // HTTPS
#include <WiFiUdp.h>
#include <time.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>  // ✅ Librería ORIGINAL para WebSockets con control SSL
//#include "Freenove_WS2812_Lib_for_ESP32.h"
#include <Wire.h>
#include <SPI.h>         //Librería para comunicación SPI
#include "UNIT_PN532.h"  //Librería Modificada
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <ld2410.h>
#include <Preferences.h>
#include "globals.h"
#include "config.h"



// Declaración adelantada
void initSensores();
void HiloComunicadorcode(void* pvParameters);
void leerNFC();
void obtenerProximaClase();
void EnviaValoresAula();
void registrarAsistencia();
String uidToString(byte *uid, unsigned int longitud);
String urlencode(String str);
unsigned long epochFromString(String fecha);
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length);  // ✅ Callback para WebSocketsClient


//Instanciamos clases que usan las librerias de los sensores
Adafruit_BME280 bme;  // I2C
BH1750 lightMeter;
ld2410 radar;
UNIT_PN532 nfc(PN532_SS);  // Línea enfocada para la comunicación por SPI

// Cliente WebSocket (maneja SSL internamente)
WebSocketsClient webSocket;

//Handle del hilo de ejecución que vamos a fijar en el core 0 para llevar el tema de comunicaciones
TaskHandle_t HiloComunicador;

// Set up global del código
void setup() {
  //Inicializo los pines de los LEDs y el buzzer
  pinMode(ledRojoPin, OUTPUT);
  pinMode(ledVerdePin, OUTPUT);
  pinMode(ledAmarilloPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  setupWiFiEvents(); //Configuramos los eventos de WiFi
  //Inicializamos Serial para comunicación en Arduino IDE
  Serial.begin(115200);
  //Inicializamos todos los sensores y actuadores que vamos a utilizar
  initSensores();
  //Creamos la tarea que se ejecutará en el Core 0 con prioridad 1
  xTaskCreatePinnedToCore(
    HiloComunicadorcode, /* Task function. */
    "HiloComunicador",   /* name of task. */
    10000,     /* Stack size of task */
    NULL,      /* parameter of the task */
    1,         /* priority of the task */
    &HiloComunicador,    /* Task handle to keep track of created task */
    0);        /* pin task to core 0 */
  delay(500);
}

//HiloComunicador: Equivale al Loop normal de .ino pero que se ejecutará en el core 0

void HiloComunicadorcode(void* pvParameters) {
  // Conectar a WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Sincronizar hora NTP
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  setenv("TZ", tzInfo, 1);
  tzset();

  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("Esperando NTP...");
    delay(1000);
  }
  Serial.println("Hora sincronizada");

  // Configurar SSL
  Serial.println("\n=== WebSocket SSL ===");
  
  // Configurar WebSocket con SSL
  Serial.print("Conectando WSS: ");
  Serial.print(wsHost);
  Serial.print(":");
  Serial.print(wsPort);
  Serial.println(wsPath);
  
  // Obtener token JWT
  if (!fetchDeviceToken()) {
    Serial.println("Error obteniendo token JWT");
  }
  // Para ESP32, beginSSL configura SSL internamente
  // El último parámetro (fingerprint) puede estar vacío para certificados autofirmados
  connectWS();
  //en caso de q falle usamos conexión no segura
  // Loop WebSocket
  for (;;) {

    // Verificar conexión WiFi y reconectar si es necesario
    checkWiFiConnection();
    webSocket.loop();
    // Procesar cola offline periódicamente
    if (millis() - lastQueueProcess > QUEUE_PROCESS_INTERVAL) {
      lastQueueProcess = millis();
      processQueue();
    }


    vTaskDelay(100 / portTICK_PERIOD_MS); // Increased delay to reduce CPU usage
  }
}

//Loop principal que utilizaremos para toda la lógica de los sensores y actuadores
void loop() {
 // Leer radar con validación
  RadarData radar_data = leerRadar();
  
  if(radar_data.valido && millis() - lastReading > 1000) {
    lastReading = millis();
    
    if(radar_data.presenciaDetectada) {
      DistanciaEstatico = radar_data.distanciaEstatico;
      DistanciaMovil = radar_data.distanciaMovil;
      
      if(DistanciaMovil > 0 && DistanciaMovil < 50) {
        NFCData nfc_data = leerNFC();
        
        if(nfc_data.valido && nfc_data.tarjetaDetectada) {
          registrarAsistencia(nfc_data.uid);
        }
      }
    }
  }

  // Obtener próxima clase
  if (millis() - lastReading3 > delayTime2) {
    lastReading3 = millis();
    obtenerProximaClase();
  }

  // Enviar datos del aula
  if (millis() - lastReading2 > delayTime) {
    lastReading2 = millis();
    EnviaValoresAula();
  }
}