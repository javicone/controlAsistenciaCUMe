/*********
 Proyecto IoT de sistema de regustro de presencia y variables ambientales con fines de registro, seguridad, control domótico...
*********/

//Librerías necesarias
#include <WiFi.h>
#include <WiFiUdp.h>
#include <time.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>
//#include "Freenove_WS2812_Lib_for_ESP32.h"

#include <Wire.h>
#include <SPI.h>         //Librería para comunicación SPI
#include "UNIT_PN532.h"  //Librería Modificada
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <ld2410.h>
#include "pinesyvariablesauxiliares.h"

//Instanciamos clases que usan las librerias de los sensores
Adafruit_BME280 bme;  // I2C
BH1750 lightMeter;
ld2410 radar;
UNIT_PN532 nfc(PN532_SS);  // Línea enfocada para la comunicación por SPI

//Instanciamos la clase websocket que nos va a permitir el intercambio de información bidireccional para el control de relays
WebSocketsClient webSocket;

//Handle del hilo de ejecución que vamos a fijar en el core 0 para llevar el tema de comunicaciones
TaskHandle_t Hilo0;

// Set up global del código
void setup() {

  //Inicializamos Serial para comunicación en Arduino IDE
  Serial.begin(115200);

  //Inicializamos todos los sensores y actuadores que vamos a utilizar
  initSensores();

  //Creamos la tarea que se ejecutará en el Core 0 con prioridad 1
  xTaskCreatePinnedToCore(
    Hilo0code, /* Task function. */
    "Hilo0",   /* name of task. */
    10000,     /* Stack size of task */
    NULL,      /* parameter of the task */
    1,         /* priority of the task */
    &Hilo0,    /* Task handle to keep track of created task */
    0);        /* pin task to core 0 */
  delay(500);
}

//Hilo0code: Equivale al Loop normal de .ino pero que se ejecutará en el core 0
//La idea es reservarla para comunicaciones
void Hilo0code(void* pvParameters) {

  // Inicialización de WiFi y nos conectamos (los datos están en pines y funciones auxiliares)
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(" Conectado!");

  //Nos conectamos a servidor de tiempo para tener la hora correcta
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  setenv("TZ", tzInfo, 1);
  tzset();

  struct tm timeinfo;

  while (!getLocalTime(&timeinfo)) {
    Serial.println("Esperando sincronización NTP...");
    delay(1000);
  }

  Serial.println("Hora sincronizada:");
  Serial.println(&timeinfo, "%c");

  //Obtenemos el token de seguridad que utiulizaremos en todas las comunicaciones
  obtenerToken();  //login de aula

  //Inicializamos el websocket
  webSocket.begin(wsHost, wsPort, wsPath);
  webSocket.onEvent(webSocketEvent);
  Serial.println("✅ WebSocket conectado (puro).");

  //Creamos un bucle infinito dentro de este hilo y así podemos distinguir tareas de
  //inicialización de tareas repetitivas sin meterlo en el Setup
  for (;;) {

    webSocket.loop();

    vTaskDelay(10);  // cede brevemente la CPU al scheduler para que no se bloquee y reduce el uso de recursos
  }

}  //Aquí acaba HiloCode0

//Loop principal que utilizaremos para toda la lógica de los sensores y actuadores
void loop() {

  //leemos el sensor de presencia
  radar.read();
  if (radar.isConnected() && millis() - lastReading > 1000)  //comprueba si está conectado cada 1000ms
  {
    lastReading = millis();
    if (radar.presenceDetected()) {
      // Compruea si hay personas estáticas
      if (radar.stationaryTargetDetected()) {
        //Serial.print(F("Stationary target: "));
        personas = radar.stationaryTargetDistance();
        //Serial.print(personas);
        //Serial.print(F("cm energy:"));
        //Serial.print(radar.stationaryTargetEnergy());
        //Serial.print(' ');
      }
      // Comprueba si hay personas moviéndose
      if (radar.movingTargetDetected()) {
        Serial.print(F("Moving target: "));
        DistanciaMovil = radar.movingTargetDistance();
        Serial.print(DistanciaMovil);
        Serial.print(F("cm energy:"));
        Serial.print(radar.movingTargetEnergy());
        Serial.println();
        //Si la persona que se mueve está a menos de 50 cm lee el NFC
        if (DistanciaMovil < 50) {
          Serial.print(F("Leyendo NFC:"));
          leerNFC();
        }
      }
      // Sensor de presencia LD2410
      clase_en_curso = (personas > 0);  // Si hay personas, la clase está en curso
    } else {
      Serial.println(F("No target"));
    }
  }
  //Compruebo cuando es la próxima clase en este aula
  if (millis() - lastReading3 > delayTime2) {
    lastReading3 = millis();
    obtenerProximaClase();
  }
  //SI ha pasado el tiempo estipulado mando los datos del aula
  if (millis() - lastReading2 > delayTime) {
    lastReading2 = millis();
    EnviaValoresAula();
  }
}
