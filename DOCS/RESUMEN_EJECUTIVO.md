# ⚡ RESUMEN EJECUTIVO - COMPONENTES Y PINES ESP32

## 🎯 Proyecto: Control Asistencia IoT UEX - Sistema Integrado

---

## 📊 TABLA RESUMEN DE COMPONENTES

```
┌────────────────────────────────────────────────────────────────┐
│                   COMPONENTES DEL SISTEMA                      │
├────────────────────────────────────────────────────────────────┤
│ SENSORES (4)           ACTUADORES (3)      INDICADORES (5)     │
├────────────────────────────────────────────────────────────────┤
│ • BME280 (Temp/Hum)   • Relé 1 (GPIO26)   • LED Rojo (GPIO25)  │
│ • BH1750 (Luz)        • Relé 2 (GPIO32)   • LED Verde(GPIO27)  │
│ • LD2410 (Radar)                          • LED Amarillo(G14)  │
│ • PN532 (NFC)                             • OLED Display       │
│                                            • Buzzer (GPIO33)   │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔌 PINES UTILIZADOS (13 GPIO + 3 interfaces de comunicación)

### GPIOs Digitales
| Función | GPIO | Estado | Habilitado |
|---------|------|--------|-----------|
| LED Rojo | 25 | Output | ✅ |
| LED Verde | 27 | Output | ✅ |
| LED Amarillo | 14 | Output | ✅ |
| Buzzer | 33 | PWM Output | ✅ |
| Relé 1 | 26 | Output (Activo LOW) | ✅ |
| Relé 2 | 32 | Output (Activo LOW) | ✅ |

### Interfaces de Comunicación
| Protocolo | Pines ESP32 | Dispositivos | Velocidad |
|-----------|------------|--------------|-----------|
| **I2C** | 21 (SDA), 22 (SCL) | BME280, BH1750, OLED | 100 kHz |
| **SPI** | 18(SCK), 19(MISO), 23(MOSI), 5(CS), 34(IRQ) | PN532 NFC | 1 MHz |
| **UART2** | 16 (RX), 17 (TX) | LD2410 Radar | 256 kbaud |

---

## 📋 ESPECIFICACIONES CRÍTICAS

### ⚠️ **ADVERTENCIAS DE VOLTAJE**

```
✅  3.3V SAFE:      BME280, BH1750, OLED, PN532, Relés, LEDs, Buzzer
⚠️  5V TOLERADOS:   LD2410 (dual voltage)
❌  NUNCA 5V:       PN532 (destruye el chip)
```

### Direcciones I2C
```
0x76  → BME280
0x23  → BH1750 (ADDR→GND) o 0x5C (ADDR→3.3V)
0x3C  → OLED Display SSD1306
```

### Consumo Estimado
```
En reposo:     ~100 mA
Con sensores:  ~250-300 mA
Pico (todo):   ~500 mA
→ Usar fuente mínimo 1A @ 5V o 3.7V/7.4V Li-Po
```

---

## 🚀 SECUENCIA DE FUNCIONAMIENTO

```
┌─────────────────┐
│   ENCENDIDO     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ INICIALIZACIÓN EN ORDEN:        │
├─────────────────────────────────┤
│ 1. LEDs + Buzzer + Relés        │
│ 2. PN532 (NFC)                  │
│ 3. LD2410 (Radar)               │
│ 4. BME280 (Temperatura)         │
│ 5. BH1750 (Luz)                 │
│ 6. OLED (Display)               │
│ 7. Sistema Listo ✅             │
└─────────────────────────────────┘

INTERVALOS DE OPERACIÓN:
├─ Lectura Sensores:      5 segundos
├─ Update OLED:           1 segundo
├─ Polling NFC:           100 ms (no bloqueante)
├─ Procesamiento Cola:    30 segundos
└─ Actualización Clase:   5 minutos
```

---

## 🎨 ESTADOS DE INDICADORES

### LEDs
```
Estado      │ Rojo | Verde | Amarillo │ Significado
────────────┼──────┼───────┼──────────┼─────────────────────
NORMAL      │  OFF │  ON   │   OFF    │ Sistema OK
ADVERTENCIA │  OFF │  OFF  │ PARPADEO │ Sensor no disponible
ERROR       │  ON  │  OFF  │   OFF    │ Fallo crítico
CRÍTICO     │PARPADEO OFF  │   OFF    │ Fallo muy grave
```

### Buzzer
```
beepCorto()   → 50 ms (confirmación)
beepLargo()   → 200 ms (alerta)
beepError()   → 3x beeps (error)
```

### Relés
```
LOW  = ENCENDIDO  (activo)
HIGH = APAGADO    (inactivo)
```

---

## 📡 DATOS QUE CAPTURA CADA SENSOR

| Sensor | Datos | Rango | Validación |
|--------|-------|-------|------------|
| **BME280** | Temp, Humedad, Presión | T: -40 a +85°C, H: 0-100%, P: 300-1100 hPa | ✅ Completa |
| **BH1750** | Luminosidad | 0-65535 lux | ✅ Completa |
| **LD2410** | Dist. estático, móvil | 0-600 cm | ✅ Completa |
| **PN532** | UID Tarjeta | 4-7 bytes | ✅ Validación ISO14443A |

---

## 🔄 FLUJO DE DATOS (Comunicación)

```
ESP32 (Core 1)                    ESP32 (Core 0)
Lectura Sensores (5s)             WiFi + WebSocket
    │                                   │
    ├─ I2C ──→ BME280 ────┐            │
    │                     ├───→ Cola    │
    ├─ I2C ──→ BH1750     │   (Datos)   │
    │                     │             │
    ├─ UART ──→ LD2410 ───┤             │ Conexión WSS
    │                     │             │
    ├─ SPI ──→ PN532 ─────┤             │
    │                     │             │
    └─ I2C ──→ OLED ◄─────┘             │
    (Actualiza pantalla)         Env. cada 30s
                                        │
                                   Servidor
                                   (HTTPS)
```

---

## 🛠️ LISTA DE VERIFICACIÓN FINAL

### Antes de Conectar
- [ ] Fuente de alimentación 5V/1A o batería Li-Po
- [ ] ESP32 sin daños (pines rectos)
- [ ] Todos los componentes recibidos
- [ ] PN532 versión **3.3V** (verificar etiqueta)
- [ ] Cables Dupont de calidad (no deshilachados)

### Durante Conexionado
- [ ] I2C: SDA(21) y SCL(22) a todos los sensores
- [ ] SPI: CLK(18), MOSI(23), MISO(19), CS(5) al PN532
- [ ] UART2: RX(16) y TX(17) al LD2410
- [ ] PN532: **Verificar 3.3V** con multímetro (CRÍTICO)
- [ ] GND: Tierra común en todas partes

### Después de Encender
- [ ] Serial Monitor (115200 baud) muestra inicialización
- [ ] LEDs hacen secuencia: Rojo→Amarillo→Verde
- [ ] OLED muestra "Control Asistencia - IoT UEX"
- [ ] Sensores: Todas las líneas con "✅"
- [ ] Sin errores "❌" en inicialización

---

## 📊 TABLA RÁPIDA DE TROUBLESHOOTING

| Síntoma | Causa Probable | Fix |
|---------|-----------------|-----|
| PN532 no aparece | 5V en PN532 | Cambiar a 3.3V |
| I2C "stuck" | Cables cruzados SDA/SCL | Intercambiar GPIO 21 y 22 |
| BME no responde | Dirección 0x77 no 0x76 | Revisar estrapa/jumper |
| OLED en blanco | Dirección 0x3D no 0x3C | Cambiar en config.h |
| LD2410 ruido | Cables largos/mal blindados | Usar cables cortos |
| Sistema lento | Core 0 sobrecargado | Reducir frecuencia WiFi |

---

## 🎓 ARCHIVOS DOCUMENTACIÓN GENERADA

```
📁 /ENUMERACION_COMPONENTES_ESP32.md  ← TÉCNICO COMPLETO
📁 /PINES_ESP32_DIAGRAMA.md           ← TABLA Y DIAGRAMAS
📁 /GUIA_CONEXIONADO_FISICO_ESP32.md  ← PASO A PASO
📁 /RESUMEN_EJECUTIVO.md              ← ESTE ARCHIVO (Hoja de referencia rápida)
```

---

## 📞 REFERENCIAS RÁPIDAS

### URLs Útiles (Datasheets)
```
BME280:  https://cdn-shop.adafruit.com/datasheets/bst-bme280-ds002.pdf
BH1750:  https://github.com/enjoyneering/BH1750/blob/master/BH1750.pdf
LD2410:  https://github.com/nquinn10/LD2410_ReloadedDriver/blob/main/LD2410.pdf
PN532:   https://cdn-shop.adafruit.com/datasheets/PN532.pdf
OLED:    https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf
```

### Librerías Arduino Utilizadas
```cpp
#include <Adafruit_BME280.h>      // BME280
#include <BH1750.h>               // BH1750
#include <ld2410.h>               // LD2410
#include <Adafruit_PN532.h>       // PN532
#include <Adafruit_SSD1306.h>     // OLED
#include <WebSocketsClient.h>     // WebSocket
#include <WiFiClientSecure.h>     // HTTPS
```

---

## 🔁 CICLO TÍPICO DE OPERACIÓN

### Cada 5 segundos (Core 1)
1. Leer BME280 → Temp, Humedad, Presión
2. Leer BH1750 → Luminosidad
3. Leer LD2410 → Presencia, Distancias
4. Polling PN532 → Tarjetas NFC

### Cada 1 segundo (Display)
1. Actualizar OLED con estado actual

### Cada 30 segundos (Core 0)
1. Procesar cola de mensajes
2. Enviar datos acumulados vía WebSocket

### Cada 12 horas (Seguridad)
1. Validar token JWT con servidor

---

## 💡 TIPS Y MEJORES PRÁCTICAS

✅ **DO:**
- Usar capacitores 0.1µF cerca de VCC de cada sensor I2C
- Mantener cables SPI cortoos (<10 cm)
- Verificar polaridad de LEDs y buzzer
- Usar resistencias 220Ω para LEDs
- Implementar soft reset en caso de fallo grave

❌ **DON'T:**
- Conectar PN532 a 5V (destruye el chip)
- Mezclar tierra de sensor NFC con otros I2C si no es necesario
- Dejar pines SPI flotantes
- Cambiar velocidades UART sin updatear código
- Conectar relés sin diodos de protección

---

## 📈 DIAGRAMA DE DEPENDENCIAS

```
ESP32 (Principal)
│
├─→ I2C (Wire)
│   ├─→ BME280 (Temperatura)
│   ├─→ BH1750 (Luz)
│   └─→ OLED (Display)
│
├─→ SPI (Nativa)
│   └─→ PN532 (NFC)
│
├─→ Serial2 (UART)
│   └─→ LD2410 (Radar)
│
├─→ GPIO Digital (Output)
│   ├─→ LED Rojo (25)
│   ├─→ LED Verde (27)
│   ├─→ LED Amarillo (14)
│   ├─→ Buzzer PWM (33)
│   ├─→ Relé 1 (26)
│   └─→ Relé 2 (32)
│
└─→ WiFi (Interna)
    └─→ WebSocket Seguro (WSS)
        └─→ Servidor HTTPS
```

---

## 📝 RESUMEN DE TIEMPOS

| Evento | Intervalo | Sincronización |
|--------|-----------|-----------------|
| Lectura Sensores | 5 seg | Sin bloqueo |
| Display OLED | 1 seg | Cada segundo |
| Cola Procesamiento | 30 seg | Acumulativo |
| Token Validación | 12 horas | Automático |
| Polling NFC | 100 ms | No bloqueante |
| Cooldown NFC | 3 seg | Anti-rebote |

---

## 🎯 OBJETIVOS DEL SISTEMA

✅ Registro automático de asistencia (NFC)  
✅ Monitoreo ambiental (Temperatura, Humedad, Luz)  
✅ Detección de presencia (Radar 24GHz)  
✅ Control domótico (Relés x2)  
✅ Notificaciones visuales (LEDs + OLED)  
✅ Alertas sonoras (Buzzer)  
✅ Comunicación segura (JWT + WSS)  

---

**Sistema:** Control Asistencia IoT UEX  
**Versión Hardware:** ESP32 WROOM-32  
**Componentes:** 13 GPIO + 3 interfaces de comunicación  
**Estado:** ✅ COMPLETAMENTE DOCUMENTADO  
**Fecha:** Febrero 2026  

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Revisar este documento
2. ✅ Obtener lista de componentes
3. ✅ Cargar código en ESP32
4. ✅ Realizar test de inicialización
5. ✅ Calibrar sensores
6. ✅ Conectar a servidor HTTPS
7. ✅ Validar flujo de datos

---

**¿Preguntas?** Consultar archivos de documentación principal:
- `ENUMERACION_COMPONENTES_ESP32.md` (Especificaciones técnicas)
- `PINES_ESP32_DIAGRAMA.md` (Diagramas y tablas)
- `GUIA_CONEXIONADO_FISICO_ESP32.md` (Paso a paso de conexión)
