#include <Wire.h>

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println("\n--- ESCÁNER I2C DEFINITIVO ---");
  Serial.println("Iniciando Wire en pines 21 (SDA) y 22 (SCL)...");
  
  // Forzamos los pines del ESP32
  Wire.begin(21, 22);
}

void loop() {
  byte error, address;
  int nDevices = 0;

  Serial.println("Buscando dispositivos...");

  for(address = 1; address < 127; address++ ) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("✅ ¡ENCONTRADO! Dirección: 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);

      // Identificamos quién es quién
      if (address == 0x23) Serial.print(" (Tu sensor de luz BH1750)");
      else if (address == 0x76) Serial.print(" (Posible BME/BMP280 - Dirección A)");
      else if (address == 0x77) Serial.print(" (Posible BME/BMP280 - Dirección B)");
      
      Serial.println();
      nDevices++;
    }
    else if (error == 4) {
      Serial.print("❓ Error desconocido en la dirección 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }
  
  if (nDevices == 0)
    Serial.println("❌ No se encontró NINGÚN dispositivo I2C\n");
  else
    Serial.println("--- Búsqueda terminada ---\n");

  delay(3000); 
}

21:08:37.655 -> Buscando dispositivos...
21:08:37.655 -> ✅ ¡ENCONTRADO! Dirección: 0x23 (Tu sensor de luz BH1750)
21:08:37.655 -> ✅ ¡ENCONTRADO! Dirección: 0x76 (Posible BME/BMP280 - Dirección A)
21:08:37.655 -> --- Búsqueda terminada ---
21:08:37.655 -> 

El problema NO es tu código. El problema es de Hardware / Identidad del Sensor.

Ese valor fijo de 182.57 y una presión absurdamente baja de 681 hPa (que equivaldría a estar a 3.200 metros de altura) son el síntoma clásico de una confusión de registros.

Aquí están las 3 causas, ordenadas de la más probable a la menos probable:

1. El "Falso Amigo": Tienes un BMP280, no un BME280
Este es el fraude más común en Amazon/AliExpress. Te venden un módulo etiquetado como "BME280" (que mide Temp + Presión + Humedad), pero sueldan un chip BMP280 (solo Temp + Presión).

Por qué falla: Los registros de memoria interna (donde se guardan los datos de calibración dig_T1, dig_T2, etc.) están en direcciones ligeramente diferentes entre ambos chips.

El resultado: La librería lee datos de una dirección equivocada, aplica la fórmula matemática y da un resultado "válido" numéricamente (182.57) pero físicamente absurdo. Además, lee "Humedad" de un registro que no existe, obteniendo basura electrónica (ese 62%).

PRUEBA VISUAL RÁPIDA: Mira el componente metálico plateado sobre la placa morada/azul:

Forma CUADRADA: Es un BME280 (El bueno).

Forma RECTANGULAR: Es un BMP280 (El impostor).

2. Error de pines flotantes (SDO / CSB)
En los módulos genéricos de 6 pines, el chip puede entrar en modo SPI en lugar de I2C si los pines de control no están definidos.

Solución: Conecta el pin SDO a GND (para dirección 0x76) o a 3.3V (para 0x77). No lo dejes al aire.

Solución: Conecta el pin CSB a 3.3V (esto le grita al sensor: "¡Trabaja en modo I2C!").


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


21:12:30.743 -> rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
21:12:30.782 -> configsip: 0, SPIWP:0xee
21:12:30.782 -> clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
21:12:30.782 -> mode:DIO, clock div:1
21:12:30.782 -> load:0x3fff0030,len:4980
21:12:30.782 -> load:0x40078000,len:16612
21:12:30.782 -> load:0x40080400,len:3480
21:12:30.782 -> entry 0x400805b4
21:12:30.900 -> 
21:12:30.900 -> --- INTERROGANDO AL SENSOR 0x76 ---
21:12:31.125 -> El sensor en 0x76 dice que su ID es: 0x0
