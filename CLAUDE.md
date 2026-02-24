# CLAUDE.md — Guía para Agentes LLM

> Este archivo proporciona a cualquier agente de IA (Claude, Copilot, Cursor, etc.) el contexto necesario para trabajar eficazmente con este proyecto. Léelo completo antes de hacer cambios.

---

## Qué es este proyecto

**Sistema IoT de Control de Asistencia y Monitorización de Aulas** para la Universidad de Extremadura (CUMEx). Registra asistencia por NFC, monitoriza condiciones ambientales y permite control domótico remoto.

**Stack tecnológico:**
- **Backend:** Python 3.10+ / FastAPI / Uvicorn / Jinja2
- **Base de datos:** MySQL 8.0+ (Docker) con driver `aiomysql` (async)
- **Firmware IoT:** Arduino C++ para ESP32 (WROOM-32)
- **Frontend:** HTML + CSS + JS vanilla (templates Jinja2, sin framework SPA)
- **Comunicación:** WebSockets bidireccionales + REST API + HTTPS/SSL
- **Autenticación:** JWT dual — HS256 (web) y RS256 (dispositivos IoT)

---

## Estructura del proyecto

```
ControlAsistencia/
├── Server/                      # ← BACKEND (Python/FastAPI)
│   ├── appFastApi.py            # Punto de entrada, lifespan, routers
│   ├── config.py                # DB_CONFIG, SECRET_KEY, ALGORITHM
│   ├── database.py              # Conexión sincrónica (legacy)
│   ├── requirements.txt         # Dependencias pip
│   ├── .env / .env.example      # Variables de entorno
│   ├── keys/                    # Certificados SSL + claves RSA para JWT
│   ├── routers/                 # Endpoints HTTP y WebSocket
│   │   ├── auth.py              # /auth/login, /auth/device, /logout
│   │   ├── asistencias.py       # /asistencias/registro, /historial
│   │   ├── aulas.py             # /estado_aulas, /control_relay
│   │   ├── clases.py            # /clases/test, /proxima_clase
│   │   ├── usuarios.py          # CRUD usuarios
│   │   ├── gestion_crud.py      # Panel admin CRUD genérico
│   │   ├── views.py             # Vistas HTML (dashboard, admin, etc.)
│   │   └── websockets.py        # /ws, /ws/admin, /ws/conserje
│   ├── services/                # Lógica de negocio
│   │   ├── auth_service.py
│   │   ├── asistencia_service.py
│   │   ├── aula_service.py
│   │   ├── clase_service.py
│   │   └── user_service.py
│   ├── repositories/            # Acceso a datos (SQL parameterizado, sin ORM)
│   │   ├── usuarioRepository.py
│   │   ├── aulaRepository.py
│   │   ├── claseRepository.py
│   │   ├── asistenciaRepository.py
│   │   └── nodos.py             # Gestión de dispositivos ESP32
│   ├── models/                  # Schemas Pydantic (validación)
│   │   ├── user.py              # UserLogin, UserCreate, UserInDB
│   │   ├── aula.py              # DatosAula, ControlRelay, EstadoAula
│   │   ├── asistencia.py        # RegistroAsistencia, AsistenciaResponse
│   │   ├── clase.py             # Clase, ClaseResponse
│   │   └── webTokens.py
│   ├── security/                # Seguridad
│   │   ├── jwt.py               # RS256 JWT (dispositivos IoT)
│   │   ├── password.py          # bcrypt hash/verify
│   │   └── input_sanitization.py # Anti SQL-injection, XSS, etc.
│   ├── middleware/              # Middlewares
│   │   ├── cors.py              # CORS configuration
│   │   ├── rate_limit.py        # slowapi rate limiting
│   │   ├── input_validation.py  # Validación global de inputs
│   │   └── logging.py
│   ├── utils/
│   │   ├── database_pool.py     # Pool async aiomysql (singleton)
│   │   └── websocket_manager.py # ConnectionManager (3 roles)
│   ├── static/                  # Assets web
│   │   ├── css/                 # styles.css, variables.css, por-vista
│   │   └── js/                  # administrador.js, conserjes.js, etc.
│   └── templates/               # Plantillas Jinja2
│       ├── index.html           # Login
│       ├── dashboard.html       # Panel principal
│       ├── administrador.html   # Vista admin
│       ├── conserjes.html       # Vista conserje
│       ├── gestion_datos.html   # CRUD panel
│       ├── asistencias_profesor.html
│       └── error.html           # Página de error genérica
│
├── Device_ESP32_app/            # ← FIRMWARE ESP32 (Arduino C++)
│   ├── Device_ESP32_app.ino     # setup() + loop() + FreeRTOS task
│   ├── config.h                 # Pines, constantes, extern declarations
│   ├── globals.h / globals.cpp  # Variables globales, structs, objetos de sensor
│   ├── NFC_module.ino           # Lector PN532 (SPI)
│   ├── BME_module.ino           # Sensor temp/humedad/presión BME280 (I2C)
│   ├── LightMeter_module.ino    # Sensor luz BH1750 (I2C)
│   ├── radar_module.ino         # Radar presencia LD2410 (UART2)
│   ├── display_module.ino       # Pantalla OLED SSD1306 128x64 (I2C)
│   ├── indicators.ino           # LEDs (rojo/verde/amarillo), buzzer, relés
│   ├── webSocketEvent.ino       # Manejo eventos WS + dispatch mensajes
│   ├── api_rest.ino             # Llamadas HTTP POST/GET al backend
│   ├── auth_device_jwt.ino      # Obtención/renovación JWT (NVS)
│   ├── cola_envio_offline.ino   # Cola offline persistente (NVS, max 50)
│   ├── wifi_manager.ino         # Reconexión WiFi + verificación periódica
│   ├── setupSensores.ino        # Init de todos los sensores
│   └── funciones_auxiliares.ino # Helpers: epoch, URL encode, timers HW
│
├── Device_ESP32_app_v2.0/       # Copia de referencia (idéntico a v1 actualmente)
│
├── Database/
│   ├── backupControlAsistencia.sql  # Dump completo (schema + datos)
│   ├── migracion_clase_id.sql       # Migración pendiente
│   └── migracion_eliminar_password_aula.sql
│
├── DOCS/                        # Documentación técnica (Markdown)
│   ├── INDICE.md                # Índice navegable
│   └── *.md                     # Arquitectura, JWT, WebSocket, hardware...
│
├── DatosAnalisisHorario/        # Scripts Python para análisis de horarios
├── tests_indivudales_Componentes/ # Pruebas aisladas de hardware
└── PROTOTIPO/                   # Prototipos anteriores
```

---

## Esquema de base de datos

```sql
-- 4 tablas principales, MySQL/MariaDB

usuarios (
  id INT PK AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  correo VARCHAR(100) DEFAULT '',
  password VARCHAR(255) DEFAULT '',
  uid_tarjeta VARCHAR(50) NOT NULL UNIQUE,  -- UID de tarjeta NFC
  rol ENUM('profesor','conserje','administrador') NOT NULL
)

aulas (
  id INT PK AUTO_INCREMENT,
  nombre VARCHAR(50) NOT NULL UNIQUE
)

clases (
  id INT PK AUTO_INCREMENT,
  aula_id INT NOT NULL → aulas(id),
  profesor_id INT NOT NULL → usuarios(id),
  asignatura VARCHAR(100) DEFAULT '',
  hora_inicio DATETIME NOT NULL,
  hora_fin DATETIME NOT NULL
)

asistencias (
  id INT PK AUTO_INCREMENT,
  usuario_id INT NOT NULL → usuarios(id),
  aula_id INT NOT NULL → aulas(id),
  fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Relaciones:**
```
usuarios (1) ──< clases (N) >── (1) aulas
usuarios (1) ──< asistencias (N) >── (1) aulas
```

---

## Arquitectura de comunicación

### Flujo principal (asistencia NFC)
```
Tarjeta NFC → ESP32 (PN532 SPI) → HTTPS POST /asistencias/registro
    → Backend valida JWT + UID → INSERT asistencias
    → WebSocket notifica admins/conserjes en tiempo real
```

### WebSocket — 3 canales con roles
| Endpoint | Quién conecta | Autenticación |
|----------|---------------|---------------|
| `/ws?token=JWT` | ESP32 devices | JWT RS256 (Bearer en query) |
| `/ws/admin` | Navegador admin | Cookie `access_token` (HS256) |
| `/ws/conserje` | Navegador conserje | Cookie `access_token` (HS256) |

### Mensajes WebSocket clave

**Device → Server:**
| tipo | Propósito |
|------|-----------|
| `nodo_conectado` | Registro al conectar (device_id, aula, IP, relays) |
| `datos_aula` | Datos sensores periódicos (temp, humedad, luz, presencia) |
| `confirmacion_relay` | ACK tras toggle de relé |
| `test_respuesta` | Respuesta a health check |

**Server → Device:**
| tipo | Propósito |
|------|-----------|
| `actualizacion_relay1/relay2` | Comando toggle relé |
| `resetear_nodo` | Reinicio remoto (ESP.restart) |
| `test_conexion` | Health check |
| `configurar_aula` | Cambiar nombre de aula (persistido en NVS) |

**Admin → Server (vía WS):**
| action | Propósito |
|--------|-----------|
| `toggle_relay` | Control domótico |
| `listar_dispositivos` | Ver nodos conectados |
| `resetear_nodo` | Reinicio remoto |
| `solicitar_estado` | Obtener estado actual |
| `test_conexion` | Ping a dispositivo |

---

## Autenticación JWT dual

| Aspecto | Web (humanos) | Dispositivos (ESP32) |
|---------|--------------|---------------------|
| Algoritmo | HS256 (simétrico) | RS256 (asimétrico) |
| Clave | `SECRET_KEY` en .env | Par PEM en `Server/keys/` |
| Transporte | Cookie HttpOnly `access_token` | Header Bearer / query param |
| Expiración | 24h (configurable) | 365 días |
| Roles | `administrador`, `conserje`, `profesor` | `device` / `admin` scope |
| Endpoint login | `POST /auth/login` | `POST /auth/device` |

---

## Hardware ESP32 — Pines GPIO

| Componente | Protocolo | Pines |
|-----------|-----------|-------|
| BME280 (temp/hum/pres) | I2C 0x76 | SDA=21, SCL=22 |
| BH1750 (luz) | I2C 0x23 | SDA=21, SCL=22 |
| OLED SSD1306 | I2C 0x3C | SDA=21, SCL=22 |
| PN532 (NFC) | SPI | MOSI=23, MISO=19, SCK=18, CS=5, IRQ=34 |
| LD2410 (radar) | UART2 256000bd | RX=16, TX=17 |
| Relé 1 (calefacción) | GPIO activo LOW | 26 |
| Relé 2 (iluminación) | GPIO activo LOW | 32 |
| LED Rojo | GPIO | 25 |
| LED Verde | GPIO | 27 |
| LED Amarillo | GPIO | 14 |
| Buzzer (PWM) | GPIO | 33 |

---

## Cómo levantar el proyecto (desarrollo)

### 1. Base de datos
```powershell
cd Database
docker run --name control-asistencia-mysql `
  -e MYSQL_ROOT_PASSWORD=1234 `
  -e MYSQL_DATABASE=control-asistencia `
  -v "$PWD:/docker-entrypoint-initdb.d" `
  -p 3306:3306 -d mysql:latest
```

### 2. Backend
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Server/requirements.txt
cp Server/.env.example Server/.env   # Editar con valores reales
cd Server
python appFastApi.py
# → http://localhost:8000 (Swagger: /docs)
```

### 3. Firmware
1. Abrir `Device_ESP32_app/Device_ESP32_app.ino` en Arduino IDE 2.0+
2. Editar `config.h`/`globals.cpp`: SSID, password, SERVER_IP
3. Instalar librerías: Adafruit PN532, BME280, BH1750, LD2410, SSD1306, ArduinoJson, WebSocketsClient
4. Board: ESP32 Dev Module → Upload

---

## Variables de entorno (.env)

| Variable | Propósito | Default |
|----------|-----------|---------|
| `DB_HOST` | Host MySQL | localhost |
| `DB_USER` | Usuario MySQL | root |
| `DB_PASSWORD` | Contraseña MySQL | 1234 |
| `DB_NAME` | Nombre BD | control-asistencia |
| `DB_PORT` | Puerto MySQL | 3306 |
| `SECRET_KEY` | Clave firma JWT HS256 | (obligatorio, >32 chars) |
| `ALGORITHM` | Algoritmo JWT | HS256 |
| `TOKEN_EXPIRE_MINUTES` | TTL tokens web | 1440 (24h) |
| `DEVICE_PASSWORD` | Contraseña auth ESP32 | (obligatorio) |
| `SSL_CERT_PATH` / `SSL_KEY_PATH` | Certificados HTTPS | (vacío = HTTP) |
| `LOG_LEVEL` | Nivel logging | INFO |
| `ENVIRONMENT` | development/staging/production | development |

---

## Patrones arquitectónicos clave

1. **Repository Pattern** — SQL crudo parametrizado en `repositories/`, sin ORM. Todas las queries usan `%s` placeholders.
2. **Async everywhere** — `aiomysql` pool (singleton, double-checked locking), handlers async, `aiohttp` para servicios externos.
3. **Action-map dispatch (WS)** — Diccionarios `MAPA_ACCIONES_DISPOSITIVO`, `ACCIONES_ADMIN` mapean `tipo`/`action` → coroutine.
4. **Estado en memoria** — `aulas_estado` (dict) guarda estado en tiempo real de sensores. No se persiste.
5. **ConnectionManager singleton** — Gestiona 3 listas: `devices` (dict por ID), `admins` (list), `conserjes` (list).
6. **Defense in depth** — Pydantic → InputValidationMiddleware → input_sanitization → SQL parametrizado.
7. **Dual-core ESP32** — Core 0: WiFi + WS + cola offline (FreeRTOS task). Core 1: sensores + NFC + loop Arduino.
8. **Cola offline NVS** — El ESP32 almacena hasta 50 eventos en NVS cuando no hay conexión, los reenvía al reconectar.
9. **JWT en NVS** — Token del dispositivo persiste entre reinicios (RAM → NVS → fetch new, con 60s de margen).
10. **Templates SSR** — El frontend es Jinja2 renderizado en servidor, con JS vanilla para interactividad y WebSocket.

---

## Convenciones de código

### Python (Backend)
- **Estilo:** PEP 8, tipado con type hints
- **Async:** Todas las funciones de I/O son `async def`
- **Queries:** SQL crudo con `%s` placeholders (NUNCA f-strings en SQL)
- **Validación:** Pydantic models en `models/`, sanitización en `security/`
- **Passwords:** bcrypt (12 rounds) vía `security/password.py`
- **Imports:** Organizados por stdlib → third-party → locales
- **Logs:** `logging` estándar, nivel configurable

### C++ (Firmware ESP32)
- **Estilo:** Arduino-style (.ino multi-file), Google C++ donde aplica
- **Variables globales:** Declaradas `extern` en `globals.h`, definidas en `globals.cpp`
- **Structs de datos:** `BME280Data`, `LuzData`, `NFCData`, `RadarData`, `SensorStatus`
- **Enum estados:** `EstadoLED { NORMAL, ADVERTENCIA, ERROR, CRITICO }`
- **Manejo errores:** Cada sensor tiene retry en setup + validación de rango en lectura
- **Persistencia:** `Preferences` (NVS) para token JWT, cola offline, nombre de aula
- **Temporización:** `millis()` para intervalos, `timerBegin()` para timer HW de fin de clase

---

## Endpoints REST principales

| Método | Ruta | Propósito | Auth |
|--------|------|-----------|------|
| POST | `/auth/login` | Login web (cookie) | — |
| POST | `/auth/device` | Login ESP32 (JWT) | — |
| GET | `/logout` | Cerrar sesión | Cookie |
| POST | `/asistencias/registro` | Registrar asistencia NFC | JWT Bearer |
| GET | `/estado_aulas` | Estado sensores todas las aulas | Cookie |
| POST | `/control_relay` | Toggle relé | Cookie admin |
| GET | `/clases/test?aula=X` | Clase actual por aula | JWT/Cookie |
| GET | `/proxima_clase?aula=X` | Próxima clase | JWT/Cookie |
| GET | `/health` | Health check + DB status | — |
| GET | `/docs` | Swagger UI | — |

**Vistas HTML (GET, requieren cookie):**
- `/` — Login
- `/dashboard` — Panel principal
- `/administrador` — Vista admin completa
- `/conserjes` — Vista conserje
- `/gestion_datos` — Panel CRUD

---

## Errores comunes y soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `No module named 'fastapi'` | Entorno virtual no activado | `.\.venv\Scripts\Activate.ps1` + `pip install -r Server/requirements.txt` |
| `Can't connect to MySQL` | Docker no levantado | `docker start control-asistencia-mysql` |
| `SECRET_KEY is None` | Falta .env | `cp Server/.env.example Server/.env` |
| ESP32 no conecta WS | IP/puerto incorrectos en config.h | Verificar `SERVER_IP` y `SERVER_PORT` |
| NFC no lee | Cableado SPI incorrecto | Revisar MOSI(23), MISO(19), SCK(18), CS(5) |
| Sensor devuelve NaN | I2C desconectado | Verificar SDA(21), SCL(22), 3.3V, GND |

---

## Para agentes: reglas importantes

1. **No modificar** `.env` directamente — usar `.env.example` como referencia.
2. **SQL siempre parametrizado** — jamás usar f-strings ni concatenación en queries.
3. **Los relés son activo-LOW** — `HIGH` = apagado, `LOW` = encendido.
4. **El frontend NO es SPA** — es SSR con Jinja2. Los JS están en `static/js/` y usan WebSocket nativo del navegador.
5. **Dos sistemas JWT coexisten** — `config.py` (HS256 web) y `security/jwt.py` (RS256 devices). No mezclar.
6. **El pool de BD es async** — usar `await get_db_pool()` + `async with pool.acquire() as conn`.
7. **Firmware multi-archivo** — Arduino IDE compila todos los `.ino` juntos. El orden importa: `globals.cpp` primero, luego módulos.
8. **NVS del ESP32** — se usan namespaces: `"auth"` (JWT), `"offline_q"` (cola), `"config"` (aula).
9. **Antes de editar routers**, revisar el middleware de validación en `middleware/input_validation.py` (puede rechazar inputs).
10. **Rate limiting activo** — login: 5/min, device auth: 10/min, API read: 100/min. Ver `middleware/rate_limit.py`.

---

## Documentación adicional

Para detalles más profundos, consultar `DOCS/`:
- **JWT completo:** `DOCS/ARQUITECTURA_JWT_DUAL.md` y `DOCS/GUIA_RAPIDA_JWT.md`
- **WebSocket detallado:** `DOCS/FORMATO_MENSAJES_WEBSOCKET.md` y `DOCS/ARQUITECTURA_WEBSOCKET_3_ROLES.md`
- **Hardware/Pines:** `DOCS/PINES_ESP32_DIAGRAMA.md` y `DOCS/GUIA_CONEXIONADO_FISICO_ESP32.md`
- **Librerías ESP32:** `DOCS/ENUMERACION_COMPONENTES_ESP32.md`
- **Troubleshooting WS:** `DOCS/DIAGNOSTICO_WEBSOCKET.md`
- **Features pendientes:** `DOCS/AGREGABLES.md`
