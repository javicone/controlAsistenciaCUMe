# 🏫 Control de Asistencia y Monitorización de Aulas (IoT)

**Sistema integrado para registro de asistencia, monitorización ambiental y control domótico de espacios educativos.**

![Logo de la aplicación](imagenes/image.png)

**Estado:** ✅ En producción | **Arquitectura:** FastAPI + WebSockets + ESP32 | **Base de datos:** MySQL (Docker)

---

## 📋 Descripción General

Sistema IoT completo para gestionar aulas inteligentes con:

- **📍 Registro de Asistencia**: Lectura de tarjetas NFC PN532 para captura automática de presencia
- **🌡️ Monitorización Ambiental**: Sensores de temperatura (BME280), iluminación (BH1750), presencia (LD2410)
- **🔌 Control Domótico**: Toggle remoto de relés para calefacción, iluminación y sistemas HVAC
- **📡 Comunicación en Tiempo Real**: WebSockets para actualizaciones instantáneas a administradores y personal
- **🔐 Autenticación JWT**: Sistema de tokens para ESP32, administradores y personal de soporte
- **🗂️ Gestión completa**: Dashboard web, análisis de datos, histórico de asistencia

---

## 🏗️ Arquitectura del Sistema

```
┌────────────────────────────────────────────────────────────────┐
│                       CAPAS DEL SISTEMA                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FRONTEND:  Navegador → HTML/CSS (Templates)                   │
│  BACKEND:   FastAPI + Uvicorn (Python 3.10+)                   │
│  WEBSOCKET: Comunicación RT (Aulas ↔ Admin/Conserjes)         │
│  DATABASE:  MySQL 8.0 (Contenedor Docker)                      │
│  DEVICES:   ESP32 + Sensores + Actuadores                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 🔀 Flujo de Datos

```
ESP32 NFC Lee Tarjeta
    ↓
API REST: POST /registro (UID, aula)
    ↓
Backend: Valida JWT, consulta BD
    ↓
Si válida: Registra asistencia ✅
    ↓
WebSocket: Notifica a admins en RT
    ↓
Dashboard actualizado en vivo
```

---

## 📦 Estructura del Proyecto

```
ControlAsistencia/
├── README.md                          # Este fichero
├── keys/
│   ├── cert_https.pem                # Certificado SSL/TLS
│   └── key_https.pem                 # Clave privada HTTPS
│
├── Database/
│   ├── backupControlAsistencia.sql   # Dump completo de la BD
│   └── docker_comando.txt            # Script para levantar MySQL
│
├── DatosAnalisisHorario/             # Scripts de análisis
│   ├── clases.py                     # Importador de horarios
│   ├── resultados/*.csv              # Estadísticas generadas
│   └── estad_*.csv                   # Ocupación por periodo
│
├── Device_ESP32_app/                 # Firmware ESP32 (CORE)
│   ├── Device_ESP32_app.ino          # Programa principal
│   ├── config.h                      # Configuración: WiFi, BD, etc
│   ├── globals.h / globals.cpp       # Variables globales
│   │
│   ├── NFC_module.ino                # Lectura PN532
│   ├── BME_module.ino                # Temperatura/Presión
│   ├── LightMeter_module.ino         # Iluminación BH1750
│   ├── radar_module.ino              # Presencia LD2410
│   ├── indicators.ino                # LEDs y buzzer
│   │
│   ├── setupSensores.ino             # Inicialización del HW
│   ├── webSocketEvent.ino            # Comunicación WebSocket
│   ├── api_rest.ino                  # Endpoints REST
│   ├── auth_device_jwt.ino           # JWT para ESP32
│   ├── cola_envio_offline.ino        # Buffer offline
│   ├── wifi_manager.ino              # Manejo WiFi
│   ├── display_module.ino            # Panel OLED SSD1306
│   ├── funciones_auxiliares.ino      # Utilities
│   └── UNIT_PN532.h / UNIT_PN532.cpp # Libería NFC custom
│
├── Server/                           # Backend Python (CORE)
│   ├── appFastApi.py                 # Punto de entrada
│   ├── requirements.txt              # Dependencias pip
│   ├── config.py                     # Configuración (variables env)
│   ├── database.py                   # Pool conexiones MySQL
│   ├── .env                          # Variables de entorno (gitignored)
│   │
│   ├── routers/                      # Endpoints FastAPI
│   │   ├── auth.py                   # Autenticación (/login, /token)
│   │   ├── asistencias.py            # Registro (/registro, /historial)
│   │   ├── aulas.py                  # Estado aulas (/estado, /control_relay)
│   │   ├── clases.py                 # Horarios (/clases, /proxima)
│   │   ├── views.py                  # Vistas HTML (/dashboard, etc)
│   │   └── websockets.py             # Canales WS (/ws, /ws/admin, /ws/conserje)
│   │
│   ├── services/                     # Lógica de negocio
│   │   ├── auth_service.py           # JWT, login, tokens
│   │   ├── asistencia_service.py     # Registro, historial
│   │   ├── aula_service.py           # Estado, relés
│   │   └── clase_service.py          # Horarios, próxima clase
│   │
│   ├── models/                       # Modelos Pydantic + SQLAlchemy
│   │   ├── user.py
│   │   ├── aula.py
│   │   ├── asistencia.py
│   │   ├── clase.py
│   │   └── webTokens.py
│   │
│   ├── middleware/                   # Middlewares personalizados
│   │   ├── cors.py                   # CORS headers
│   │   └── logging.py                # Logging centralizado
│   │
│   ├── utils/                        # Funciones auxiliares
│   │   ├── database_pool.py          # Gestión pool MySQL
│   │   └── websocket_manager.py      # Manager singleton WS
│   │
│   ├── security/                     # Autenticación y autorización
│   │   └── jwt_utils.py              # Funciones JWT
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/                       # JavaScript del dashboard
│   │
│   ├── templates/                    # Plantillas Jinja2
│   │   ├── index.html                # Login
│   │   ├── dashboard.html            # Panel administrador
│   │   ├── administrador.html        # Gestión completa
│   │   ├── conserjes.html            # Vista personal soporte
│   │   └── gestion_aulas.html        # Control relés
│   │
│   ├── antiguasVersiones/            # Código deprecado (referencia)
│   │   ├── appFlask.py               # Flask monolítico
│   │   └── appFastApi_MONOLITO.py    # Primera versión FastAPI
│   │
│   └── __pycache__/
│
├── DOCS/                             # Documentación técnica
│   ├── RESUMEN_EJECUTIVO.md          # Hardware specs
│   ├── ARQUITECTURA_WEBSOCKET_3_ROLES.md
│   ├── PINES_ESP32_DIAGRAMA.md       # Pinout completo
│   ├── GUIA_CONEXIONADO_FISICO_ESP32.md
│   ├── ENUMERACION_COMPONENTES_ESP32.md
│   ├── FORMATO_MENSAJES_WEBSOCKET.md
│   ├── DIAGNOSTICO_WEBSOCKET.md
│   ├── LOGS_SEGURIDAD_HTTPS.md
│   ├── SISTEMA_JWT_UNIFICADO.md
│   ├── MIGRACION_ARDUINOWEBSOCKETS.md
│   └── AGREGABLES.md
│
├── imagenes/
│   └── image.png
│
└── tests_individuales_Componentes/   # Pruebas aisladas
    ├── PRUEBA_BME280_BH1750/
    ├── PRUEBA_LD2410/
    ├── PRUEBAS_HTTPS/
    ├── PRUEBBA_NFC/
    └── RELE_PRUEBAS/
```

---

## 🔌 Componentes del Dispositivo ESP32

### Sensores (4)
| Sensor | Modelo | Puerto | Función |
|--------|--------|--------|---------|
| **Temperatura/Presión** | BME280 | I2C (0x76) | Monitoreo ambiental |
| **Iluminación** | BH1750 | I2C (0x23) | Nivel de luz |
| **Presencia** | LD2410 | UART2 (RX17/TX16) | Radar de movimiento |
| **NFC/RFID** | PN532 | SPI + IRQ | Lectura tarjetas |

### Actuadores (2)
| Actuador | GPIO | Función | Control |
|----------|------|---------|---------|
| **Relé 1** | 26 | Calefacción/HVAC | Activo LOW |
| **Relé 2** | 32 | Iluminación | Activo LOW |

### Indicadores (4)
| Indicador | GPIO | Función |
|-----------|------|---------|
| **LED Rojo** | 25 | Error/Alerta |
| **LED Verde** | 27 | Operación normal |
| **LED Amarillo** | 14 | Estado WiFi/LD2410 |
| **Buzzer** | 33 | Confirmación NFC (PWM) |
| **OLED Display** | I2C (0x3C) | Información visual |

### Pinout Completo

```
ESP32 (38 pines usables)
┌─────────────────┐
│ 3V3 ▓▓ GND      │  Alimentación
│ EN  ▓▓ D23      │  GPIO23: MOSI (SPI NFC)
│ D36 ▓▓ D22      │  GPIO22: SCL (I2C sensores)
│ D39 ▓▓ TXD0     │  UART0 (debug)
│ D34 ▓▓ RXD0     │
│ D35 ▓▓ D21      │  GPIO21: SDA (I2C sensores)
│ D32 ▓▓ D19      │  GPIO32: Relé 2, GPIO19: MISO (SPI)
│ D33 ▓▓ D18      │  GPIO33: Buzzer, GPIO18: SCK (SPI)
│ D25 ▓▓ D5       │  GPIO25: LED Rojo, GPIO5: CS NFC
│ D26 ▓▓ TXD2     │  GPIO26: Relé 1, GPIO17: RX2 LD2410
│ D27 ▓▓ RXD2     │  GPIO27: LED Verde, GPIO16: TX2 LD2410
│ D14 ▓▓ D13      │  GPIO14: LED Amarillo, GPIO13: IRQ NFC
│      ▓▓ D12     │
│      ▓▓ D4      │
│      ▓▓ D2      │
│      ▓▓ D15     │
└─────────────────┘

I²C Bus: SDA(21) - SCL(22) - GND
Dispositivos: BME280(0x76), BH1750(0x23), OLED(0x3C)

SPI Bus (NFC): MOSI(23) - MISO(19) - SCK(18) - CS(5) - IRQ(13) - GND
Velocidad: 1 MHz

Serial2 (LD2410): RX(16) - TX(17) - GND
Baudrate: 256000 bps
```

---

## ⚡ Requisitos

### Hardware
- **Microcontrolador:** ESP32 (DevKit, WROOM-32, etc)
- **Sensores:** BME280, BH1750, LD2410, PN532
- **Actuadores:** 2 relés 5V (GPIO activo LOW)
- **Display:** OLED SSD1306 (opcional)
- **Alimentación:** Fuente 5V/2A

### Software

#### Backend
- **Python:** 3.10+ (3.11/3.12 recomendadas)
- **FastAPI:** Framework HTTP/WebSocket
- **MySQL:** 8.0+ (se proporciona Dockerfile)
- **Sistema Operativo:** Windows, Linux, macOS

#### Firmware
- **Arduino IDE:** 2.0+
- **PlatformIO:** Recomendado
- **Board:** ESP32 DEV KIT
- **Librerías:** Ver [`Device_ESP32_app/requirements.txt` conceptual]*

> *El firmware de Arduino/PlatformIO usa `#include` directas; las dependencias están documentadas en `DOCS/ENUMERACION_COMPONENTES_ESP32.md`

---

## 🚀 Instalación y Configuración

### 1️⃣ Base de Datos (MySQL + Docker)

```powershell
# Abrir PowerShell en D:\UEX\ControlAsistencia\Database

cd Database

# Crear contenedor MySQL (Windows)
docker run --name control-asistencia-mysql `
  -e MYSQL_ROOT_PASSWORD=1234 `
  -e MYSQL_DATABASE=control-asistencia `
  -v "$PWD`:/docker-entrypoint-initdb.d" `
  -p 3306:3306 `
  -d mysql:latest

# El contenedor ejecutará automáticamente backupControlAsistencia.sql
```

**Alternativa:** Si MySQL ya está localmente instalado:
```bash
mysql -u root -p < backupControlAsistencia.sql
```

### 2️⃣ Backend (FastAPI)

#### Paso A: Crear entorno virtual
```powershell
# Desde la raíz del proyecto
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Verificar Python
python --version  # 3.10+
```

#### Paso B: Instalar dependencias
```powershell
pip install --upgrade pip
pip install -r Server/requirements.txt
```

#### Paso C: Configurar variables de entorno
```powershell
# Crear archivo .env en Server/
cat > Server/.env << 'EOF'
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=1234
DB_NAME=control-asistencia
SECRET_KEY=tu_clave_jwt_super_secreta_minimo_32_caracteres_CAMBIAR_EN_PRODUCCION
TOKEN_EXPIRE_MINUTES=1440
EOF
```

> ⚠️ **NUNCA** subir `.env` a control de versiones. Usar `.gitignore` para excluirlo.

#### Paso D: Ejecutar servidor
```powershell
cd Server
python appFastApi.py

# Debería mostrar:
# ✅ Servidor escuchando en: http://0.0.0.0:8000
# 🔒 SSL/TLS HABILITADO ✅ (si están los certificados en keys/)
```

**Acceso:**
- 🌐 Frontend: http://localhost:8000
- 🔐 HTTPS: https://localhost:8000 (si los certificados existen)
- 📚 Docs: http://localhost:8000/docs (Swagger UI)
- 🧪 ReDoc: http://localhost:8000/redoc (Documentación interactiva)

### 3️⃣ Firmware (ESP32)

#### Requisitos
1. Arduino IDE 2.0+ o PlatformIO
2. Board manager: ESP32 1.0.6+
3. Librerías (instalar vía Arduino IDE Library Manager o PlatformIO):
   - Adafruit PN532
   - Adafruit BME280
   - BH1750 (TinyLux)
   - LD2410 (esphome)
   - Adafruit GFX + SSD1306
   - ArduinoJson
   - WebSocketsClient

#### Pasos
1. **Abrir proyecto:**
   ```
   File → Open → ControlAsistencia/Device_ESP32_app/Device_ESP32_app.ino
   ```

2. **Configurar credenciales** en `config.h`:
   ```cpp
   #define SSID "TuRedWiFi"
   #define PASSWORD "TuContraseña"
   #define SERVER_IP "192.168.X.X"     // IP del backend
   #define SERVER_PORT 8000            // Puerto FastAPI
   #define AULA_ID "Aula A-101"        // Identificador del aula
   ```

3. **Seleccionar placa:**
   ```
   Tools → Board → ESP32 → ESP32 Dev Module
   Tools → COM Port → COMx (el puerto del ESP32)
   ```

4. **Compilar y cargar:**
   ```
   ✔️ → (verificar) o Sketch → Upload
   ```

5. **Monitor Serial:**
   ```
   Tools → Serial Monitor → 115200 baud
   Observar logs de inicialización
   ```

---

## 🔗 API Endpoints

### Autenticación

**POST** `/login`
```json
Request:
{
  "usuario": "admin",
  "contraseña": "123456"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_type": "admin"
}
```

**POST** `/login_aula`
```json
Request:
{
  "aula_id": "Aula A-101",
  "device_password": "device_secret_123"
}

Response (200):
{
  "access_token": "device_jwt_token...",
  "token_type": "bearer"
}
```

### Asistencia

**POST** `/registro`
- **Headers:** `Authorization: Bearer {token}`
- **Body:**
  ```json
  {
    "uid": "04B8C2DA5F3B80",
    "aula": "Aula A-101"
  }
  ```
- **Response:** `{ "status": "registrado", "usuario": "Juan Pérez", "timestamp": "2025-02-11T10:30:00" }`

**GET** `/historial?aula=Aula A-101&fecha=2025-02-11`
- Retorna lista de registros de asistencia del día

### Estado de Aulas

**GET** `/estado_aulas`
```json
Response:
{
  "Aula A-101": {
    "temperatura": 22.5,
    "humedad": 45,
    "luz": 450,
    "personas": 2,
    "clase_en_curso": true,
    "relay_1": false,
    "relay_2": true
  }
}
```

**POST** `/control_relay`
```json
{
  "aula": "Aula A-101",
  "relay": 1,
  "estado": true
}
```

### Horarios

**GET** `/proxima_clase?aula=Aula A-101`
```json
Response:
{
  "clase": "Matemáticas II",
  "profesor": "Dr. García",
  "inicio": "2025-02-11T11:00:00",
  "duracion_minutos": 90,
  "aula": "Aula A-101"
}
```

---

## 📡 WebSocket (Comunicación en Tiempo Real)

### Canales

| Endpoint | Rol | Propósito |
|----------|-----|----------|
| `/ws` | ESP32 Devices | Envía datos sensores, recibe comandos |
| `/ws/admin` | Administrador | Monitoreo completo, control total |
| `/ws/conserje` | Personal soporte | Monitoreo parcial, control limitado |

### Ejemplo: Conexión Device

**Cliente ESP32 → Servidor:**
```json
{
  "tipo": "conexion",
  "aula": "Aula A-101",
  "device_id": "ESP32_001"
}
```

**Device envía datos cada 30 segundos:**
```json
{
  "tipo": "sensor_data",
  "aula": "Aula A-101",
  "temperatura": 22.5,
  "humedad": 45,
  "luz": 450,
  "personas": 2,
  "clase_en_curso": true
}
```

**Servidor envía comandos:**
```json
{
  "tipo": "comando",
  "accion": "toggle_relay",
  "relay": 1,
  "estado": true
}
```

### Ejemplo: Conexión Admin

```javascript
// JavaScript en navegador
const ws = new WebSocket('wss://localhost:8000/ws/admin?token=eyJ...');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log('Aula actualizada:', msg);
  // Actualizar UI en tiempo real
};

ws.send(JSON.stringify({
  tipo: 'comando',
  aula: 'Aula A-101',
  accion: 'toggle_relay',
  relay: 1
}));
```

---

## 🔐 Seguridad

### JWT (JSON Web Tokens)

Sistema unificado de autenticación:

- **Administrador:** `scope="admin"` → Control total
- **Conserje/Personal:** `scope="conserje"` → Control parcial
- **Dispositivo:** `scope="device"` → Envío de datos, recepción comandos

**Expiración:** 1440 minutos (24 horas) - configurable en `.env`

### HTTPS/SSL

Si existen certificados en `Server/keys/`:
```
cert_https.pem  → Certificado público
key_https.pem   → Clave privada
```

El servidor se inicia automáticamente con HTTPS. Para generar certificados autofirmados:

```bash
openssl req -x509 -newkey rsa:4096 -keyout key_https.pem -out cert_https.pem -days 365 -nodes
```

### Buenas Prácticas

✅ **Hacer:**
- Cambiar `SECRET_KEY` en producción
- Usar HTTPS/TLS en conexiones
- Validar tokens JWT en cada request
- Hash de contraseñas (bcrypt/argon2)
- Rate limiting en endpoints sensibles

❌ **Evitar:**
- Subir `.env` o credenciales a Git
- Usar contraseñas por defecto
- Dejar debug enabled en producción
- Exponer stack traces en errores

---

## 🐛 Troubleshooting

### Backend no inicia

**Error:** `No module named 'fastapi'`
```powershell
pip install -r Server/requirements.txt --force-reinstall
```

**Error:** `Can't connect to MySQL server on 'localhost:3306'`
```bash
# Verificar que el contenedor Docker esté corriendo
docker ps

# Si no aparece, iniciar:
docker start control-asistencia-mysql
```

### ESP32 no conecta a WiFi

1. Verificar SSID y contraseña en `config.h`
2. Revisar logs en Serial Monitor (115200 baud)
3. Próbar con AP diferente
4. Resetear ESP32: `EN` button (1-2 segundos)

### WebSocket desconexiones frecuentes

- Aumentar **timeout** en cliente (ESP32 library)
- Revisar latencia de red: `ping servidor`
- Verificar firewall (puerto 8000)
- Logs en `Server/logs/` (si existen)

### NFC no lee tarjetas

1. Validar conexión SPI:
   - MOSI(23), MISO(19), SCK(18), CS(5)
   - GND correcto
2. Verificar distancia (max 10cm)
3. Probar con `tests_individuales_Componentes/PRUEBBA_NFC/`
4. Usar terminal serial para debug

### Sensores reporting "NULL" / "NaN"

| Sensor | Causa | Solución |
|--------|-------|----------|
| **BME280** | I2C no responde | Verificar SDA(21), SCL(22), voltaje 3.3V |
| **BH1750** | Dirección incorrecta (0x23 vs 0x5C) | Revisar pin ADDR en sensor |
| **LD2410** | Baudrate incorrecto | Serial2 debe estar a 256000 |
| **PN532** | CS o IRQ desconectados | Verificar pines 5 y 13 |

---

## 📊 Análisis de Datos

### Scripts de Horarios

```powershell
cd DatosAnalisisHorario
python clases.py

# Genera:
# - clases_*.csv (horarios por carrera)
# - estad_ocupacion_*.csv (estadísticas)
# - pivot_dia_hora.csv (heatmap ocupación)
```

### Exportar Datos de BD

```bash
# Backup completo
mysqldump -u root -p1234 control-asistencia > backup_$(date +%Y%m%d_%H%M%S).sql

# Solo tabla asistencias
mysqldump -u root -p1234 control-asistencia asistencias > asistencias_export.sql
```

---

## 🤝 Contribución

### Estructura de Ramas
```
main                    → Producción estable
├── develop            → Integración features
│   ├── feature/ws-ssl  → Nueva funcionalidad
│   ├── bugfix/nfc      → Correcciones
│   └── hotfix/jwt      → Urgente a main
```

### Checklist antes de Push

- [ ] Código sigue PEP 8 (Python) / Google Style (C++)
- [ ] Variables de entorno en `.env.example` (no secrets)
- [ ] README actualizado
- [ ] Tests lanzados sin error
- [ ] Sin credentials en commits
- [ ] Mensaje de commit descriptivo

### Documentación

Toda nueva funcionalidad debe ir acompañada de docs en `DOCS/`:
- Endpoint API → swagger automático
- WebSocket → `FORMATO_MENSAJES_WEBSOCKET.md`
- Hardware → `PINES_ESP32_DIAGRAMA.md`
- Arquitectura → `ARQUITECTURA_*.md`

---

## 📞 Soporte y Contacto

- **Issues/Bugs:** [Crear issue en repo]
- **Documentación técnica:** Ver carpeta `DOCS/`
- **Preguntas frecuentes:** `DOCS/DIAGNOSTICO_WEBSOCKET.md`
- **Hardware specs:** `DOCS/RESUMEN_EJECUTIVO.md`

---

## 📄 Licencia

Proyecto interno Universidad de Extremadura.
Uso restringido a propósitos educativos.

---

## 🗺️ Roadmap

- [ ] **v2.0** - Dashboard avanzado (React/Vue)
- [ ] **v2.1** - App móvil (Flutter)
- [ ] **v2.2** - Integración con SIS (Sistema académico)
- [ ] **v2.3** - ML: Predicción ocupación aulas
- [ ] **v3.0** - Multi-campus
- [ ] **v3.1** - Módulo de energía (kWh monitoring)

---

**Última actualización:** Febrero 2025 | **Versión:** 1.5.x

