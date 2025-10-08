#include "globals.h"

// Token y estado de aula
String jwtToken = "asdfghjklñzxcvbnmQWERTYUIOPZXCVBNMLKJHGFDSA1234567890";
bool clase_en_curso = false;

// Variables de sensores y estado
float temperatura = 0.0;
float humedad = 0.0;
float presion = 0.0;
float iluminacion = 0.0;
int personas = 0;
float DistanciaMovil = 0.0; // Cambiado a float
bool radarConnected = false;
int status = 0; // Cambiado a int

// Tiempos y flags
unsigned long delayTime = 1000;
unsigned long delayTime2 = 5000;
uint32_t lastReading = 0;
uint32_t lastReading2 = 0;
uint32_t lastReading3 = 0;
unsigned long targetTimeMillis = 0;
bool ledRedOn = false;

// NFC
uint8_t DatoRecibido[4];
boolean LeeTarjeta = false;
uint8_t uid[7];
uint8_t LongitudUID = 0;