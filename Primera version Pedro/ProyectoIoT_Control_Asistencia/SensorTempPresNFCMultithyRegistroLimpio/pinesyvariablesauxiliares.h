const char* ssid = "Nothing";
const char* password = "12345678";

const char* wsHost = "10.39.217.94";
const int wsPort = 5678;
const char* wsPath = "/";

const char* serverUrl = "http://10.39.217.94:5000";

const char* datos_aula = "/datos_aula";
const char* registro = "/registro";

// Configura zona horaria con DST automático para España (CET/CEST)
const char* tzInfo = "CET-1CEST,M3.5.0/2,M10.5.0/3";

String jwtToken = "";  // Guardaremos aquí el token

const char* aula = "Aula 101";
const int relayPin = 26;  // Pin del relé

#define SEALEVELPRESSURE_HPA (1013.25)

#define RADAR_RX_PIN 16
#define RADAR_TX_PIN 17
#define RADAR_SERIAL Serial1

//Conexiones SPI del ESP32
#define PN532_SCK (18)
#define PN532_MOSI (23)
#define PN532_SS (5)

unsigned long delayTime = 30000;
unsigned long delayTime2 = 30000;
uint32_t lastReading = 0;
uint32_t lastReading2 = 0;
uint32_t lastReading3 = 0;
bool radarConnected = false;

bool status;

float temperatura;
float humedad;
float presion;
float iluminacion;
int personas = 0;
int DistanciaMovil = 0;  //distancia del objeto que se mueve
bool clase_en_curso = false;

unsigned long targetTimeMillis = 0;  // Tiempo objetivo (en milisegundos) para encender el LED
bool ledRedOn = false;

uint8_t DatoRecibido[4];                  //Para almacenar los datos
boolean LeeTarjeta;                       //Variable para almacenar la detección de una tarjeta
uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  // Búfer para almacenar el UID devuelto
uint8_t LongitudUID;                      //Variable para almacenar la longitud del UID de la tarjeta