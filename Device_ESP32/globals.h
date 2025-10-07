#pragma once 
//se utiliza para evitar que el archivo de cabecera (globals.h o config.h)
//  se incluya más de una vez durante la compilación. Esto previene errores 
// de redefinición y conflictos, especialmente en proyectos grandes con múltiples
//  inclusiones.

#include <Arduino.h>

// Token y estado de aula
extern String jwtToken;
extern bool clase_en_curso;

// Variables de sensores y estado
extern float temperatura;
extern float humedad;
extern float presion;
extern float iluminacion;
extern int personas;
extern int DistanciaMovil;
extern bool radarConnected;
extern bool status;

// Tiempos y flags
extern unsigned long delayTime;
extern unsigned long delayTime2;
extern uint32_t lastReading;
extern uint32_t lastReading2;
extern uint32_t lastReading3;
extern unsigned long targetTimeMillis;
extern bool ledRedOn;

// NFC
extern uint8_t DatoRecibido[4];
extern boolean LeeTarjeta;
extern uint8_t uid[7];
extern uint8_t LongitudUID;