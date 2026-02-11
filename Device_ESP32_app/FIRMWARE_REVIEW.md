# Evaluación Firmware ESP32 - Embedded Systems Review

**Proyecto:** Control de Asistencia IoT — Nodo ESP32  
**Evaluador:** Embedded Systems Agent  
**Fecha:** 2026-02-11  
**Plataforma:** ESP32 (Dual-Core Xtensa LX6, 520KB SRAM, WiFi/BLE)

---

## 📊 Puntuación General: 6.8 / 10

| Categoría | Nota | Peso |
|-----------|------|------|
| Arquitectura y Modularización | 7.5/10 | 15% |
| Gestión de Memoria (RAM/Flash) | 5.5/10 | 20% |
| Seguridad | 4.0/10 | 20% |
| Fiabilidad y Recuperación de Errores | 7.0/10 | 15% |
| Concurrencia y Tiempo Real | 6.5/10 | 15% |
| Eficiencia Energética | 5.0/10 | 5% |
| Comunicaciones (WiFi/WS/HTTPS) | 7.0/10 | 10% |

---

## ✅ Aspectos Positivos (Lo que está bien hecho)

### 1. Modularización por archivos `.ino`
Separación limpia por funcionalidad: sensores, comunicaciones, indicadores, NFC, display, cola offline. Facilita el mantenimiento y la lectura.

### 2. Sistema de cola offline (`cola_envio_offline.ino`)
Excelente decisión de diseño. Si la red falla, los fichajes y datos de sensores se persisten en NVS (flash) y se reenvían cuando se recupera la conexión. Máximo 50 eventos, con compactación y reintentos limitados a 5.

### 3. Estructuras de datos bien definidas
`SensorStatus`, `BME280Data`, `LuzData`, `NFCData`, `RadarData` — typesafe, con flag `.valido` para control de errores. Buena práctica para embedded.

### 4. Validación de rangos de sensores
Cada módulo valida rangos realistas (BME280: -40°C a 85°C, BH1750: 0 a 65535 lux, LD2410: 0 a 600 cm). Previene envío de datos basura al servidor.

### 5. Timer hardware para fin de clase
Uso correcto de `hw_timer_t` con ISR `IRAM_ATTR` y flag `volatile`. El timer dispara automáticamente el reset de estado al acabar la clase.

### 6. Reintentos en inicialización de sensores
BME280, BH1750 y PN532 se reintentan 3-4 veces con delays. Manejo robusto de sensores que fallan intermitentemente.

### 7. Dual-core con FreeRTOS task
Comunicaciones en Core 0, lógica de sensores/NFC en Core 1 (loop). Evita que la latencia de red bloquee la lectura NFC.

---

## 🔴 Hallazgos Críticos (Prioridad Alta)

### H1. 🔴 SSL Deshabilitado en Producción

**Archivos:** `api_rest.ino:12`, `auth_device_jwt.ino:57`, `api_rest.ino:225`

```cpp
client.setInsecure(); // ⚠️ TEMPORAL: Desactiva validación SSL para debugging
```

**Impacto:** Todas las conexiones HTTPS y WSS son vulnerables a ataques Man-in-the-Middle. Un atacante en la red podría interceptar:
- Tokens JWT
- UIDs de tarjetas NFC
- Credenciales `apiKey` del dispositivo
- Datos de sensores

**Recomendación:**
```cpp
// ✅ Usar el certificado que YA está definido en globals.cpp
client.setCACert(server_certificate);
// ELIMINAR: client.setInsecure();
```

**Severidad:** CRÍTICA — El certificado ya está cargado en memoria pero no se usa.

---

### H2. 🔴 Credenciales Hardcodeadas en Código Fuente

**Archivo:** `globals.cpp:10-14`

```cpp
String deviceId = "node-002";
String apiKey = "V3cC5xZ8mN1bB4vL9kH2jG7fD6sA0pQ";
const char* ssid = "SERVER";
const char* password = "12345678";
```

**Impacto:** Si el firmware se extrae del dispositivo (fácil con `esptool.py`), un atacante obtiene:
- API Key para suplantar el dispositivo
- Credenciales WiFi de la red
- Device ID para ataques de impersonación

**Recomendación:** Usar NVS (Non-Volatile Storage) cifrado con `nvs_flash_secure_init()`:
```cpp
// Provisionar en fábrica, no en código fuente
Preferences creds;
creds.begin("secrets", true); // namespace "secrets", read-only
String apiKey = creds.getString("api_key", "");
String ssid = creds.getString("wifi_ssid", "");
```

---

### H3. 🔴 Token JWT en URL WebSocket (Query String)

**Archivo:** `webSocketEvent.ino:508`

```cpp
String path = "/ws?token=" + token;
webSocket.beginSSL(wsHost, wsPort, path.c_str());
```

**Impacto:** El token JWT viaja en la URL, que puede ser registrada en logs del servidor, proxies, o firewalls. Además, la URL completa (con token) se imprime en Serial.

**Recomendación:** Enviar el token como header HTTP o como primer mensaje tras conexión:
```cpp
// Opción 1: Header (requiere soporte del servidor)
webSocket.setExtraHeaders(("Authorization: Bearer " + token).c_str());

// Opción 2: Enviar como primer mensaje (ya lo hace parcialmente con nodo_conectado)
```

---

### H4. 🔴 DynamicJsonDocument en Dispositivo con RAM Limitada

**Archivo:** `auth_device_jwt.ino:74`

```cpp
DynamicJsonDocument res(1024); // ← Asignación dinámica en heap
```

**Impacto:** `DynamicJsonDocument` usa `malloc()` interno. En ESP32 con heap fragmentado, puede fallar silenciosamente. ArduinoJson v7 ya deprecó `DynamicJsonDocument`.

**Recomendación:** Usar siempre `StaticJsonDocument` (stack) o `JsonDocument` (v7):
```cpp
StaticJsonDocument<512> res;  // Tamaño fijo en stack
// El payload del token raramente supera 512 bytes
```

---

## 🟡 Hallazgos Importantes (Prioridad Media)

### H5. 🟡 Stack Size del Task FreeRTOS Insuficiente

**Archivo:** `Device_ESP32_app.ino:100`

```cpp
xTaskCreatePinnedToCore(
    HiloComunicadorcode,
    "HiloComunicador",
    10000,     // 10KB de stack
    NULL, 1, &HiloComunicador, 0);
```

**Problema:** El task `HiloComunicador` ejecuta operaciones SSL (WebSocket), serialización JSON, y procesamiento de cola. Estas operaciones pueden consumir >8KB de stack. Con 10KB hay poco margen.

**Recomendación:**
```cpp
xTaskCreatePinnedToCore(
    HiloComunicadorcode,
    "HiloComunicador",
    16384,  // 16KB - margen seguro para SSL + JSON
    NULL, 1, &HiloComunicador, 0);

// Añadir monitoreo de stack en el loop del task:
Serial.printf("Stack libre HiloComunicador: %d bytes\n", 
              uxTaskGetStackHighWaterMark(NULL));
```

---

### H6. 🟡 Race Condition: Variables Compartidas sin Protección

**Variables afectadas:** `wsConectado`, `aula`, `claseEnCurso`, `relay1Estado`, `relay2Estado`

Estas variables se leen/escriben desde **ambos cores** sin mutex ni secciones críticas:
- Core 0 (HiloComunicador): Modifica `wsConectado`, `aula`, `relay*Estado` vía WebSocket
- Core 1 (loop): Lee `claseEnCurso`, `wsConectado`, modifica `fichajeClaseCompletado`

**Recomendación:**
```cpp
// En globals.h
extern SemaphoreHandle_t xMutexEstado;

// En globals.cpp
SemaphoreHandle_t xMutexEstado = xSemaphoreCreateMutex();

// Uso:
if (xSemaphoreTake(xMutexEstado, pdMS_TO_TICKS(100))) {
    wsConectado = true;
    xSemaphoreGive(xMutexEstado);
}
```

---

### H7. 🟡 Display Lee Sensores en Cada Update (1 segundo)

**Archivo:** `display_module.ino:164-182`

```cpp
void updateDisplay() {
    // ...
    BME280Data bmeData = leerBME280();  // Lee I2C cada segundo
    LuzData luzData = leerLuz();         // Lee I2C cada segundo
    RadarData radarData = leerRadar();   // Lee UART cada segundo
}
```

**Problema:** La función `updateDisplay()` llama a `leerBME280()`, `leerLuz()` y `leerRadar()` directamente. Estos ya se leen en `EnviaValoresAula()` cada 5 segundos. Resultado: **doble lectura** de sensores I2C y conflictos potenciales en el bus.

**Recomendación:** Cachear los últimos datos válidos:
```cpp
// En globals.h
extern BME280Data ultimosBME;
extern LuzData ultimaLuz;
extern RadarData ultimoRadar;

// En EnviaValoresAula() (donde ya se leen):
ultimosBME = leerBME280();
ultimaLuz = leerLuz();
ultimoRadar = leerRadar();

// En updateDisplay():
if (ultimosBME.valido) {
    display.print(ultimosBME.temperatura, 1);
}
```

---

### H8. 🟡 Cola Offline: Sin FIFO Real, Gaps tras Reenvío

**Archivo:** `cola_envio_offline.ino`

**Problema:** La cola usa indices `evt_0`, `evt_1`, etc. Cuando se reenvía y elimina `evt_2`, queda un hueco. `compactQueue()` intenta rellenar pero se ejecuta con `queuePrefs` ya abierto — no es atómico respecto a `saveToQueue()`.

Además, `processQueue()` llama a `queuePrefs.begin()` / `queuePrefs.end()` pero `compactQueue()` NO — asume que ya está abierto. Si se llama desde otro contexto, fallará.

**Recomendación:** Usar un buffer circular simple:
```cpp
struct QueueBuffer {
    int head = 0;
    int tail = 0;
    int count = 0;
};
```

---

### H9. 🟡 `delay()` Bloqueantes en Task FreeRTOS

**Archivos:** Múltiples archivos

```cpp
// En api_rest.ino
delay(500);   // Bloquea 500ms tras LED verde
delay(1500);  // Bloquea 1.5s tras error 400
delay(1000);  // Bloquea 1s tras error 404

// En wifi_manager.ino
delay(500);   // Dentro del loop de reconexión WiFi
```

**Problema:** `delay()` en FreeRTOS no cede el procesador; simplemente espera. Debería usarse `vTaskDelay()`.

**Recomendación:**
```cpp
vTaskDelay(pdMS_TO_TICKS(500));  // Cede CPU a otras tareas durante 500ms
```

---

### H10. 🟡 Logging Excesivo (Impacto en Rendimiento)

**Impacto:** ~100+ llamadas a `Serial.println()` con emojis UTF-8 (3-4 bytes cada uno). A 115200 baudios, un log típico de 200 caracteres tarda ~17ms. En el peor caso (WebSocket event + sensor read + display update), se acumulan >100ms de latencia solo por logging.

**Recomendación:** Compilar con niveles de log:
```cpp
#define LOG_LEVEL_DEBUG 0
#define LOG_LEVEL_INFO  1
#define LOG_LEVEL_WARN  2
#define LOG_LEVEL_ERROR 3

#define CURRENT_LOG_LEVEL LOG_LEVEL_INFO  // Cambiar para producción

#define LOG_DEBUG(msg) if(CURRENT_LOG_LEVEL <= LOG_LEVEL_DEBUG) Serial.println(msg)
#define LOG_INFO(msg)  if(CURRENT_LOG_LEVEL <= LOG_LEVEL_INFO)  Serial.println(msg)
#define LOG_WARN(msg)  if(CURRENT_LOG_LEVEL <= LOG_LEVEL_WARN)  Serial.println(msg)
#define LOG_ERROR(msg) if(CURRENT_LOG_LEVEL <= LOG_LEVEL_ERROR) Serial.println(msg)
```

---

## 🟢 Hallazgos Menores (Prioridad Baja)

### H11. 🟢 Variables `extern` Duplicadas

**Archivos:** `config.h` y `globals.h`

Ambos archivos declaran `extern String deviceId`, `extern String apiKey`, `extern const char* ssid`, etc. Esto funciona pero es una fuente de confusión. Debería haber **un solo archivo** de declaraciones externas.

**Recomendación:** Eliminar las declaraciones de `config.h` y usar solo `globals.h` como punto central.

---

### H12. 🟢 Constantes Duplicadas entre `config.h` y `globals.h`

```cpp
// config.h
#define QUEUE_PROCESS_INTERVAL 30000
// globals.h  
#define QUEUE_PROCESS_INTERVAL 30000  // duplicado
#define SENSOR_READ_INTERVAL   5000   // solo aquí
```

Hay `#define` en ambos archivos con valores repetidos. Si se cambia uno y no el otro, el comportamiento depende del orden de inclusión.

---

### H13. 🟢 Relé: Inconsistencia HIGH/LOW entre Funciones

```cpp
// indicators.ino — activarRele1()
digitalWrite(relayPin1, estado ? HIGH : LOW);  // HIGH = ON

// webSocketEvent.ino — actualizacion_relay1
digitalWrite(RELAY_PIN_1, relayState ? LOW : HIGH);  // LOW = ON (activo LOW)

// setupSensores.ino
digitalWrite(relayPin1, HIGH); // HIGH = OFF (activo LOW)
```

**Problema:** `activarRele1()` trata HIGH como ON, pero `webSocketEvent` trata LOW como ON. Esto es contradictorio. El relay es activo en LOW (confirmado por `setupSensores`), pero `activarRele1()` tiene la lógica invertida.

**Impacto:** Si alguien llama `activarRele1(true)`, el relé se APAGA en lugar de encenderse.

---

### H14. 🟢 `extern` en Definiciones (globals.cpp)

```cpp
// globals.cpp:142-145
extern String claseActual = "";      // ❌ extern en DEFINICIÓN
extern String horaInicioClase = "";  // ❌ extern en DEFINICIÓN
extern String horaFinClase = "";     // ❌ extern en DEFINICIÓN
extern bool claseEnCurso = false;    // ❌ extern en DEFINICIÓN
```

`extern` se usa en **declaraciones**, no en **definiciones**. Algunos compiladores lo aceptan pero es técnicamente incorrecto y puede causar warnings o errores en compiladores estrictos.

**Fix:** Eliminar `extern` en las definiciones de `globals.cpp`.

---

## 📐 Análisis de Recursos

### Estimación de RAM

| Componente | RAM Estimada |
|------------|-------------|
| WiFiClientSecure (SSL buffer) | ~40 KB |
| WebSocketsClient | ~4 KB |
| StaticJsonDocument<512> | 512 B × N instancias |
| Strings globales (deviceId, aula, jwt...) | ~2 KB |
| SensorStatus + estructuras | ~200 B |
| Stack FreeRTOS task | 10 KB |
| Stack loop (main) | 8 KB (default) |
| Display buffer (128×64) | 1 KB |
| **Total estimado** | **~66 KB** |
| **ESP32 disponible** | **~320 KB** |
| **Margen** | **~254 KB (79%)** |

### Uso de Flash (NVS)

| Namespace | Datos |
|-----------|-------|
| `auth` | JWT token + timestamp expiración |
| `config` | Nombre de aula |
| `offline_q` | Cola de eventos (hasta 50) |

---

## 🎯 Plan de Acción Recomendado

### Fase 1: Crítico (Inmediato)
1. **[H1]** Activar validación SSL — Usar `setCACert()` en lugar de `setInsecure()`
2. **[H2]** Mover credenciales a NVS cifrado — Script de provisión
3. **[H3]** Token JWT como header, no en URL
4. **[H4]** Reemplazar `DynamicJsonDocument` por `StaticJsonDocument`

### Fase 2: Importante (1-2 semanas)
5. **[H5]** Aumentar stack del task a 16KB + monitoreo
6. **[H6]** Añadir mutex para variables compartidas
7. **[H7]** Cachear lecturas de sensores para display
8. **[H13]** Corregir lógica de relés (HIGH/LOW consistente)

### Fase 3: Mejoras (Sprint siguiente)
9. **[H8]** Rediseñar cola offline como buffer circular
10. **[H9]** Reemplazar `delay()` por `vTaskDelay()`
11. **[H10]** Sistema de logging por niveles
12. **[H11-H12]** Eliminar duplicaciones en headers
13. **[H14]** Corregir `extern` en definiciones
14. Añadir **watchdog timer** (WDT) para recovery automático

---

## 🏆 Veredicto

| Aspecto | Estado |
|---------|--------|
| **¿Funciona?** | ✅ Sí, la lógica principal es correcta |
| **¿Es seguro?** | ❌ No, SSL deshabilitado + credenciales expuestas |
| **¿Es robusto?** | 🟡 Parcialmente — buena recuperación de sensores, pero race conditions |
| **¿Es eficiente?** | 🟡 Parcialmente — doble lectura de sensores, logging excesivo |
| **¿Es mantenible?** | ✅ Sí, buena modularización y naming |
| **¿Está listo para producción?** | ❌ No hasta resolver H1, H2, H3, H13 |

**Resumen:** El firmware tiene una arquitectura sólida y buenas prácticas de modularización, pero las vulnerabilidades de seguridad (SSL deshabilitado, credenciales hardcodeadas) y la inconsistencia en la lógica de relés son bloqueadores para producción. La implementación de la cola offline y el sistema de timer por hardware son destacables. Priorizar la seguridad antes del despliegue.
