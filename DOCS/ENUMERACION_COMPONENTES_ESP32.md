# 📋 ENUMERACIÓN DE COMPONENTES Y CONEXIONES - PROYECTO ESP32

**Proyecto:** Sistema de Registro de Presencia y Variables Ambientales IoT  
**Dispositivo:** ESP32 (WROOM-32)  
**Arquitectura:** Multi-core (Core 0 para comunicaciones, Core 1 para sensores)

---

## 🎯 RESUMEN EJECUTIVO

El proyecto integra **5 sensores + 5 actuadores** para monitorización ambiental y control domótico en aulas educativas:

| Categoría | Cantidad | Componentes |
|-----------|----------|-------------|
| **Sensores de Ambiente** | 2 | BME280, BH1750 |
| **Sensores de Presencia** | 2 | LD2410 (radar), PN532 (NFC) |
| **Indicadores Visuales** | 4 | LED Rojo, LED Verde, LED Amarillo, OLED Display |
| **Actuadores de Control** | 2 | Relé 1, Relé 2 |
| **Indicadores Sonoros** | 1 | Buzzer |

---

## 📌 ASIGNACIÓN DE PINES (GPIO)

### 🔴 Indicadores - LEDs
```
LED_ROJO_PIN       = GPIO 25
LED_VERDE_PIN      = GPIO 27
LED_AMARILLO_PIN   = GPIO 14
```

### 🔊 Control de Actuadores
```
RELAY_PIN_1        = GPIO 26  (Activo en LOW)
RELAY_PIN_2        = GPIO 32  (Activo en LOW)
BUZZER_PIN         = GPIO 33  (PWM para frecuencia variable)
```

### 🖥️ Pantalla OLED Display (SSD1306) - I2C
```
OLED_SDA_PIN       = GPIO 21  (Datos I2C)
OLED_SCL_PIN       = GPIO 22  (Reloj I2C)
OLED_RESET_PIN     = -1       (Compartido con reset ESP32)
OLED_I2C_ADDRESS   = 0x3C     (dirección I2C típica)
Resolución: 128x64 pixeles, 0.95"
```

### 🌡️ Sensor BME280 (Temperatura, Humedad, Presión) - I2C
```
Protocolo: I2C (Bus compartido con OLED)
Dirección I2C: 0x76
Parámetros:
  - Temperatura: -40°C a +85°C
  - Humedad: 0% a 100%
  - Presión: 300 hPa a 1100 hPa
```

### 💡 Sensor BH1750 (Luminosidad) - I2C
```
Protocolo: I2C (Bus compartido con OLED y BME280)
Dirección I2C: Variable (típicamente 0x23 o 0x5C)
Rango: 0 a 65535 lux
Modo: CONTINUOUS_HIGH_RES_MODE
```

### 📡 Sensor LD2410 (Radar de Presencia) - UART/Serial2
```
RADAR_RX_PIN       = GPIO 16  (Recepción)
RADAR_TX_PIN       = GPIO 17  (Transmisión)
Velocidad: 256000 baud
Tipos de detección:
  - Objetos estáticos: 0-600 cm
  - Objetos en movimiento: 0-600 cm
```

### 🏷️ Lector NFC PN532 - SPI
```
PN532_SCK (Reloj)  = GPIO 18  (Clock)
PN532_MOSI (Data)  = GPIO 23  (Master Out Slave In)
PN532_MISO (Data)  = GPIO 19  (Master In Slave Out)
PN532_SS (Chip S.) = GPIO 5   (Chip Select)
PN532_IRQ (Int.)   = GPIO 34  (Interrupción, entrada)
Protocolo: SPI
Modos NFC:
  - Tarjetas MIFARE Classic 4K
  - Protocolo ISO14443A
  - UID: 4 o 7 bytes
```

---

## 🔗 DIAGRAMA DE CONEXIONES POR PROTOCOLO

### 📊 BUS I2C (GPIO 21 y 22)
```
      GPIO 21 (SDA)
         |
    ┌────┼────┬────────┬─────────┐
    |         |        |         |
 OLED    BME280    BH1750    [+Expansión]
 0x3C     0x76      0x23/5C
```

### 🔌 BUS SPI (GPIO 18, 19, 23, 5)
```
    ESP32 SPI
     |  |  |  |
     │  │  │  └─ GPIO 5  (CS)  ─→  PN532 (CE/SS)
     │  │  └──── GPIO 23 (MOSI)─→  PN532 (DIN)
     │  └─────── GPIO 19 (MISO)←─  PN532 (DOUT)
     └────────── GPIO 18 (SCK) ─→  PN532 (CLK)
     
     + GPIO 34 (IRQ) ← PN532 (IRQ)
```

### 🔗 UART Serial2 (GPIO 16, 17)
```
    ESP32          LD2410
     |              |
  GPIO 16 (RX) ←─ TX
  GPIO 17 (TX) ─→ RX
```

### 💡 Pines Digitales de Salida (GPIO Directos)
```
GPIO 25 ─→ LED Rojo
GPIO 27 ─→ LED Verde
GPIO 14 ─→ LED Amarillo
GPIO 33 ─→ Buzzer (PWM)
GPIO 26 ─→ Relé 1
GPIO 32 ─→ Relé 2
```

---

## 📦 ESPECIFICACIONES TÉCNICAS POR COMPONENTE

### 1️⃣ **Sensor BME280** (Bosch)
- **Tipo:** Sensor de Ambiente (Temperatura, Humedad, Presión)
- **Pinout:** I2C (4 pines: VCC, GND, SDA, SCL)
- **Dirección I2C:** 0x76
- **Rango Operativo:**
  - Temperatura: -40°C a +85°C (tolerancia ±1°C)
  - Humedad: 0% a 100% (tolerancia ±3%)
  - Presión: 300 hPa a 1100 hPa
- **Consumo:** 5.8 µA (modo reposo)
- **Tiempo de respuesta:** ~1 ms

### 2️⃣ **Sensor BH1750** (ROHM)
- **Tipo:** Sensor de Luz Ambiental
- **Pinout:** I2C (4 pines: VCC, GND, SDA, SCL)
- **Rango:** 1 lux a 65535 lux
- **Resolución:** 1.2 lux/step
- **Modo Operativo:** Continuous High Resolution
- **Tiempo de integración:** 120 ms
- **Consumo:** 150 µA (operativo)

### 3️⃣ **Radar LD2410** (Hi-Link)
- **Tipo:** Sensor de Detección de Presencia (Radar 24 GHz)
- **Pinout:** UART Serial2 (TX, RX)
- **Velocidad:** 256000 baud
- **Rango de Detección:**
  - Estático: 0-600 cm
  - Dinámico: 0-600 cm
- **Resolución:** 75 cm
- **Consumo:** 10 mA (operativo)
- **Firmware:** Version (consultable mediante getFirmwareVersion())

### 4️⃣ **Lector NFC PN532** (NXP)
- **Tipo:** Lector de Tarjetas Inteligentes / NFC
- **Pinout:** SPI (5 pines: CLK, MOSI, MISO, CS, IRQ)
  - GPIO 18 (CLK)
  - GPIO 23 (MOSI)
  - GPIO 19 (MISO)
  - GPIO 5 (CS)
  - GPIO 34 (IRQ)
- **Protocolo:** ISO14443A/MIFARE
- **UID:** 4 bytes (short) o 7 bytes (long)
- **Rango de Lectura:** 0-10 cm
- **Tiempo de polling:** 100 ms (no bloqueante)
- **Consumo:** 100 mA (operativo)

### 5️⃣ **Display OLED 0.95"** (SSD1306)
- **Tipo:** Pantalla OLED monocromática
- **Pinout:** I2C (4 pines: VCC, GND, SDA, SCL)
- **Dirección I2C:** 0x3C
- **Resolución:** 128x64 pixeles
- **Diagonal:** 0.95 pulgadas
- **Contraste:** Muy alto
- **Consumo:** 10-20 mA
- **Tiempo de actualización:** ~1000 ms (definido en código)

### 6️⃣ **Relés** (2x)
- **Tipo:** Relés Electromecánicos / de Estado Sólido
- **Activación:** GPIO 26 (Relé 1) y GPIO 32 (Relé 2)
- **Lógica:** Activos en LOW (HIGH = OFF, LOW = ON)
- **Estado Inicial:** Ambos APAGADOS (HIGH = OFF)
- **Consumo:** ~100 mA por relé (activos)

### 7️⃣ **LEDs Indicadores** (3x)
- **LED Rojo:** GPIO 25 (Indicador de error/crítico)
- **LED Verde:** GPIO 27 (Indicador OK/normal)
- **LED Amarillo:** GPIO 14 (Indicador de advertencia)
- **Modo:** Digital ON/OFF
- **Estados:**
  - NORMAL: Verde
  - ADVERTENCIA: Amarillo + parpadeo
  - ERROR: Rojo
  - CRÍTICO: Rojo + parpadeo

### 8️⃣ **Buzzer** (Piezo)
- **Tipo:** Buzzer pasivo (sin oscilador interno)
- **Pinout:** GPIO 33 (PWM)
- **Frecuencia Variable:** Sí (mediante PWM)
- **Modos:**
  - Beep Corto: 50 ms
  - Beep Largo: 200 ms
  - Frecuencias: Personalizables

---

## 🔋 ALIMENTACIÓN

| Componente | Voltaje | Corriente (aprox.) | Pin |
|-----------|---------|-------------------|-----|
| **ESP32** | 3.3V | 80 mA (idle) | VCC |
| **BME280** | 3.3V | 5 µA - 5.8 mA | VCC |
| **BH1750** | 3.3V | 150 µA - 190 µA | VCC |
| **LD2410** | 3.3V/5V | 10 mA - 80 mA | VCC |
| **PN532** | 3.3V ⚠️ | 100 mA norm, 300 mA pico | VCC |
| **OLED** | 3.3V | 10-20 mA | VCC |
| **LEDs** | 3.3V | 2-5 mA c/u | GPIO |
| **Buzzer** | 3.3V | 0-100 mA | GPIO 33 |
| **Relés** | 3.3V | 100 mA c/u | GPIO 26/32 |
| **Total Estimado** | 3.3V | **250-500 mA** | |

⚠️ **NOTA CRÍTICA:** El PN532 requiere **exactamente 3.3V**. NO conectar a 5V.

---

## 🔄 ESTRUCTURA DE TAREAS

### **Core 0** (Comunicaciones - Hilo HiloComunicador)
- Conexión WiFi
- WebSocket Seguro (WSS)
- Procesamiento de cola de mensajes
- **Intervalo:** 30 segundos

### **Core 1** (Principal)
- Lectura de sensores
- Control de indicadores
- Procesamiento de NFC
- **Intervalo:** 5 segundos

---

## 📡 PROTOCOLOS DE COMUNICACIÓN

| Protocolo | Pines | Velocidad | Dispositivos |
|-----------|-------|-----------|--------------|
| **I2C** | 21, 22 | 100 kHz | BME280, BH1750, OLED |
| **SPI** | 18, 19, 23, 5 | 1 MHz | PN532 |
| **UART (Serial2)** | 16, 17 | 256000 baud | LD2410 |
| **WiFi** | Interna | 2.4 GHz | Router WiFi |
| **WebSocket** | WiFi | SSL/TLS | Servidor HTTPS |

---

## 🚀 SECUENCIAS DE INICIALIZACIÓN

### 1. **Setupindicadores** (setupIndicators)
   - Configura GPIO 25, 27, 14, 33
   - Reproduce secuencia de inicio

### 2. **Setup Relés**
   - Configura GPIO 26 y 32 como OUTPUT
   - Estado inicial: HIGH (APAGADOS)

### 3. **Setup NFC** (setupNFC)
   - Inicializa SPI (GPIO 18, 19, 23, 5)
   - Detecta firmware PN532
   - Configura SAM (Secure Access Module)

### 4. **Setup Radar** (setupRadar)
   - Inicializa Serial2 (GPIO 16, 17)
   - Velocidad: 256000 baud
   - Verifica conexión

### 5. **Setup BME** (setupBME)
   - Inicializa I2C en dirección 0x76
   - Reintentos: 3

### 6. **Setup LightMeter** (setupLightMeter)
   - Inicializa I2C BH1750
   - Modo: CONTINUOUS_HIGH_RES_MODE
   - Reintentos: 3

### 7. **Setup Display** (setupDisplay)
   - Inicializa I2C en dirección 0x3C
   - Pantalla de bienvenida
   - Muestra logo UEX

---

## ⚡ TIEMPOS Y INTERVALOS

| Evento | Intervalo | Descripción |
|--------|-----------|-------------|
| Lectura de sensores | 5 segundos | BME280, BH1750, LD2410 |
| Actualización display OLED | 1 segundo | Refresco de pantalla |
| Procesamiento de cola | 30 segundos | Envío acumulado de datos |
| Polling NFC | 100 ms | No bloqueante |
| Cooldown entre lecturas NFC | 3 segundos | Evita lecturas duplicadas |
| Check token JWT | 12 horas | Validación de autenticación |
| Check clase actual | 5 minutos | Consulta al servidor |

---

## 🔒 SEGURIDAD

- **Autenticación:** JWT (JSON Web Tokens)
- **Comunicación:** WSS (WebSocket Secure) con certificado SSL/TLS
- **Certificado:** Root CA Certificate almacenado en globals.cpp
- **Almacenamiento:** NVS (Non-Volatile Storage) en Preferences

---

## 🧪 CÓDIGOS DE DIAGNÓSTICO

### Estados de Validación de Sensores
```cpp
struct SensorStatus {
  bool bme280_ok;     // Sensor de temperatura/humedad/presión
  bool bh1750_ok;     // Sensor de luz
  bool ld2410_ok;     // Sensor de radar
  bool pn532_ok;      // Lector NFC
  bool display_ok;    // Pantalla OLED
};
```

### Estados de LEDs
```cpp
enum EstadoLED {
  NORMAL,      // Verde ✅
  ADVERTENCIA, // Amarillo ⚠️
  ERROR,       // Rojo ❌
  CRITICO      // Rojo parpadeante 🔴
};
```

---

## 📋 CHECKLIST DE CONEXIONES

- [ ] **Alimentación 3.3V** a todos los componentes
- [ ] **GND común** a todos los dispositivos
- [ ] **I2C:** SDA (GPIO 21) y SCL (GPIO 22) unidos a BME280, BH1750, OLED
- [ ] **SPI:** CLK (GPIO 18), MOSI (GPIO 23), MISO (GPIO 19), CS (GPIO 5) a PN532
- [ ] **UART2:** GPIO 16 (RX) y GPIO 17 (TX) a LD2410
- [ ] **LEDs:** Ánodos a GPIO 25, 27, 14 + resistencias (220Ω típico)
- [ ] **Buzzer:** GPIO 33 + capacitor (opcional)
- [ ] **Relés:** GPIO 26, GPIO 32 + diodos de protección
- [ ] **PN532:** ⚠️ Verificar 3.3V (NOT 5V!)
- [ ] **OLED:** SDA=21, SCL=22, VCC=3.3V, GND=GND
- [ ] **LD2410:** Velocidad serial 256000 baud

---

## 📚 ARCHIVOS PRINCIPALES

| Archivo | Función |
|---------|---------|
| `config.h` | Definición de pines (#define) |
| `globals.h/cpp` | Variables globales y configuración |
| `BME_module.ino` | Lectura de temperatura/humedad/presión |
| `LightMeter_module.ino` | Lectura de luminosidad |
| `radar_module.ino` | Lectura de presencia (LD2410) |
| `NFC_module.ino` | Lectura de tarjetas NFC (PN532) |
| `display_module.ino` | Control de pantalla OLED |
| `indicators.ino` | Control de LEDs, buzzer y relés |
| `setupSensores.ino` | Inicialización global de hardware |

---

**Última Actualización:** Febrero 2026  
**Versión del Hardware:** ESP32 WROOM-32  
**Estado del Proyecto:** Control Asistencia IoT UEX
