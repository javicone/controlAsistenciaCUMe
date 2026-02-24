# Especificación de Requisitos del Software (ERS)
## Sistema IoT de Control de Asistencia y Monitorización de Aulas

**Proyecto:** ControlAsistencia  
**Institución:** Universidad de Extremadura (CUMEx)  
**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Estado:** Implementado

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Descripción General](#2-descripción-general)
3. [Requisitos Funcionales](#3-requisitos-funcionales)
4. [Requisitos No Funcionales](#4-requisitos-no-funcionales)
5. [Requisitos de Datos](#5-requisitos-de-datos)
6. [Requisitos de Interfaces](#6-requisitos-de-interfaces)
7. [Restricciones del Sistema](#7-restricciones-del-sistema)

---

## 1. Introducción

### 1.1 Propósito

Este documento describe los requisitos funcionales y no funcionales del **Sistema IoT de Control de Asistencia y Monitorización de Aulas** actualmente implementado para el Centro Universitario de Mérida (CUMEx) de la Universidad de Extremadura.

### 1.2 Alcance

El sistema permite:
- Registro de asistencia de profesores mediante tarjetas NFC
- Monitorización en tiempo real de condiciones ambientales en aulas
- Control domótico remoto de calefacción e iluminación
- Gestión centralizada desde paneles web diferenciados por rol

### 1.3 Definiciones, Acrónimos y Abreviaturas

| Término | Definición |
|---------|------------|
| **NFC** | Near Field Communication - Comunicación de campo cercano |
| **ESP32** | Microcontrolador Wi-Fi/Bluetooth de Espressif Systems |
| **JWT** | JSON Web Token - Estándar de autenticación stateless |
| **WebSocket** | Protocolo de comunicación bidireccional persistente |
| **UID** | Unique Identifier - Identificador único de tarjeta NFC |
| **Relé** | Dispositivo electromecánico de conmutación para control domótico |
| **IoT** | Internet of Things - Internet de las Cosas |
| **NVS** | Non-Volatile Storage - Almacenamiento persistente del ESP32 |

### 1.4 Usuarios del Sistema

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Profesor** | Docente que ficha asistencia | Registro NFC, ver historial propio |
| **Conserje** | Personal de mantenimiento | Monitorizar aulas, controlar relés |
| **Administrador** | Gestor del sistema | Acceso total: CRUD, configuración, estadísticas |
| **Dispositivo IoT** | Nodo ESP32 en aula | Enviar datos, recibir comandos |

---

## 2. Descripción General

### 2.1 Perspectiva del Producto

El sistema integra hardware IoT con una plataforma web centralizada, proporcionando:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DEL SISTEMA                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    HTTPS/WSS    ┌──────────────────────────┐  │
│  │   ESP32      │◄──────────────► │    Backend FastAPI       │  │
│  │   (por aula) │                 │    (Python 3.10+)        │  │
│  │              │                 │                          │  │
│  │ • NFC PN532  │  WebSocket      │  • REST API              │  │
│  │ • BME280     │  bidireccional  │  • WebSocket 3 canales   │  │
│  │ • BH1750     │                 │  • Jinja2 templates      │  │
│  │ • LD2410     │                 │                          │  │
│  │ • OLED       │                 └─────────┬────────────────┘  │
│  │ • 2 Relés    │                           │                   │
│  └──────────────┘                           │                   │
│                                             ▼                   │
│                                    ┌──────────────────┐         │
│                                    │   MySQL 8.0+     │         │
│                                    │   (Docker)       │         │
│                                    └──────────────────┘         │
│                                             ▲                   │
│  ┌──────────────────────────────────────────┼────────────────┐  │
│  │              PANELES WEB (Navegador)     │                │  │
│  │                                          │                │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │  │
│  │  │ Administra- │  │  Conserje   │  │  Profesor   │        │  │
│  │  │    dor      │  │             │  │             │        │  │
│  │  │  • CRUD     │  │  • Monitor  │  │  • Historial│        │  │
│  │  │  • Config   │  │  • Relés    │  │    propio   │        │  │
│  │  │  • Stats    │  │             │  │             │        │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Funciones Principales

1. **Registro de Asistencia NFC** - Fichaje automático al acercar tarjeta
2. **Monitorización Ambiental** - Temperatura, humedad, luz, presión, presencia
3. **Control Domótico** - Activar/desactivar calefacción e iluminación
4. **Gestión de Datos** - CRUD de usuarios, aulas, clases, asistencias
5. **Comunicación Tiempo Real** - WebSockets bidireccionales

### 2.3 Características de los Usuarios

| Característica | Descripción |
|----------------|-------------|
| Nivel técnico | Usuarios finales sin conocimientos técnicos avanzados |
| Acceso | Autenticación por credenciales web o tarjeta NFC |
| Frecuencia de uso | Diaria para profesores; bajo demanda para conserjes/admins |

---

## 3. Requisitos Funcionales

### 3.1 Módulo de Autenticación

#### RF-AUTH-001: Login Web
| Atributo | Valor |
|----------|-------|
| **ID** | RF-AUTH-001 |
| **Nombre** | Autenticación de usuarios web |
| **Descripción** | El sistema debe permitir login mediante correo y contraseña |
| **Entrada** | `correo`, `password` (formulario POST) |
| **Salida** | Cookie HttpOnly `access_token` (JWT HS256, 24h TTL) |
| **Proceso** | Validar credenciales → Generar JWT → Redirigir según rol |
| **Roles** | Profesor, Conserje, Administrador |
| **Estado** | ✅ Implementado |

#### RF-AUTH-002: Autenticación de Dispositivos
| Atributo | Valor |
|----------|-------|
| **ID** | RF-AUTH-002 |
| **Nombre** | Autenticación de nodos ESP32 |
| **Descripción** | Los dispositivos IoT deben autenticarse para obtener token |
| **Entrada** | `device_id`, `api_key` (JSON POST) |
| **Salida** | JWT Bearer token (365 días TTL) |
| **Endpoint** | `POST /auth/device` |
| **Rate Limit** | 10 intentos/minuto por IP |
| **Estado** | ✅ Implementado |

#### RF-AUTH-003: Cierre de Sesión
| Atributo | Valor |
|----------|-------|
| **ID** | RF-AUTH-003 |
| **Nombre** | Logout de usuarios web |
| **Descripción** | Eliminar cookie de sesión y redirigir a login |
| **Endpoint** | `GET /logout` |
| **Estado** | ✅ Implementado |

---

### 3.2 Módulo de Asistencias

#### RF-ASIS-001: Registro de Fichaje NFC
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ASIS-001 |
| **Nombre** | Registro de asistencia por tarjeta NFC |
| **Descripción** | Registrar entrada de profesor al acercar tarjeta al lector |
| **Entrada** | `uid` (UID tarjeta, hex), `device_id`, `timestamp` (opcional) |
| **Proceso** | 1. Validar UID en BD → 2. Obtener aula desde device_id → 3. Buscar clase actual (BD o webservice) → 4. Validar profesor coincide con clase → 5. Insertar asistencia |
| **Validaciones** | UID hex 8-20 chars; device_id alfanumérico 3-50 chars |
| **Salida** | `{mensaje, usuario_id, aula_id, clase_id, asignatura, fecha_hora}` |
| **Endpoint** | `POST /asistencias/registro` |
| **Estado** | ✅ Implementado |

#### RF-ASIS-002: Consulta de Historial Personal
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ASIS-002 |
| **Nombre** | Historial de asistencias del profesor |
| **Descripción** | Obtener todas las asistencias del usuario autenticado con estadísticas |
| **Autenticación** | Cookie JWT requerida |
| **Salida** | `{nombre, estadisticas: {...}, asistencias: [...]}` |
| **Endpoint** | `GET /asistencias/mis-asistencias` |
| **Estado** | ✅ Implementado |

---

### 3.3 Módulo de Aulas y Monitorización

#### RF-AULA-001: Recepción de Datos Ambientales
| Atributo | Valor |
|----------|-------|
| **ID** | RF-AULA-001 |
| **Nombre** | Actualización de estado de aula |
| **Descripción** | Recibir y almacenar datos telemetría de sensores |
| **Datos** | temperatura (°C), humedad (%), luz (lux), presion (hPa), personas (int), relay1, relay2 |
| **Transporte** | WebSocket mensaje tipo `datos_aula` |
| **Almacenamiento** | En memoria (`aulas_estado` dict) - no persistido |
| **Broadcast** | Notificar a admins (completo) y conserjes (filtrado) |
| **Estado** | ✅ Implementado |

#### RF-AULA-002: Control de Relés
| Atributo | Valor |
|----------|-------|
| **ID** | RF-AULA-002 |
| **Nombre** | Comando de actuación de relés |
| **Descripción** | Enviar orden on/off a calefacción (relay1) o iluminación (relay2) |
| **Entrada** | `{action: 'toggle_relay', aula, relay_num, relay_state}` |
| **Proceso** | Staff envía comando → Server resuelve device_id → Reenvía a ESP32 → ESP32 confirma → Server notifica a todos |
| **Roles** | Conserje, Administrador |
| **Estado** | ✅ Implementado |

#### RF-AULA-003: Vinculación de Dispositivo
| Atributo | Valor |
|----------|-------|
| **ID** | RF-AULA-003 |
| **Nombre** | Registro de nodo ESP32 al conectar |
| **Descripción** | Al conectar WS, el ESP32 envía mensaje `nodo_conectado` con datos de identificación |
| **Datos** | `{tipo: 'nodo_conectado', aula, device_id, ip, uptime, relay1, relay2}` |
| **Validación** | Verificar nombre de aula no en uso por otro dispositivo |
| **Estado** | ✅ Implementado |

---

### 3.4 Módulo de Clases

#### RF-CLAS-001: Obtener Clase Actual
| Atributo | Valor |
|----------|-------|
| **ID** | RF-CLAS-001 |
| **Nombre** | Consulta de clase en curso |
| **Descripción** | Obtener información de la clase actual de un aula |
| **Fuentes** | 1. BD local, 2. Webservice externo (fallback) |
| **Endpoint** | `GET /clases/actual?aula={nombre}` |
| **Salida** | `{asignatura, profesor, hora_inicio, hora_fin}` o `{"mensaje": "No hay clase"}` |
| **Estado** | ✅ Implementado |

#### RF-CLAS-002: Guardar Clase desde Webservice
| Atributo | Valor |
|----------|-------|
| **ID** | RF-CLAS-002 |
| **Nombre** | Persistir clase obtenida de webservice |
| **Descripción** | Al obtener clase desde webservice externo, guardarla en BD para estadísticas futuras |
| **Automatización** | Se ejecuta durante RF-ASIS-001 si clase no existe en BD |
| **Estado** | ✅ Implementado |

---

### 3.5 Módulo de Gestión (CRUD)

#### RF-CRUD-001: Gestión de Usuarios
| Atributo | Valor |
|----------|-------|
| **ID** | RF-CRUD-001 |
| **Nombre** | CRUD de usuarios |
| **Operaciones** | Listar, Crear, Actualizar, Eliminar |
| **Campos** | nombre, correo, password, uid_tarjeta, rol |
| **Restricciones** | `uid_tarjeta` único; rol debe ser enum válido |
| **Autenticación** | Solo administrador |
| **Estado** | ✅ Implementado |

#### RF-CRUD-002: Gestión de Aulas
| Atributo | Valor |
|----------|-------|
| **ID** | RF-CRUD-002 |
| **Nombre** | CRUD de aulas |
| **Operaciones** | Listar, Crear, Actualizar, Eliminar |
| **Campos** | nombre (único, 3-50 chars) |
| **Restricciones** | No eliminar si tiene clases o asistencias asociadas |
| **Endpoints** | `/api/v1/aulas-crud`, `/api/v1/aulas-crud/{id}` |
| **Estado** | ✅ Implementado |

#### RF-CRUD-003: Gestión de Clases
| Atributo | Valor |
|----------|-------|
| **ID** | RF-CRUD-003 |
| **Nombre** | CRUD de clases |
| **Operaciones** | Listar, Crear, Actualizar, Eliminar |
| **Campos** | asignatura, aula_id, profesor_id, hora_inicio, hora_fin |
| **Validación** | `hora_fin` > `hora_inicio` |
| **Estado** | ✅ Implementado |

#### RF-CRUD-004: Gestión de Asistencias
| Atributo | Valor |
|----------|-------|
| **ID** | RF-CRUD-004 |
| **Nombre** | CRUD de asistencias |
| **Operaciones** | Listar, Crear, Actualizar, Eliminar (admin) |
| **Campos** | usuario_id, aula_id, fecha_hora |
| **Estado** | ✅ Implementado |

---

### 3.6 Módulo de Comunicación en Tiempo Real

#### RF-WS-001: Canal de Dispositivos IoT
| Atributo | Valor |
|----------|-------|
| **ID** | RF-WS-001 |
| **Nombre** | WebSocket para ESP32 |
| **Endpoint** | `/ws?token={JWT}` |
| **Autenticación** | JWT Bearer (RS256 o HS256) |
| **Mensajes entrantes** | `nodo_conectado`, `datos_aula`, `confirmacion_relay`, `test_respuesta`, `ping` |
| **Mensajes salientes** | `actualizacion_relay1/2`, `resetear_nodo`, `test_conexion`, `configurar_aula`, `pong` |
| **Estado** | ✅ Implementado |

#### RF-WS-002: Canal de Administradores
| Atributo | Valor |
|----------|-------|
| **ID** | RF-WS-002 |
| **Nombre** | WebSocket para panel admin |
| **Endpoint** | `/ws/admin` |
| **Autenticación** | Cookie JWT (rol: administrador) |
| **Acciones** | `toggle_relay`, `listar_dispositivos`, `actualizar_config`, `resetear_nodo`, `solicitar_estado`, `test_conexion` |
| **Notificaciones** | Estado completo de aulas (incluye IP, RSSI, uptime) |
| **Estado** | ✅ Implementado |

#### RF-WS-003: Canal de Conserjes
| Atributo | Valor |
|----------|-------|
| **ID** | RF-WS-003 |
| **Nombre** | WebSocket para panel conserje |
| **Endpoint** | `/ws/conserje` |
| **Autenticación** | Cookie JWT (rol: conserje) |
| **Acciones** | `toggle_relay`, `listar_dispositivos` |
| **Notificaciones** | Estado de aulas filtrado (sin IP/RSSI/uptime) |
| **Estado** | ✅ Implementado |

---

### 3.7 Módulo de Vistas Web

#### RF-VIEW-001: Página de Login
| Atributo | Valor |
|----------|-------|
| **ID** | RF-VIEW-001 |
| **Ruta** | `/` |
| **Descripción** | Formulario de autenticación |
| **Template** | `index.html` |
| **Estado** | ✅ Implementado |

#### RF-VIEW-002: Panel de Administrador
| Atributo | Valor |
|----------|-------|
| **ID** | RF-VIEW-002 |
| **Ruta** | `/adminPanel` |
| **Descripción** | Vista completa de monitorización y control |
| **Funciones** | Ver todas las aulas, controlar relés, configurar dispositivos, resetear nodos |
| **Requisito** | Rol: administrador |
| **Estado** | ✅ Implementado |

#### RF-VIEW-003: Panel de Conserje
| Atributo | Valor |
|----------|-------|
| **ID** | RF-VIEW-003 |
| **Ruta** | `/conserje` |
| **Descripción** | Panel simplificado de control domótico |
| **Funciones** | Ver aulas, controlar relés (calefacción/iluminación) |
| **Requisito** | Rol: conserje |
| **Estado** | ✅ Implementado |

#### RF-VIEW-004: Historial del Profesor
| Atributo | Valor |
|----------|-------|
| **ID** | RF-VIEW-004 |
| **Ruta** | `/profesor/asistencias` |
| **Descripción** | Historial personal de fichajes con estadísticas |
| **Funciones** | Ver asistencias propias, estadísticas mensuales |
| **Requisito** | Rol: profesor |
| **Estado** | ✅ Implementado |

#### RF-VIEW-005: Gestión de Datos
| Atributo | Valor |
|----------|-------|
| **ID** | RF-VIEW-005 |
| **Ruta** | `/gestion-datos` |
| **Descripción** | Panel CRUD para gestión de BD |
| **Funciones** | CRUD de usuarios, aulas, clases, asistencias |
| **Requisito** | Rol: administrador |
| **Estado** | ✅ Implementado |

---

### 3.8 Módulo del Firmware ESP32

#### RF-ESP-001: Lectura NFC
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ESP-001 |
| **Nombre** | Lectura de tarjetas NFC |
| **Hardware** | PN532 (SPI) |
| **Descripción** | Detectar y leer UID de tarjetas MIFARE |
| **Salida** | UID como string hexadecimal |
| **Feedback** | LED verde + buzzer (éxito); LED rojo (error) |
| **Estado** | ✅ Implementado |

#### RF-ESP-002: Sensores Ambientales
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ESP-002 |
| **Nombre** | Lectura de sensores ambientales |
| **Hardware** | BME280 (I2C), BH1750 (I2C), LD2410 (UART) |
| **Datos** | Temperatura (°C), Humedad (%), Presión (hPa), Luz (lux), Presencia (personas) |
| **Intervalo** | Envío periódico al backend vía WebSocket |
| **Estado** | ✅ Implementado |

#### RF-ESP-003: Control de Relés
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ESP-003 |
| **Nombre** | Actuación de relés |
| **Hardware** | 2 relés (GPIO 26, 32) - Activos en LOW |
| **Función** | relay1 = Calefacción; relay2 = Iluminación |
| **Activación** | Comando WebSocket `actualizacion_relay1/2` |
| **Confirmación** | Respuesta `confirmacion_relay` al servidor |
| **Estado** | ✅ Implementado |

#### RF-ESP-004: Display OLED
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ESP-004 |
| **Nombre** | Pantalla de información |
| **Hardware** | SSD1306 128x64 (I2C) |
| **Funciones** | Mostrar estado, mensaje de fichaje, errores |
| **Estado** | ✅ Implementado |

#### RF-ESP-005: Cola Offline
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ESP-005 |
| **Nombre** | Almacenamiento offline de fichajes |
| **Descripción** | Guardar fichajes en NVS cuando no hay conexión |
| **Capacidad** | Máximo 50 eventos |
| **Reenvío** | Automático al reconectar |
| **Estado** | ✅ Implementado |

#### RF-ESP-006: Indicadores LED
| Atributo | Valor |
|----------|-------|
| **ID** | RF-ESP-006 |
| **Nombre** | LEDs de estado |
| **Hardware** | LED Rojo (25), Verde (27), Amarillo (14), Buzzer (33) |
| **Significados** | Verde=OK/Fichaje exitoso; Amarillo=Procesando; Rojo=Error |
| **Estado** | ✅ Implementado |

---

## 4. Requisitos No Funcionales

### 4.1 Seguridad

#### RNF-SEG-001: Autenticación JWT Dual
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-001 |
| **Descripción** | Sistema dual de tokens JWT |
| **Web (humanos)** | HS256 con clave simétrica, cookie HttpOnly, 24h TTL |
| **Dispositivos** | RS256 con par de claves RSA, Bearer token, 365d TTL |
| **Estado** | ✅ Implementado |

#### RNF-SEG-002: Protección de Contraseñas
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-002 |
| **Descripción** | Hash de contraseñas con bcrypt |
| **Rounds** | 12 |
| **Estado** | ✅ Implementado |

#### RNF-SEG-003: Rate Limiting
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-003 |
| **Descripción** | Limitación de peticiones por IP |
| **Login web** | 5 intentos/minuto |
| **Device auth** | 10 intentos/minuto |
| **API read** | 100 peticiones/minuto |
| **Estado** | ✅ Implementado |

#### RNF-SEG-004: Sanitización de Inputs
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-004 |
| **Descripción** | Validación y sanitización de todas las entradas |
| **Capas** | Pydantic → Middleware → SQL parametrizado |
| **Protección** | SQL Injection, XSS, Path Traversal |
| **Estado** | ✅ Implementado |

#### RNF-SEG-005: HTTPS/SSL
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-005 |
| **Descripción** | Comunicación cifrada |
| **Backend** | Certificado SSL configurable |
| **ESP32** | WiFiClientSecure para HTTPS/WSS |
| **Estado** | ✅ Implementado |

### 4.2 Rendimiento

#### RNF-REND-001: Conexiones Concurrentes
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-REND-001 |
| **Descripción** | Pool de conexiones async a BD |
| **Implementación** | aiomysql con singleton pattern |
| **Escalabilidad** | Configurable vía pool size |
| **Estado** | ✅ Implementado |

#### RNF-REND-002: Tiempo Real
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-REND-002 |
| **Descripción** | Latencia de notificaciones WebSocket |
| **Objetivo** | < 1 segundo en condiciones normales |
| **Estado** | ✅ Implementado |

### 4.3 Disponibilidad

#### RNF-DISP-001: Reconexión Automática
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-DISP-001 |
| **Descripción** | ESP32 reconecta automáticamente |
| **WiFi** | Reconexión automática con backoff |
| **WebSocket** | Reconexión cada 5 segundos |
| **Estado** | ✅ Implementado |

#### RNF-DISP-002: Operación Offline
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-DISP-002 |
| **Descripción** | Fichajes funcionan sin conexión |
| **Mecanismo** | Cola en NVS (hasta 50 eventos) |
| **Sincronización** | Automática al restaurar conexión |
| **Estado** | ✅ Implementado |

### 4.4 Usabilidad

#### RNF-USA-001: Interfaz Responsive
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-USA-001 |
| **Descripción** | Paneles web adaptables |
| **Breakpoints** | 1024px, 768px, 480px |
| **Estado** | ✅ Implementado |

#### RNF-USA-002: Feedback Visual ESP32
| Atributo | Valor |
|----------|-------|
| **ID** | RNF-USA-002 |
| **Descripción** | Indicación clara de estado al usuario |
| **LEDs** | Verde (OK), Amarillo (procesando), Rojo (error) |
| **Buzzer** | Tono de confirmación tras fichaje |
| **Display** | Mensaje de éxito/error |
| **Estado** | ✅ Implementado |

---

## 5. Requisitos de Datos

### 5.1 Modelo de Datos

```sql
-- Esquema implementado (MySQL/MariaDB)

usuarios (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  correo VARCHAR(100) DEFAULT '',
  password VARCHAR(255) DEFAULT '',      -- bcrypt hash
  uid_tarjeta VARCHAR(50) NOT NULL UNIQUE,
  rol ENUM('profesor','conserje','administrador') NOT NULL
)

aulas (
  id INT PRIMARY KEY AUTO_INCREMENT,
  nombre VARCHAR(50) NOT NULL UNIQUE
)

clases (
  id INT PRIMARY KEY AUTO_INCREMENT,
  aula_id INT NOT NULL REFERENCES aulas(id),
  profesor_id INT NOT NULL REFERENCES usuarios(id),
  asignatura VARCHAR(100) DEFAULT '',
  hora_inicio DATETIME NOT NULL,
  hora_fin DATETIME NOT NULL,
  CHECK (hora_fin > hora_inicio)
)

asistencias (
  id INT PRIMARY KEY AUTO_INCREMENT,
  usuario_id INT NOT NULL REFERENCES usuarios(id),
  aula_id INT NOT NULL REFERENCES aulas(id),
  fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 5.2 Datos en Memoria (No Persistidos)

| Estructura | Propósito |
|------------|-----------|
| `aulas_estado` | Estado actual de sensores y relés por device_id |
| `ConnectionManager.devices` | WebSockets activos de dispositivos |
| `ConnectionManager.admins` | WebSockets activos de administradores |
| `ConnectionManager.conserjes` | WebSockets activos de conserjes |

### 5.3 Almacenamiento NVS (ESP32)

| Namespace | Clave | Propósito |
|-----------|-------|-----------|
| `auth` | `jwt_token` | Token JWT del dispositivo |
| `config` | `aula` | Nombre de aula asignado |
| `offline_q` | `count`, `event_{n}` | Cola de fichajes offline |

---

## 6. Requisitos de Interfaces

### 6.1 API REST

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/auth/login` | POST | Login web | - |
| `/auth/device` | POST | Auth dispositivo | - |
| `/logout` | GET | Cerrar sesión | Cookie |
| `/asistencias/registro` | POST | Fichaje NFC | JWT Bearer |
| `/asistencias/mis-asistencias` | GET | Historial propio | Cookie |
| `/aulas/datos` | POST | Recibir telemetría | - |
| `/aulas/estado` | GET | Estado de aulas | Cookie |
| `/aulas/relay` | POST | Control relé | Cookie |
| `/clases/actual` | GET | Clase en curso | Cookie/JWT |
| `/api/v1/aulas-crud` | CRUD | Gestión aulas | Admin |
| `/api/v1/clases` | CRUD | Gestión clases | Admin |
| `/api/v1/asistencias` | CRUD | Gestión asistencias | Admin |

### 6.2 WebSocket Messages

**Dispositivo → Servidor:**

```json
{"tipo": "nodo_conectado", "aula": "Aula 101", "ip": "192.168.1.50", "relay1": false, "relay2": true}
{"tipo": "datos_aula", "aula": "Aula 101", "temperatura": 22.5, "humedad": 45, "luz": 350, "presion": 1013, "personas": 12}
{"tipo": "confirmacion_relay", "aula": "Aula 101", "relay_num": 1, "relay_state": true}
{"tipo": "test_respuesta", "aula": "Aula 101", "relay1": false, "relay2": true}
```

**Servidor → Dispositivo:**

```json
{"tipo": "actualizacion_relay1", "relay": true}
{"tipo": "actualizacion_relay2", "relay": false}
{"tipo": "resetear_nodo"}
{"tipo": "test_conexion"}
{"tipo": "configurar_aula", "data": {"nombre": "Aula 102"}}
```

**Admin/Conserje → Servidor:**

```json
{"action": "toggle_relay", "aula": "Aula 101", "relay_num": 1, "relay_state": true}
{"action": "listar_dispositivos"}
{"action": "resetear_nodo", "device_id": "esp32_001"}
{"action": "test_conexion", "device_id": "esp32_001"}
```

### 6.3 Interfaces Hardware (ESP32)

| Componente | Protocolo | Pines/Dirección |
|------------|-----------|-----------------|
| BME280 | I2C | 0x76, SDA=21, SCL=22 |
| BH1750 | I2C | 0x23, SDA=21, SCL=22 |
| SSD1306 | I2C | 0x3C, SDA=21, SCL=22 |
| PN532 | SPI | MOSI=23, MISO=19, SCK=18, CS=5, IRQ=34 |
| LD2410 | UART2 | RX=16, TX=17, 256000 baud |
| Relé 1 | GPIO | 26 (activo LOW) |
| Relé 2 | GPIO | 32 (activo LOW) |
| LED Rojo | GPIO | 25 |
| LED Verde | GPIO | 27 |
| LED Amarillo | GPIO | 14 |
| Buzzer | GPIO/PWM | 33 |

---

## 7. Restricciones del Sistema

### 7.1 Restricciones Técnicas

| Restricción | Descripción |
|-------------|-------------|
| **Python 3.10+** | Requerido para match/case y typing moderno |
| **MySQL 8.0+** | Funciones JSON, CTEs, Window functions |
| **ESP32 WROOM-32** | Dual-core, WiFi integrado, suficiente memoria |
| **Arduino IDE 2.0+** | Para compilación del firmware |
| **Docker** | Recomendado para base de datos en desarrollo |

### 7.2 Restricciones de Seguridad

| Restricción | Descripción |
|-------------|-------------|
| **SQL Parametrizado** | Nunca usar f-strings en queries SQL |
| **Relés Activo-LOW** | HIGH = apagado, LOW = encendido |
| **Certificados SSL** | Almacenados en `/Server/keys/` |
| **Variables de Entorno** | Credenciales en `.env`, nunca en código |

### 7.3 Restricciones de Negocio

| Restricción | Descripción |
|-------------|-------------|
| **UID Tarjeta Único** | Cada tarjeta NFC pertenece a un solo usuario |
| **Profesor ↔ Clase** | Un profesor solo puede fichar en sus propias clases |
| **Un dispositivo por aula** | Nombre de aula único por ESP32 conectado |

---

## Apéndice A: Variables de Entorno

```env
# Configuración de Base de Datos
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=****
DB_NAME=control-asistencia
DB_PORT=3306

# Seguridad JWT
SECRET_KEY=<clave-32+chars>
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=1440

# Autenticación Dispositivos
DEVICE_PASSWORD=****

# SSL (opcional)
SSL_CERT_PATH=
SSL_KEY_PATH=

# Entorno
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## Apéndice B: Librerías ESP32

| Librería | Versión | Propósito |
|----------|---------|-----------|
| Adafruit_PN532 | 1.3+ | Lector NFC |
| Adafruit_BME280 | 2.2+ | Sensor ambiental |
| BH1750 | 1.3+ | Sensor de luz |
| ld2410 | 0.1+ | Radar de presencia |
| Adafruit_SSD1306 | 2.5+ | Display OLED |
| ArduinoJson | 6.21+ | Parsing JSON |
| WebSocketsClient | 2.4+ | Cliente WebSocket |
| Preferences | (integrada) | Almacenamiento NVS |

---

## Historial de Cambios

| Versión | Fecha | Descripción |
|---------|-------|-------------|
| 1.0 | Feb 2026 | Documento inicial basado en implementación actual |

---

*Documento generado automáticamente a partir del análisis del código fuente del sistema ControlAsistencia.*
