# 🔧 GUÍA DE CONEXIONADO FÍSICO - DISPOSITIVO ESP32

## 📏 RESUMEN VISUAL DE CONEXIONES

### Tabla de Conexiones Rápida (Todos los Componentes)

```
╔═══════════════════════════════════════════════════════════════════════════╗
║                    MATRIZ DE CONEXIONES - TODAS LAS LÍNEAS                ║
╠═══════════════════════════════════════════════════════════════════════════╣
║  COMPONENTE        │ PIN ESP32  │  VOLTAJE  │  PROTOCOLO  │   DATOS      ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                   SENSORES AMBIENTALES                                    ║
║  BME280            │ 21/22 I2C  │ 3.3V      │ I2C 0x76    │ T/H/P       ║
║  BH1750            │ 21/22 I2C  │ 3.3V      │ I2C 0x23    │ Lux         ║
║                   SENSORES DE PRESENCIA                                   ║
║  LD2410 Radar      │ 16/17 UART │ 3.3V/5V   │ Ser2 256k   │ Dist/Mvto   ║
║  PN532 NFC         │ 5/18/19/23 │ 3.3V ⚠️   │ SPI +GPIO34 │ UID/Cards   ║
║                   INDICADORES VISUALES                                    ║
║  LED Rojo          │ GPIO 25    │ 3.3V      │ Digital PWM │ Error       ║
║  LED Verde         │ GPIO 27    │ 3.3V      │ Digital PWM │ OK          ║
║  LED Amarillo      │ GPIO 14    │ 3.3V      │ Digital PWM │ Advert.     ║
║  OLED Display      │ 21/22 I2C  │ 3.3V      │ I2C 0x3C    │ Screen      ║
║                   ACTUADORES                                             ║
║  Relé 1            │ GPIO 26    │ 3.3V      │ Digital LO  │ Control     ║
║  Relé 2            │ GPIO 32    │ 3.3V      │ Digital LO  │ Control     ║
║  Buzzer            │ GPIO 33    │ 3.3V      │ PWM Variable│ Sound/Alert ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## 🎯 INSTRUCCIONES DE CONEXIONADO POR PROTOCOLO

### 🔌 CONEXIONES I2C (BUS COMPARTIDO - GPIO 21 SDA, GPIO 22 SCL)

#### Paso 1: ACT physical strip de resistencias pull-up (OPCIONAL)
```
Si la placa ESP32 ya tiene pull-ups internos (típicamente sí), saltar este paso.
Si no, soldar:
  
    3.3V
     │
    10kΩ resistor
     │
    SDA (GPIO 21)
    
    3.3V
     │
    10kΩ resistor
     │
    SCL (GPIO 22)
```

#### Paso 2: Conectar BME280
```
BME280 Pinout (5 pines típico):
┌─────────────────┐
│ VCC  SDA  SCL   │
│      GND   CSB  │
└─────────────────┘

Conexión:
  BME280.VCC   → ESP32.3.3V
  BME280.GND   → ESP32.GND
  BME280.SDA   → ESP32.GPIO 21 (SDA I2C)
  BME280.SCL   → ESP32.GPIO 22 (SCL I2C)
  BME280.CSB   → ESP32.3.3V (fuerza modo I2C)
  
Dirección I2C: 0x76 (si hay puente, puede ser 0x77)
```

#### Paso 3: Conectar BH1750
```
BH1750 Pinout (6 pines tipico):
┌──────────────────┐
│ GND   VCC   ADDR │
│       SDA   SCL  │
└──────────────────┘

Conexión:
  BH1750.VCC   → ESP32.3.3V
  BH1750.GND   → ESP32.GND
  BH1750.SDA   → ESP32.GPIO 21 (SDA I2C - compartido)
  BH1750.SCL   → ESP32.GPIO 22 (SCL I2C - compartido)
  BH1750.ADDR  → GND o 3.3V (selecciona dirección 0x23 o 0x5C)
  
Dirección I2C: 0x23 (ADDR→GND) o 0x5C (ADDR→3.3V)
```

#### Paso 4: Conectar OLED Display (SSD1306)
```
OLED Pinout (4 pines típico):
┌────────────┐
│ GND  VCC   │
│ SDA  SCL   │
└────────────┘

Conexión:
  OLED.GND    → ESP32.GND
  OLED.VCC    → ESP32.3.3V
  OLED.SDA    → ESP32.GPIO 21 (SDA I2C - compartido)
  OLED.SCL    → ESP32.GPIO 22 (SCL I2C - compartido)
  
Dirección I2C: 0x3C (algunas placas pueden ser 0x3D)
Resolución: 128x64 píxeles
```

#### ✅ Diagrama I2C Final
```
ESP32
│
├─ GPIO 21 (SDA) ──┬─→ BME280.SDA (0x76)
│                 ├─→ BH1750.SDA (0x23 o 0x5C)
│                 └─→ OLED.SDA (0x3C)
│
├─ GPIO 22 (SCL) ──┬─→ BME280.SCL
│                 ├─→ BH1750.SCL
│                 └─→ OLED.SCL
│
├─ 3.3V ──→ [Resistencias 10kΩ pull-up] → SDA/SCL (opcional)
│
└─ GND (común) ──→ Tierra de todos los dispositivos
```

---

### 🔌 CONEXIONES SPI (PN532 NFC - GPIO 5, 18, 19, 23, 34)

```
PN532 Pinout (8+ pines típico):
┌─────────────────────────┐
│ GND  MISO MOSI SCK  CS  │
│ IRQ  3.3V  (RST)       │
└─────────────────────────┘

Conexión CRÍTICA:
  PN532.VCC   → ESP32.3.3V ⚠️ (NUNCA 5V!!!)
  PN532.GND   → ESP32.GND (tierra común)
  
  PN532.SCK   → ESP32.GPIO 18 (SPI Clock)
  PN532.MISO  → ESP32.GPIO 19 (Master In Slave Out)
  PN532.MOSI  → ESP32.GPIO 23 (Master Out Slave In)
  PN532.CS    → ESP32.GPIO 5  (Chip Select)
  PN532.IRQ   → ESP32.GPIO 34 (Interrupción, entrada)
  PN532.RST   → Sin conectar o a 3.3V (generan reset por software)

IMPORTANTE:
⚠️  DEBE SER 3.3V EXACTAMENTE
⚠️  EL MÓDULO TIENE REGULADOR PERO NO TOLERA 5V
⚠️  USAR CABLES CORTOS PARA SPI (< 10 cm)
```

#### ✅ Diagrama SPI Final
```
ESP32
│
├─ GPIO 18 (SCK)  ──→ PN532.SCK
├─ GPIO 23 (MOSI) ──→ PN532.MOSI
├─ GPIO 19 (MISO) ←── PN532.MISO
├─ GPIO 5 (CS)    ──→ PN532.CS
├─ GPIO 34 (IRQ)  ←── PN532.IRQ (entrada, no usa PWM)
│
├─ 3.3V ───→ PN532.VCC ⚠️ CRÍTICO
│
└─ GND ────→ PN532.GND (común)
```

---

### 🔌 CONEXIONES UART (LD2410 RADAR - GPIO 16, 17)

```
LD2410 Pinout (4+ pines típico):
┌──────────────┐
│ GND  3.3V    │
│ TX   RX      │
└──────────────┘

Conexión:
  LD2410.VCC  → ESP32.3.3V (o 5V si el módulo lo soporta)
  LD2410.GND  → ESP32.GND
  
  LD2410.TX   → ESP32.GPIO 16 (RX de Serial2)
  LD2410.RX   → ESP32.GPIO 17 (TX de Serial2)
  
Velocidad Serial: 256000 baud (NO cambiar sin actualizar código)
```

#### ✅ Diagrama UART Final
```
ESP32 Serial2
│
├─ GPIO 16 (RX) ←── LD2410.TX (salida del radar)
├─ GPIO 17 (TX) ──→ LD2410.RX (entrada del radar)
│
├─ 3.3V (o 5V) ──→ LD2410.VCC
│
└─ GND ┬──→ LD2410.GND
       │   (tierra común)
```

---

### 🔌 CONEXIONES DIGITALES DIRECTAS

#### LEDs Indicadores (3 unidades)
```
Genérico LED RGB/Indicadores:
┌─────┐
│Λ │ Ánodo (+)
│ │ Cátodo (-)
└─────┘

LED Rojo:
  VCC ──[220Ω resistor 1/4W]──→ LED Rojo Ánodo
  LED Rojo Cátodo ──→ ESP32.GPIO 25
  Estado: HIGH = ENCENDIDO, LOW = APAGADO
  
LED Verde:
  VCC ──[220Ω resistor 1/4W]──→ LED Verde Ánodo
  LED Verde Cátodo ──→ ESP32.GPIO 27
  Estado: HIGH = ENCENDIDO, LOW = APAGADO

LED Amarillo:
  VCC ──[220Ω resistor 1/4W]──→ LED Amarillo Ánodo
  LED Amarillo Cátodo ──→ ESP32.GPIO 14
  Estado: HIGH = ENCENDIDO, LOW = APAGADO
```

#### Buzzer Piezo (PWM)
```
Buzzer Pasivo (SIN oscilador):
┌─────────────┐
│  (-) (+)    │ o │  Rojo  Negro │
└─────────────┘

Conexión:
  ESP32.GPIO 33 (PWM) ──→ Buzzer (+)
  Buzzer (-)          ──→ ESP32.GND
  
Opcional:
  Capacitor 10µF entre GPIO 33 y GND (suaviza PWM)
  
PWM Frecuencia: Variable (80 Hz - 40 kHz)
```

#### Relés (2 unidades - Activos en LOW)
```
Módulo Relé (típico):
┌──────────────────┐
│ GND  VCC  IN1 IN2│
└──────────────────┘

Relé 1:
  Módulo.VCC ──→ ESP32.3.3V
  Módulo.GND ──→ ESP32.GND
  Módulo.IN1 ──→ ESP32.GPIO 26
  
  Lógica: GPIO 26 = LOW → Relé ACTIVADO
          GPIO 26 = HIGH → Relé DESACTIVADO
  
Relé 2:
  Módulo.VCC ──→ ESP32.3.3V
  Módulo.GND ──→ ESP32.GND
  Módulo.IN2 ──→ ESP32.GPIO 32
  
  Lógica: GPIO 32 = LOW → Relé ACTIVADO
          GPIO 32 = HIGH → Relé DESACTIVADO
```

#### ✅ Diagrama Digitales Final
```
ESP32
│
├─ GPIO 25 ──[220Ω]──→ LED Rojo Ánodo
├─ GPIO 27 ──[220Ω]──→ LED Verde Ánodo
├─ GPIO 14 ──[220Ω]──→ LED Amarillo Ánodo
│
├─ GPIO 33 (PWM) ──→ Buzzer (+)
│                     │
│                     [10µF cap - opcional]
│                     │
├─ GPIO 26 ──→ Módulo Relé IN1
├─ GPIO 32 ──→ Módulo Relé IN2
│
├─ 3.3V ──→ [Módulo Relé VCC]
│
└─ GND (tierra común) ──┬─→ Todos los Cátodos LED
                        ├─→ Todos los pines GND
                        ├─→ Buzzer (-)
                        └─→ Módulo Relé GND
```

---

## ⚡ ESQUEMA FÍSICO COMPLETO

```
┌──────────────────────────────────────────────────────────────┐
│                    FUENTE DE ALIMENTACIÓN                     │
│                                                               │
│  USB 5V o Batería LiPo 3.7V/7.4V                             │
│         ↓                                                      │
│  ┌──────────────────────────────────────────┐               │
│  │ Regulador Buck 5V→3.3V (si es USB)       │               │
│  │ o conexión directa (si es batería)       │               │
│  └──────────────────────────────────────────┘               │
│         ↓                                                      │
│      3.3V (CARRIL POSITIVO)                                  │
│         ↓                                                      │
│    ┌────┴────────────────┬─────────────────────────┐        │
│    │                     │                         │        │
│  [C1]              CARRIL 3.3V            [FUSE 500mA]     │
│ 100µF                    │                         │        │
│    │                     ├─────→ BME280.VCC        │        │
│    │                     ├─────→ BH1750.VCC        │        │
│    │                     ├─────→ OLED.VCC          │        │
│    │                     ├─────→ PN532.VCC (3.3V!) │        │
│    │                     ├─────→ LD2410.VCC        │        │
│    │                     ├─────→ Módulo Relé.VCC   │        │
│    │                     └─────→ ESP32.3V3         │        │
│    │                             (entrada)         │        │
│    GND                                             GND      │
│    ↓ (CARRIL NEGATIVO - TIERRA COMÚN)              ↓        │
│    │                                                │        │
│    ├─→ BME280.GND                                  │        │
│    ├─→ BH1750.GND                                  │        │
│    ├─→ OLED.GND                                    │        │
│    ├─→ PN532.GND                                   │        │
│    ├─→ LD2410.GND                                  │        │
│    ├─→ LED Rojo Cátodo (vía GPIO 25)               │        │
│    ├─→ LED Verde Cátodo (vía GPIO 27)              │        │
│    ├─→ LED Amarillo Cátodo (vía GPIO 14)           │        │
│    ├─→ Buzzer (-) (vía GPIO 33)                    │        │
│    ├─→ Módulo Relé.GND                             │        │
│    └─→ ESP32.GND (entrada)                         │        │
│                                                    │        │
│    Capacitor cerámico 0.1µF cerca de pines        │        │
│    de alimentación de cada sensor I2C             │        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ LISTA COMPLETA DE MATERIALES

| Componente | Cantidad | Especificación | Notas |
|-----------|----------|-----------------|-------|
| **ESP32** | 1 | WROOM-32 | Placa principal |
| **BME280** | 1 | Sensor I2C 0x76 | Temperatura/Humedad/Presión |
| **BH1750** | 1 | Sensor I2C 0x23 | Luxómetro |
| **LD2410** | 1 | Radar 24GHz UART | Detección de presencia |
| **PN532** | 1 | Lector NFC SPI 3.3V | ⚠️ SOLO 3.3V |
| **OLED 0.95"** | 1 | SSD1306 I2C 0x3C | Pantalla 128x64 |
| **LED Rojo** | 1 | 3mm/5mm 5V-3.3V | Indicador |
| **LED Verde** | 1 | 3mm/5mm 5V-3.3V | Indicador |
| **LED Amarillo** | 1 | 3mm/5mm 5V-3.3V | Indicador |
| **Resistor** | 3 | 220Ω 1/4W | Para LEDs |
| **Resistor** | 2 | 10kΩ 1/4W | Pull-up I2C (opcional) |
| **Buzzer** | 1 | Pasivo piezo 3.3V | Indicador sonoro |
| **Capacitor** | 2 | 100µF 6.3V+ | Filtrado de potencia |
| **Capacitor** | 4 | 0.1µF cerámica | Por sensor I2C |
| **Capacitor** | 1 | 10µF electrolítico | GPIO 33 (opcional) |
| **Módulo Relé** | 1 | 2 canales 3.3V | Relé 1 y 2 |
| **Fusible** | 1 | 500mA | Protección general |
| **Cables** | Varios | Dupont/Jumper M-H | Conexiones |
| **Protoboard** | 1 | 830 pines (opcional) | Para prototipado |

---

## 🔍 CHECKLIST PRE-CONEXIONADO

- [ ] He revisado los datasheets de MISsensores
- [ ] Tengo todos los materiales listados arriba
- [ ] El PN532 es versión 3.3V (NO 5V)
- [ ] Tengo un multímetro para verificar continuidad
- [ ] He hecho una copia de este diagrama en papel
- [ ] Voy a usar cables de colores para diferenciar: Rojo (3.3V), Negro (GND), etc.
- [ ] Desconectarto la alimentación antes de hacer cambios

---

## 🚀 PROCESO DE CONEXIONADO RECOMENDADO

### Fase 1: Preparación
1. Descargar schematic oficial ESP32
2. Imprimir esta guía
3. Montar componentes en protoboard sin soldar primero
4. Verificar visualmente todas las conexiones

### Fase 2: Conexionado de Potencia
1. Instalar regulador 5V → 3.3V (si es necesario)
2. Conectar carril 3.3V con todos los VCC
3. Conectar carril GND con todos los GND
4. Instalar fusible de 500mA antes de encender

### Fase 3: Bus I2C
1. Conectar SDA (GPIO 21) a todos los SDA de sensores (BME, BH, OLED)
2. Conectar SCL (GPIO 22) a todos los SCL de sensores
3. Agregar pull-ups de 10kΩ si es necesario
4. Verificar con multímetro continuidad

### Fase 4: Bus SPI (PN532)
1. Conectar Clock (GPIO 18) → PN532.SCK
2. Conectar MOSI (GPIO 23) → PN532.MOSI
3. Conectar MISO (GPIO 19) → PN532.MISO
4. Conectar CS (GPIO 5) → PN532.CS
5. Conectar IRQ (GPIO 34) → PN532.IRQ
6. **VERIFICAR 3.3V en PN532** con multímetro

### Fase 5: UART Serial2 (LD2410)
1. Conectar GPIO 16 (RX) → LD2410.TX
2. Conectar GPIO 17 (TX) → LD2410.RX
3. Conectar potencia y GND

### Fase 6: Salidas Digitales
1. Conectar LEDs (con resistencias 220Ω)
2. Conectar Buzzer a GPIO 33
3. Conectar Módulo Relé a GPIO 26 y 32

### Fase 7: Prueba
1. ENCENDER SIN NINGÚN SENSOR PRIMERO
2. Ver que LEDs hacen secuencia
3. Conectar sensores UNO A UNO
4. Monitorear Serial a 115200 baud
5. Verificar que cada sensor report "✅"

---

## ⚠️ PROBLEMAS COMUNES Y SOLUCIONES

| Problema | Causa Probable | Solución |
|----------|-----------------|----------|
| PN532 no detecta | Voltaje 5V | Verificar exactamente 3.3V con multímetro |
| I2C no responde | Cables sollados | Usar cables Dupont buenos, verificar continuidad |
| Sensor BME no responde | Dirección I2C incorrecta | Verificar 0x76 en datasheet, hay variantes |
| OLED no aparece | Cables I2C cruzados | Intercambiar SDA↔SCL |
| LD2410 datos aleatorios | Baud rate incorrecto | Mantener 256000 baud |
| LEDs no encienden | GPIO invertido | Revisar orden rojo(25), verde(27), amarillo(14) |
| Buzzer muy bajo | Frecuencia PWM baja | Aumentar frecuencia en indicators.ino |

---

## 📞 VERIFICACIÓN FINAL

Antes de dar por válido el conexionado:

```
╔════════════════════════════════════════════════════╗
║  TEST EN SERIE (Aplicar en este orden):           ║
╠════════════════════════════════════════════════════╣
║ 1. Comprobación de Potencia                       ║
║    □ 3.3V presente en carril de 3.3V              ║
║    □ GND omún en todas las capas                  ║
║    □ Sin cortocircuitos entre VCC y GND           ║
║                                                   ║
║ 2. Comprobación I2C                              ║
║    □ SDA y SCL sin cortocircuito entre sí         ║
║    □ Continuidad en cables I2C                    ║
║    □ Pull-ups funcionando (si están)              ║
║                                                   ║
║ 3. Comprobación SPI                              ║
║    □ Cables SPI no cruzados                       ║
║    □ CS activo en LOW                             ║
║    □ PN532 recibe exactamente 3.3V                ║
║                                                   ║
║ 4. Comprobación UART                              ║
║    □ TX y RX no invertidosy                       ║
║    □ Baud rate configurado a 256000               ║
║                                                   ║
║ 5. Comprobación Digital                           ║
║    □ LEDs correctamente polarizados                ║
║    □ Resistencias de 220Ω en serie con LEDs       ║
║    □ Buzzer polaridad correcta                    ║
║    □ Relés lógica invertida (activo LOW)          ║
╚════════════════════════════════════════════════════╝
```

---

**Documento:** Guía de Conexionado Físico  
**Proyecto:** Control Asistencia IoT UEX  
**Actualización:** Febrero 2026  
**Versión:** 1.0 - Completa  
**Estado:** ✅ LISTO PARA IMPLEMENTACIÓN
