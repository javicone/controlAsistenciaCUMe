#include <Wire.h>

#define SENSOR_ADDR 0x76 

void setup() {
  Serial.begin(115200);
  while(!Serial);
  
  // Iniciamos I2C en tus pines correctos
  Wire.begin(21, 22); 
  
  Serial.println("\n--- INTERROGANDO AL SENSOR 0x76 ---");
  delay(100);

  // 1. Despertar al sensor (por si está dormido)
  Wire.beginTransmission(SENSOR_ADDR);
  Wire.write(0xF4); // Registro de control
  Wire.write(0x27); // Modo normal
  Wire.endTransmission();
  delay(100);

  // 2. Preguntar por el ID (Registro 0xD0)
  Wire.beginTransmission(SENSOR_ADDR);
  Wire.write(0xD0); // Dirección del registro "CHIP ID"
  Wire.endTransmission();
  
  Wire.requestFrom(SENSOR_ADDR, 1);
  if (Wire.available()) {
    byte id = Wire.read();
    Serial.print("El sensor en 0x76 dice que su ID es: 0x");
    Serial.println(id, HEX);
    
    // VEREDICTO
    if (id == 0x60) Serial.println("VEREDICTO: Es un BME280 Real.");
    else if (id == 0x58) Serial.println("VEREDICTO: Es un BMP280 (El impostor).");
    else if (id == 0x61) Serial.println("VEREDICTO: Es un BME680.");
    else Serial.println("VEREDICTO: Es un CLON DESCONOCIDO o defectuoso.");
  } else {
    Serial.println("Error: El sensor no respondió al pedido de ID.");
  }
}

void loop() {}