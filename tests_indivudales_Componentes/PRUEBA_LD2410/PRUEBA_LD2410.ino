#include <MyLD2410.h>

// Pines para ESP32 (RX del ESP conecta a TX del sensor, TX del ESP a RX del sensor)
#define LD2410_RX_PIN 16
#define LD2410_TX_PIN 17

// Constructor pasando el Serial
MyLD2410 sensor(Serial2);

void setup() {
  Serial.begin(115200);
  Serial.println("Iniciando prueba LD2410...");

  // Iniciar Serial2 a 256000 baudios (velocidad por defecto del LD2410)
  Serial2.begin(256000, SERIAL_8N1, LD2410_RX_PIN, LD2410_TX_PIN);

  Serial.println("LD2410 inicializado (esperando datos...)");
}

void loop() {
  // 1. CORRECCIÓN: La función debería ser 'check()'
  sensor.check();

  // 2. Verificar si hay presencia
  if (sensor.presenceDetected()) {
    
    Serial.print("¡Presencia! ");

    // Verificar si es movimiento
    if (sensor.movingTargetDetected()) {
       Serial.print("[MOVIMIENTO: ");
       Serial.print(sensor.movingTargetDistance()); // Paréntesis obligatorios
       Serial.print("cm] ");
    }

    // Verificar si es estático
    if (sensor.stationaryTargetDetected()) {
       Serial.print("[ESTÁTICO: ");
       Serial.print(sensor.stationaryTargetDistance()); // Paréntesis obligatorios
       Serial.print("cm] ");
    }

    Serial.println(); // Nueva línea
  } 
  
  // Pequeña pausa para no saturar el monitor serial
  // Nota: 'check()' debe llamarse frecuentemente, así que no pongas delays largos.
  delay(100); 
}