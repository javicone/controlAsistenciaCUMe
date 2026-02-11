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
| 14  | D14 (GPIO14) | LED Amarillo | Indicador | Output | PWM compatible |
| 16  | D16 (GPIO16) | RX Serial2 | LD2410 Radar | Serial Input | UART2 RX |
| 17  | D17 (GPIO17) | TX Serial2 | LD2410 Radar | Serial Output | UART2 TX |
| 18  | D18 (GPIO18) | CLK (SPI Clock) | PN532 NFC | SPI Clock | Reloj SPI |
| 19  | D19 (GPIO19) | MISO (SPI) | PN532 NFC | SPI Input | Slave Output |
| 21  | D21 (GPIO21) | SDA (I2C Data) | BME280, BH1750, OLED | I2C SDA | Bus compartido |
| 22  | D22 (GPIO22) | SCL (I2C Clock) | BME280, BH1750, OLED | I2C SCL | Bus compartido |
| 23  | D23 (GPIO23) | MOSI (SPI) | PN532 NFC | SPI Output | Master Output |
| 25  | D25 (GPIO25) | LED Rojo | Indicador | Output | PWM compatible |
| 26  | D26 (GPIO26) | Relé 1 | Control domótico | Output | Activo en LOW |
| 27  | D27 (GPIO27) | LED Verde | Indicador | Output | PWM compatible |
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
│ D23 (MOSI)       ─── PN532         D1 (TX0) ─── Serial Monitor │
│ D22 (SCL I2C)    ─── BME/BH/OLED   D3 (RX0) ─── Serial Monitor │
│ D21 (SDA I2C)    ─── BME/BH/OLED   D4 ─── [Libre]             │
│ D19 (MISO)       ─── PN532         D16 (RX2)─── LD2410        │
│ D18 (CLK)        ─── PN532         D17 (TX2)─── LD2410        │
│ D5 (CS)          ─── PN532         D2 ─── [Libre]             │
│ D27 (LED Verde)  ─── LED Verde     D15 ─── [Libre]            │
│ D26 (Relé 1)     ─── Relé 1        D13 ─── [Libre]            │
│ D25 (LED Rojo)   ─── LED Rojo      D12 ─── [Libre]            │
│ D33 (Buzzer)     ─── Buzzer        D14 (LED Amar.)───LED Amari│
│ D32 (Relé 2)     ─── Relé 2        GND ─── GND                │
│ D34 (IRQ NFC)    ─── PN532 IRQ     3V3 ─── 3V3                │
│ GND              ─── GND           GND ─── GND                │
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

### 2️⃣ BUS SPI (GPIO 18, 19, 23, 5)
```
              ESP32
               
         GPIO 18 (CLK)────────┐
         GPIO 23 (MOSI)───┐   │
         GPIO 19 (MISO)─┐ │   │
         GPIO 5 (CS)──┐ │ │   │
                      │ │ │   │
                   ┌──┴─┴─┴───┴────┐
                   │     PN532      │
                   │   NFC Reader   │
                   │                │
                   │ CLK: GPIO 18   │
                   │ DIN: GPIO 23   │
                   │ DOUT: GPIO 19  │
                   │ CE: GPIO 5     │
                   │ IRQ: GPIO 34   │
                   │                │
                   │ VCC: 3.3V ⚠️   │
                   │ GND: GND      │
                   └────────────────┘
                        ↑
                    Importante:
                    ⚠️ SOLO 3.3V
                    ❌ NO 5V
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

### 4️⃣ SALIDAS DIGITALES (GPIO Directos)
```
    GPIO 25 ──>[220Ω]──→ LED Rojo
    GPIO 27 ──>[220Ω]──→ LED Verde
    GPIO 14 ──>[220Ω]──→ LED Amarillo
    GPIO 33 ──────────→ Buzzer (PWM)
    GPIO 26 ──────────→ Relé 1 (activo LOW)
    GPIO 32 ──────────→ Relé 2 (activo LOW)
    
    Todas → GND (Tierra común)
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
// SPI Bus
SCLK = GPIO 18 (Clock)
MOSI = GPIO 23 (Master Out Slave In)
MISO = GPIO 19 (Master In Slave Out)
SS   = GPIO 5  (Chip Select)

// Inicialización:
SPI.begin(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);
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
| SPI | Clock | 1 | MHz |
| SPI | CLK Pin | 18 | GPIO |
| SPI | MOSI Pin | 23 | GPIO |
| SPI | MISO Pin | 19 | GPIO |
| SPI | CS Pin | 5 | GPIO |
| UART2 | Baud Rate | 256000 | bps |
| UART2 | RX Pin | 16 | GPIO |
| UART2 | TX Pin | 17 | GPIO |

---

## 📝 NOTAS IMPORTANTES

1. **PN532 Alimentación:** Usar EXACTAMENTE 3.3V. No conectar a 5V.
2. **I2C Bus:** Compartido por 3 sensores. Las direcciones no deben conflictuar.
3. **SPI Velocidad:** PN532 soporta hasta 10 MHz, pero configurado a 1 MHz para estabilidad.
4. **Relés Activos en LOW:** GPIO HIGH = APAGADO, GPIO LOW = ENCENDIDO.
5. **Capacitores:** Colocar capacitores de 0.1µF cerca de pines VCC de sensores.
6. **Pull-ups I2C:** Si es necesario, agregar resistencias 10kΩ entre SDA/SCL y 3.3V.

---

## 📞 REFERENCIA RÁPIDA

```
╔════════════════════════════════════════════════════╗
║           PINOUT RÁPIDO ESP32                      ║
╠════════════════════════════════════════════════════╣
║ SENSORES I2C (Bus Compartido):                    ║
║   SDA (GPIO 21) / SCL (GPIO 22)                   ║
║   Componentes: BME280, BH1750, OLED               ║
║                                                   ║
║ SENSOR SPI (PN532 NFC):                           ║
║   CLK(18) MOSI(23) MISO(19) CS(5) IRQ(34)         ║
║                                                   ║
║ SENSOR SERIAL (LD2410 Radar):                     ║
║   RX(16) / TX(17) @ 256000 baud                   ║
║                                                   ║
║ INDICADORES:                                      ║
║   LED Rojo(25) Verde(27) Amarillo(14)             ║
║   Buzzer(33) / Relé1(26) Relé2(32)               ║
╚════════════════════════════════════════════════════╝
```

---

**Documento:** Tabla Completa de Pines ESP32  
**Proyecto:** Control Asistencia IoT UEX  
**Actualización:** Febrero 2026  
**Versión:** 1.0
