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
#include <WebSocketsClient.h>  
//#include "Freenove_WS2812_Lib_for_ESP32.h"
//-----------------------------------
#include <Wire.h>
#include <SPI.h>         //Librería para comunicación SPI
#include <Adafruit_PN532.h>
//-----------------------------------
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <BH1750.h>
#include <ld2410.h>
#include <Adafruit_GFX.h>


#include <Preferences.h>
#include "globals.h"
#include "config.h"



// Declaración adelantada
void initSensores();
void HiloComunicadorcode(void* pvParameters);
NFCData leerNFC();  // Devuelve NFCData
void obtenerProximaClase();
void EnviaValoresAula();
bool registrarAsistencia(String tarjetaUID);  // Devuelve true si fichaje exitoso
String uidToString(byte *uid, unsigned int longitud);
String urlencode(String str);
unsigned long epochFromString(String fecha);
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length);  // ✅ Callback para WebSocketsClient
// Declaraciones faltantes para las funciones de otros archivos
void setupWiFiEvents();          
bool fetchDeviceToken();         
void connectWS();                
void checkWiFiConnection();      
void processQueue();             
RadarData leerRadar();         


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
  // Cargar nombre de aula desde NVS (Preferences) si existe
  {
    Preferences preferences;
    preferences.begin("config", true);
    String savedAula = preferences.getString("aula", "");
    if (savedAula.length() > 0) {
      aula = savedAula;
      Serial.printf("📦 Aula cargada desde NVS: %s\n", aula.c_str());
    } else {
      Serial.println("⚠️ No hay aula guardada en NVS; usando valor por defecto");
    }
    preferences.end();
  }
  //Inicializamos Serial2 para el radar LD2410
  // esta decision se debe a que si llamamos la funcion en runtime puede fallar al reiniciar la UART, por lo que
  secuenciaInicio();
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
  
  // ============================================
  // VERIFICAR SI EL TIMER DE FIN DE CLASE SE DISPARÓ
  // ============================================
  if (timerFinClaseDisparado) {
    Serial.println("⏰ Timer de fin de clase disparado!");
    resetearEstadoFichaje();  // Resetea estado y consulta nueva clase
  }

  // ============================================
  // POLLING NFC DIRECTO (sin IRQ - más estable)
  // Solo activo si hay clase en curso Y no se ha fichado aún
  // ============================================
  
  if(claseEnCurso && !fichajeClaseCompletado){
    // Gestionar cooldown entre lecturas de tarjetas
    if (nfcReaderDisabled && millis() - nfcTimeLastCardRead > DELAY_BETWEEN_CARDS) {
        nfcReaderDisabled = false;
    }
    
    // Si no está en cooldown, intentar leer tarjeta
    if (!nfcReaderDisabled) {
        NFCData nfc_data = leerNFC();  // Polling directo con timeout corto
        
        if (nfc_data.valido && nfc_data.tarjetaDetectada) {
            Serial.println("🔔 Tarjeta detectada por polling");
            
           
            bool fichajeExitoso = registrarAsistencia(nfc_data.uid);
            
            if (fichajeExitoso) {
                secuenciaExito();
                fichajeClaseCompletado = true;  // Deshabilitar NFC
                Serial.println("✅ Fichaje verificado. NFC deshabilitado hasta fin de clase.");
                
                // Iniciar timer hasta fin de clase
                iniciarTimerFinClase();
            }
            else {
                secuenciaError();
                Serial.println("❌ Fichaje fallido. Intente nuevamente.");
            }
            
            nfcTimeLastCardRead = millis();
            nfcReaderDisabled = true;
        }
    }
  } else if (fichajeClaseCompletado && claseEnCurso) {
    // Mostrar mensaje periódicamente mientras espera fin de clase
    static unsigned long lastMsgTime = 0;
    if (millis() - lastMsgTime > 60000) {  // Cada minuto
      Serial.printf("ℹ️ NFC deshabilitado - esperando fin de clase (%s)\n", horaFinClase.c_str());
      lastMsgTime = millis();
    }
  } else if (!claseEnCurso) {
    // No hay clase - NFC permanece inactivo
    static unsigned long lastNoClassMsg = 0;
    if (millis() - lastNoClassMsg > 120000) {  // Cada 2 minutos
      Serial.println("😴 Sin clase activa - NFC inactivo");
      lastNoClassMsg = millis();
    }
  }
  

  // ============================================
  // OBTENER PRÓXIMA CLASE (solo si no hay fichaje pendiente de timer)
  // Cuando el timer está activo, él se encarga de la transición
  // ============================================
  if (!fichajeClaseCompletado && millis() - lastReading3 > CLASS_CHECK_INTERVAL) {
    lastReading3 = millis();
    obtenerProximaClase();
  }

  // ============================================
  // ENVIAR DATOS DEL AULA
  // ============================================
  if (millis() - lastReading2 > SENSOR_READ_INTERVAL) {
    lastReading2 = millis();
    EnviaValoresAula();
}

  // ============================================
  // RENOVAR JWT SI ES NECESARIO
  // ============================================
  
static unsigned long lastTokenCheck = 0;
if (millis() - lastTokenCheck > TOKEN_CHECK_INTERVAL) {
    lastTokenCheck = millis();
    Serial.println("⏰ Comprobando/renovando JWT por timer...");
    String newToken = ensureToken();
    if (newToken.length() > 0) {
        Serial.println("✅ JWT válido o renovado correctamente");
    } else {
        Serial.println("❌ Error renovando JWT");
    }
}

}

