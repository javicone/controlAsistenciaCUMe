# 📚 Índice de Documentación

Navegación rápida por toda la documentación técnica del sistema.

---

## 🚀 Empezar Rápido

**NUEVO EN EL PROYECTO?** Seguir en este orden:

1. **[README.md](../README.md)** - Descripción general, estructura, requisitos
2. **[SETUP_WINDOWS.md](../SETUP_WINDOWS.md)** - Instalación paso a paso (Windows)
3. **[RESUMEN_EJECUTIVO.md](#resumen_ejecutivo)** - Hardware y especificaciones

---

## 📑 Documentos por Tema

### 🛠️ **Hardware y Componentes**

| Documento | Contenido | Público |
|-----------|----------|---------|
| [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) | Tabla componentes, pines GPIO, voltajes, direcciones I2C | ✅ |
| [PINES_ESP32_DIAGRAMA.md](PINES_ESP32_DIAGRAMA.md) | Pinout completo, esquemas de conexión, conexionado físico | ✅ |
| [GUIA_CONEXIONADO_FISICO_ESP32.md](GUIA_CONEXIONADO_FISICO_ESP32.md) | Instrucciones paso a paso para cablear sensores y actuadores | ✅ |
| [ENUMERACION_COMPONENTES_ESP32.md](ENUMERACION_COMPONENTES_ESP32.md) | Lista detallada de librerías, versiones, compatibility matrix | ✅ |

**Ir aquí si:** 
- Necesitas cablear componentes
- Quieres revisar especificaciones de sensores
- Tienes problemas con I2C, SPI o UART

---

### 🌐 **Backend, API, WebSocket**

| Documento | Contenido | Público |
|-----------|----------|---------|
| [ARQUITECTURA_WEBSOCKET_3_ROLES.md](ARQUITECTURA_WEBSOCKET_3_ROLES.md) | Sistema 3 roles (Admin, Conserje, Device), permisos, matriz de acceso | ✅ |
| [FORMATO_MENSAJES_WEBSOCKET.md](FORMATO_MENSAJES_WEBSOCKET.md) | JSON payloads para todos los mensajes WS, ejemplos | ✅ |
| [DIAGNOSTICO_WEBSOCKET.md](DIAGNOSTICO_WEBSOCKET.md) | Troubleshooting, debug, logs, herramientas diagnóstico | ✅ |

**Ir aquí si:**
- Quieres entender cómo comunica el ESP32 con el backend
- Necesitas agregar nuevos tipos de mensajes WS
- Tienes desconexiones o latencia
- Quieres revisar matriz de permisos

---

### 🔐 **Seguridad y Autenticación**

| Documento | Contenido | Público |
|-----------|----------|---------|
| [GUIA_RAPIDA_JWT.md](GUIA_RAPIDA_JWT.md) | ⚡ **INICIO RÁPIDO** - Resumen de 1 página del sistema JWT | ✅ |
| [ARQUITECTURA_JWT_DUAL.md](ARQUITECTURA_JWT_DUAL.md) | HS256 vs RS256, modelo de amenazas, decisiones de diseño (completo) | ✅ |
| [SISTEMA_JWT_UNIFICADO.md](SISTEMA_JWT_UNIFICADO.md) | JWT, scopes, flujo login, renovación tokens, almacenamiento seguro | ✅ |
| [LOGS_SEGURIDAD_HTTPS.md](LOGS_SEGURIDAD_HTTPS.md) | SSL/TLS, certificados, HTTPS setup, auditoría de conexiones | ✅ |

**Ir aquí si:**
- **¿Primera vez?** → Empieza con GUIA_RAPIDA_JWT.md
- Necesitas entender **por qué usamos dos algoritmos JWT diferentes**
- Quieres saber la diferencia entre JWT para web vs dispositivos IoT
- Necesitas entender JWT y cómo loguearse
- Quieres configurar HTTPS
- Necesitas revisar logs de seguridad
- Implementas autenticación en nuevo módulo

---

### 📦 **Frameworks y Migraciones**

| Documento | Contenido | Público |
|-----------|----------|---------|
| [MIGRACION_ARDUINOWEBSOCKETS.md](MIGRACION_ARDUINOWEBSOCKETS.md) | Migración de websockets antiguos, cambios API, problemas conocidos | ✅ |
| [AGREGABLES.md](AGREGABLES.md) | Features que pueden agregarse, roadmap técnico, extensiones propuestas | ✅ |

**Ir aquí si:**
- Trabajas con versiones antiguas del código
- Quieres ver qué más podría agregarse
- Tienes compatibilidad con bibliotecas antiguas

---

## 🎯 Guías por Rol

### 👨‍💻 **Desarrollador Backend (Python/FastAPI)**

1. [README.md](../README.md) - Repositorio
2. [ARQUITECTURA_WEBSOCKET_3_ROLES.md](ARQUITECTURA_WEBSOCKET_3_ROLES.md) - Diseño
3. [FORMATO_MENSAJES_WEBSOCKET.md](FORMATO_MENSAJES_WEBSOCKET.md) - API WS
4. [ARQUITECTURA_JWT_DUAL.md](ARQUITECTURA_JWT_DUAL.md) - **JWT HS256 vs RS256**
5. [SISTEMA_JWT_UNIFICADO.md](SISTEMA_JWT_UNIFICADO.md) - Auth
6. [DIAGNOSTICO_WEBSOCKET.md](DIAGNOSTICO_WEBSOCKET.md) - Debug

**Carpetas clave:**
- `Server/routers/` - Endpoints HTTP
- `Server/services/` - Lógica negocio
- `Server/utils/websocket_manager.py` - WS manager

---

### 🔧 **Desarrollador ESP32 (Arduino/C++)**

1. [README.md](../README.md) - General
2. [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) - Componentes
3. [PINES_ESP32_DIAGRAMA.md](PINES_ESP32_DIAGRAMA.md) - Hardware
4. [GUIA_CONEXIONADO_FISICO_ESP32.md](GUIA_CONEXIONADO_FISICO_ESP32.md) - Cableado
5. [ENUMERACION_COMPONENTES_ESP32.md](ENUMERACION_COMPONENTES_ESP32.md) - Librerías
6. [FORMATO_MENSAJES_WEBSOCKET.md](FORMATO_MENSAJES_WEBSOCKET.md) - Protocolo WS
7. [ARQUITECTURA_JWT_DUAL.md](ARQUITECTURA_JWT_DUAL.md) - **Por qué RS256 en dispositivos**
8. [SISTEMA_JWT_UNIFICADO.md](SISTEMA_JWT_UNIFICADO.md) - Autenticación

**Carpetas clave:**
- `Device_ESP32_app/` - Código firmware
- `Device_ESP32_app/config.h` - Configuración WiFi, credenciales

---

### 🔐 **DevOps / Administrador**

1. [README.md](../README.md) - General
2. [SETUP_WINDOWS.md](../SETUP_WINDOWS.md) - Instalación
3. [ARQUITECTURA_JWT_DUAL.md](ARQUITECTURA_JWT_DUAL.md) - **Seguridad JWT**
4. [LOGS_SEGURIDAD_HTTPS.md](LOGS_SEGURIDAD_HTTPS.md) - Certificados, HTTPS
5. [DIAGNOSTICO_WEBSOCKET.md](DIAGNOSTICO_WEBSOCKET.md) - Troubleshooting
6. [ARQUITECTURA_WEBSOCKET_3_ROLES.md](ARQUITECTURA_WEBSOCKET_3_ROLES.md) - Permisos

**Carpetas clave:**
- `Server/.env` - Configuración
- `Database/` - Backup y scripts MySQL
- `Server/keys/` - Certificados SSL

---

## 🔍 Búsqueda Rápida

**¿Cómo...?**

| Pregunta | Documento |
|----------|-----------|
| ...instalar el proyecto? | [SETUP_WINDOWS.md](../SETUP_WINDOWS.md) |
| ...cablear un sensor? | [GUIA_CONEXIONADO_FISICO_ESP32.md](GUIA_CONEXIONADO_FISICO_ESP32.md) |
| ...añadir un nuevo endpoint? | [README.md](../README.md#-api-endpoints) |
| ...autenticar un usuario? | [SISTEMA_JWT_UNIFICADO.md](SISTEMA_JWT_UNIFICADO.md) |
| ...asignar permisos? | [ARQUITECTURA_WEBSOCKET_3_ROLES.md](ARQUITECTURA_WEBSOCKET_3_ROLES.md) |
| ...debuggear WebSocket? | [DIAGNOSTICO_WEBSOCKET.md](DIAGNOSTICO_WEBSOCKET.md) |
| ...migrar desde versión antigua? | [MIGRACION_ARDUINOWEBSOCKETS.md](MIGRACION_ARDUINOWEBSOCKETS.md) |
| ...configurar HTTPS? | [LOGS_SEGURIDAD_HTTPS.md](LOGS_SEGURIDAD_HTTPS.md) |
| ...qué hardware necesito? | [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) |
| ...qué librerías necesitan los sensores? | [ENUMERACION_COMPONENTES_ESP32.md](ENUMERACION_COMPONENTES_ESP32.md) |

---

## 📊 Documentación Adicional

### En el proyecto:

```
DatosAnalisisHorario/
├── clases.py           # Script para importar horarios desde Excel
└── resultados/         # CSV con estadísticas de ocupación

tests_individuales_Componentes/
├── PRUEBA_BME280_BH1750/
├── PRUEBA_LD2410/
├── PRUEBAS_HTTPS/
├── PRUEBBA_NFC/
└── RELE_PRUEBAS/       # Códigos de prueba para cada componente
```

---

## 📝 Actualización de Documentación

Esta documentación se mantiene junto al código.

**Cuándo actualizar:**
- ✅ Cambios en API endpoints
- ✅ Nuevos sensores o hardware
- ✅ Cambios en arquitectura WebSocket
- ✅ Nuevas funcionalidades de seguridad

**Cómo actualizar:**
1. Editar el `.md` correspondiente
2. Incluir ejemplos de código cuando sea relevante
   3. Commit: `docs: Actualizar [documento]`
4. Si es cambio crítico, avisar al equipo

---

## 🔗 Enlaces Rápidos

- 📖 **README Principal**: [README.md](../README.md)
- 🚀 **Instalación Rápida**: [SETUP_WINDOWS.md](../SETUP_WINDOWS.md)
- 🐍 **Backend Code**: `Server/appFastApi.py`
- 🔧 **Firmware Code**: `Device_ESP32_app/Device_ESP32_app.ino`
- 🗄️ **Base de Datos**: `Database/backupControlAsistencia.sql`
- 📡 **API Docs (en vivo)**: http://localhost:8000/docs

---

**Última actualización:** Febrero 2025
