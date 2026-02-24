# 🔌 TABLA COMPLETA DE PINES ESP32 - CONTROL ASISTENCIA

## 📊 TABLA MAESTRA DE PINES

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ASIGNACIÓN COMPLETA ESP32 WROOM-32                   │
└─────────────────────────────────────────────────────────────────────────┘
```

| GPIO | Pin Nombre | Función | Componente | Tipo | Notas |
|-----|-----------|---------|-----------|------|-------|
| 5   | D5 (GPIO5) | CS (Chip Select) | PN532 NFC | SPI Output | Pull-up requerido |
| 14  | D14 (GPIO14) | DIO0 (Interrupt) | SX1276 LoRa | Input | Interrupción LoRa |
| 16  | D16 (GPIO16) | RX Serial2 | LD2410 Radar | Serial Input | UART2 RX |
| 17  | D17 (GPIO17) | TX Serial2 | LD2410 Radar | Serial Output | UART2 TX |
| 18  | D18 (GPIO18) | CLK (SPI Clock) | PN532 NFC + SX1276 | SPI Clock | Reloj SPI compartido |
| 19  | D19 (GPIO19) | MISO (SPI) | PN532 NFC + SX1276 | SPI Input | Slave Output compartido |
| 21  | D21 (GPIO21) | SDA (I2C Data) | BME280, BH1750, OLED | I2C SDA | Bus compartido |
| 22  | D22 (GPIO22) | SCL (I2C Clock) | BME280, BH1750, OLED | I2C SCL | Bus compartido |
| 23  | D23 (GPIO23) | MOSI (SPI) | PN532 NFC + SX1276 | SPI Output | Master Output compartido |
| 25  | D25 (GPIO25) | RST (Reset) | SX1276 LoRa | Output | Reset del módulo LoRa |
| 26  | D26 (GPIO26) | Relé 1 | Control domótico | Output | Activo en LOW |
| 27  | D27 (GPIO27) | CS (Chip Select) | SX1276 LoRa | SPI Output | Chip Select dedicado |
| 32  | D32 (GPIO32) | Relé 2 | Control domótico | Output | Activo en LOW |
| 33  | D33 (GPIO33) | Buzzer | Indicador Sonoro | PWM Output | PWM variable |
| 34  | D34 (GPIO34) | IRQ (NFC) | PN532 NFC | Input Only | Interrupción (entrada) |

---

## 🗺️ MAPA VISUAL DE PINES ESP32

```
                    ┌─────────────────────┐
                    │    ESP32 WROOM-32   │
                    │                     │
         D1 (TX0)   ├─────────────────────┤   ← Serial Monitor
         D3 (RX0)   │  3V3 [USB 5V] GND   │
                    │                     │
       GND          │   36  39  34  35    │
       D23 (MOSI)   │   4   2   15  13    │
       D22 (SCL)    │   14  27  26  25    │
       D21 (SDA)    │   33  32  5   18    │
       D19 (MISO)   │   17  16  4   0     │
       D18 (CLK)    │                     │
                    │  GND GND 3V3 3V3    │
                    └─────────────────────┘

LEYENDA DE COLORES:
🟢 GPIO Entrada/Salida Digital
🔴 GPIO PWM
🟣 GPIO Especial (UART, SPI, I2C)
⚫ GND (Tierra)
🟡 Poder (3.3V)
```

### Tabla de Pines Utilizados

```
┌────────────────────────────────────────────────────────────────┐
│  LADO IZQUIERDO                   LADO DERECHO                │
├────────────────────────────────────────────────────────────────┤
│ GND              ─── GND           3V3 ─── 3V3                 │
│ D23 (MOSI)       ─── SPI COMPARTIDO D1 (TX0) ─── Serial Monitor│
│ D22 (SCL I2C)    ─── BME/BH/OLED   D3 (RX0) ─── Serial Monitor│
│ D21 (SDA I2C)    ─── BME/BH/OLED   D4 ─── [Libre]             │
│ D19 (MISO)       ─── SPI COMPARTIDO D16 (RX2)─── LD2410       │
│ D18 (CLK)        ─── SPI COMPARTIDO D17 (TX2)─── LD2410       │
│ D5 (CS PN532)    ─── PN532         D2 ─── [Libre]             │
│ D26 (Relé 1)     ─── Relé 1        D15 ─── [Libre]            │
│ D33 (Buzzer)     ─── Buzzer        D13 ─── [Libre]            │
│ D32 (Relé 2)     ─── Relé 2        D14 (DIO0)──── SX1276 LoRa │
│ D34 (IRQ NFC)    ─── PN532 IRQ     D25 (RST)──── SX1276 LoRa  │
│ GND              ─── GND           D27 (CS)───── SX1276 LoRa  │
│                                    GND ─── GND                │
│                                    3V3 ─── 3V3                │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔗 DIAGRAMAS DE CONEXIÓN POR PROTOCOLO

### 1️⃣ BUS I2C (GPIO 21 y 22)
```
                    ESP32
                     
          GPIO 21 (SDA)
              ║
    ┌─────────╫─────────┬──────────┬──────────┐
    ║         ║         ║          ║          ║
  10kΩ      10kΩ      3.3V       GND        
    ║         ║         ║          ║
   SDA       SCL    Común Común   
    │         │      ├─┼──────────┼──────────┤
    │         │      │ │          │          │
┌───┴──────┬──┴──┬   │ │          │          │
│  BME280   │    │   │ │          │          │
│ 0x76      │    │   │ │          │          │
│ Temp/Hum  │    │   │ │          │          │
└───┬──────┴──┬──┘   │ │          │          │
    │ SDA  SCL│      │ │          │          │
    │    │    │      │ │          │          │
    │    │    ├──────┘ │          │          │
    │    │    │        │          │          │
    │ ┌──┴────┴───┐    │          │          │
    │ │ BH1750    │    │          │          │
    │ │ Luz       │    │          │          │
    │ └──┬────┬───┘    │          │          │
    │    │    │        │          │          │
    │    └─┬──┴────────┘          │          │
    │      │                      │          │
    │ ┌────┴──────┐               │          │
    │ │   OLED    │               │          │
    │ │  0x3C     │               │          │
    │ │ 128x64px  │               │          │
    │ │           │               │          │
    │ └────┬──┬───┘               │          │
    │      │  │                   │          │
    ├──────┘  │                   │          │
    │         │                   │          │
   3.3V     GND                  GND         │
                                            │
                                           GND
```

### 2️⃣ BUS SPI (GPIO 18, 19, 23 - COMPARTIDO entre PN532 y SX1276)
```
              ESP32
               
         GPIO 18 (CLK)────────┬────────────┐
         GPIO 23 (MOSI)───┬───┤            │
         GPIO 19 (MISO)─┬─┤   │            │
                        │ │   │            │
        ┌───────────────┘ │   │            │
        │              ┌──┴─┬─┴────┐       │
        │              │    │      │       │
        │            PN532  │      │   SX1276
        │            NFC    │      │   LoRa
        │                   │      │
        │  CLK: GPIO18 ─────┤      │───────→ CLK: GPIO18
        │  DIN: GPIO23 ─────┤      │───────→ DIN: GPIO23
        │  OUT: GPIO19 ←─────┤      │←────── OUT: GPIO19
        │  CE: GPIO 5  ──→   │      │
        │  IRQ: GPIO34 ←─    │      │───────→ CS: GPIO 27
        │                    │      │───────→ RST: GPIO 25
        │  VCC: 3.3V ⚠️      │      │───────→ DIO0: GPIO 14
        │  GND: GND  ────────┴──────┴────────→ VCC: 3.3V ⚠️
        │                              GND: GND
        └──────────────────────────────────────────────────────

⚠️  IMPORTANTE:
    - PN532 y SX1276 comparten CLK, MOSI, MISO (GPIO 18,23,19)
    - Cada uno tiene su propio CS (Chip Select) exclusivo
    - PN532: CS en GPIO 5
    - SX1276: CS en GPIO 27, RST en GPIO 25, DIO0 en GPIO 14
    - Ambos requieren EXACTAMENTE 3.3V (NO 5V)
```

### 3️⃣ UART Serial2 (GPIO 16, 17)
```
        ESP32               LD2410 Radar
        
    GPIO 16 (RX2) ←─────── TX
    GPIO 17 (TX2) ───────→ RX
    
    Velocidad: 256000 baud
    Detección: 0-600 cm estático
              0-600 cm dinámico
```

### 4️⃣ SALIDAS DIGITALES Y ACTUADORES
```
    GPIO 33 ──────────→ Buzzer (PWM)
    GPIO 26 ──────────→ Relé 1 (activo LOW)
    GPIO 32 ──────────→ Relé 2 (activo LOW)
    GPIO 25 ──────────→ SX1276 RST (Reset LoRa)
    GPIO 27 ──────────→ SX1276 CS (Chip Select LoRa)
    GPIO 14 ──────────→ SX1276 DIO0 (Interrupt LoRa)
    
    Todas → GND (Tierra común)
    
    NOTA: LEDs rojo, verde y amarillo han sido removidos
          Los pines 25 (RST LoRa) y 27 (CS LoRa) están
          ahora dedicados al módulo SX1276
          El pin 14 (DIO0 LoRa) recibe interrupciones del módulo
```

---

## 📋 CONFIGURACIÓN DE PINES POR PROTOCOLO

### I2C Configuration
```cpp
// Wire I2C Bus
SDA = GPIO 21
SCL = GPIO 22
Frecuencia: 100 kHz (Standard)

// Inicialización:
Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);
```

### SPI Configuration
```cpp
// SPI Bus (COMPARTIDO entre PN532 y SX1276)
SCLK = GPIO 18 (Clock)
MOSI = GPIO 23 (Master Out Slave In)
MISO = GPIO 19 (Master In Slave Out)
CS_PN532  = GPIO 5  (Chip Select PN532)
CS_SX1276 = GPIO 27 (Chip Select SX1276)
RST_SX1276 = GPIO 25 (Reset SX1276)
DIO0_SX1276 = GPIO 14 (Interrupt SX1276)

// Inicialización SPI:
SPI.begin(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

// Configuración LoRa:
LoRa.setPins(LORA_CS, LORA_RST, LORA_DIO0);
// donde:
// LORA_CS = 27
// LORA_RST = 25
// LORA_DIO0 = 14
```

### UART Configuration
```cpp
// Serial2 (Segunda UART)
RX = GPIO 16
TX = GPIO 17
Velocidad: 256000 baud
Inicialización:
Serial2.begin(256000, SERIAL_8N1, RADAR_RX_PIN, RADAR_TX_PIN);
```

---

## 🔋 ESQUEMA DE POTENCIA

```
┌─────────────────────────────────────────────────────┐
│           Fuente de Alimentación                    │
│           USB 5V o Batería Li-ion                   │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │        Regulador de Voltaje 5V → 3.3V      │    │
│  │  (Necesario si se usa USB 5V)             │    │
│  └────────────────────────────────────────────┘    │
│           ║                                         │
│        3.3V                                         │
│           ║                                         │
│    ┌──────┴──────┐                                 │
│    │   +3.3V BUS │                                 │
│    └──────┬──────┘                                 │
│           │                                         │
│    ┌──────┴───────────────────┬─────────────────┐  │
│    │                          │                 │  │
│ ESP32                    Capacitor             Capacitor
│ 3.3V                     100µF                 100µF
│    │                          │                 │  │
│    ├─────────→ BME280    ┌────┴────┐    ┌─────┴──┐
│    │                     │ BH1750  │    │  OLED  │
│    ├─────────→ PN532     └────┬────┘    └─────┬──┘
│    │                          │               │    │
│    │                          GND             GND   │
│    │                                               │
│    └─────────→ LEDs (c/u con 220Ω)               │
│    │                                               │
│    └─────────→ Buzzer + Control Relés            │
│                                                     │
│ GND ────────────┬───────────────────────────────┐  │
│                 │                               │  │
│              Tierra Común                        │  │
│              (BUS GND CENTRAL)                   │  │
└─────────────────────────────────────────────────┘
```

---

## ✅ LISTA DE VERIFICACIÓN TÉCNICA

### Antes de Encender
- [ ] Verificar alimentación 3.3V en todos los pines VCC
- [ ] Confirmar GND común en todos los componentes
- [ ] PN532: ⚠️ Verificar exactamente 3.3V (medidor)
- [ ] Revisar no hay puentes de cobre en la placa
- [ ] I2C: Pines SDA (21) y SCL (22) unidos correctamente
- [ ] SPI: Pines CLK (18), MOSI (23), MISO (19), CS (5) correctos
- [ ] UART2: RX (16) ↔ TX (17) cruzados correctamente
- [ ] LEDs: Ánodos a GPIO, Cátodos a GND (con resistencias)
- [ ] Relés: GPIO → Pin de entrada del módulo relé
- [ ] Buzzer: GPIO 33 → Positivo, GND → Negativo

### Después de Encender
- [ ] Serial Monitor: Ver inicialización de componentes
- [ ] LEDs: Secuencia de inicio (rojo → amarillo → verde)
- [ ] OLED: Mostrar pantalla de bienvenida
- [ ] Sensores: Reportar "✅" en resumen
- [ ] PN532: Confirmar detección de firmware
- [ ] LD2410: Confirmar versión de firmware
- [ ] No hay "❌ FALLO" en la inicialización

---

## 🚀 TABLA DE VELOCIDADES Y CONFIGURACIONES

| Interfaz | Parámetro | Valor | Unidad |
|----------|-----------|-------|--------|
| I2C | Frecuencia | 100 | kHz |
| I2C | SDA Pin | 21 | GPIO |
| I2C | SCL Pin | 22 | GPIO |
| SPI | Clock | 1-10 | MHz |
| SPI | CLK Pin | 18 | GPIO |
| SPI | MOSI Pin | 23 | GPIO |
| SPI | MISO Pin | 19 | GPIO |
| SPI PN532 | CS Pin | 5 | GPIO |
| SPI SX1276 | CS Pin | 27 | GPIO |
| SPI SX1276 | RST Pin | 25 | GPIO |
| SPI SX1276 | DIO0 Pin | 14 | GPIO |
| LoRa | Frecuencia | 868/915 | MHz |
| LoRa | Spreading Factor | 7-12 | - |
| LoRa | Bandwidth | 125 | kHz |
| UART2 | Baud Rate | 256000 | bps |
| UART2 | RX Pin | 16 | GPIO |
| UART2 | TX Pin | 17 | GPIO |

---

## 📝 NOTAS IMPORTANTES

1. **PN532 Alimentación:** Usar EXACTAMENTE 3.3V. No conectar a 5V.
2. **SX1276 Alimentación:** Usar EXACTAMENTE 3.3V. No conectar a 5V.
3. **SPI Compartido:** PN532 y SX1276 comparten CLK, MOSI, MISO pero tienen CS diferentes.
4. **I2C Bus:** Compartido por 3 sensores. Las direcciones no deben conflictuar.
5. **SPI Velocidad:** PN532 soporta hasta 10 MHz, SX1276 hasta 10 MHz. Configurado a 1 MHz para estabilidad.
6. **Relés Activos en LOW:** GPIO HIGH = APAGADO, GPIO LOW = ENCENDIDO.
7. **LoRa Configuración:** 868 MHz (Europa) o 915 MHz (América), SF7, BW 125kHz.
8. **LEDs Removidos:** Los pines anteriormente usados para LEDs (GPIO 25, 27, 14) ahora controlan SX1276.

---

## 📞 REFERENCIA RÁPIDA

```
╔════════════════════════════════════════════════════╗
║           PINOUT RÁPIDO ESP32 v2.0                ║
╠════════════════════════════════════════════════════╣
║ SENSORES I2C (Bus Compartido):                    ║
║   SDA (GPIO 21) / SCL (GPIO 22)                   ║
║   Componentes: BME280, BH1750, OLED               ║
║                                                   ║
║ SENSORES SPI (Bus Compartido):                    ║
║   CLK(18) MOSI(23) MISO(19)                       ║
║   PN532 NFC:      CS(5) IRQ(34)                   ║
║   SX1276 LoRa:    CS(27) RST(25) DIO0(14)         ║
║                                                   ║
║ SENSOR SERIAL (LD2410 Radar):                     ║
║   RX(16) / TX(17) @ 256000 baud                   ║
║                                                   ║
║ ACTUADORES:                                       ║
║   Buzzer(33) / Relé1(26) / Relé2(32)             ║
║                                                   ║
║ COMUNICACIÓN LoRa (SX1276):                       ║
║   868/915 MHz, SF7, BW 125kHz                     ║
║   3.3V SOLAMENTE                                  ║
╚════════════════════════════════════════════════════╝
```

---

**Documento:** Tabla Completa de Pines ESP32 v2.0  
**Proyecto:** Control Asistencia IoT UEX  
**Actualización:** Febrero 2026  
**Versión:** 2.0 - Agregado módulo SX1276 LoRa, LEDs removidos
