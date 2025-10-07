# Proyecto IoT — Control de Asistencia y Monitorización de Aulas

Un sistema IoT para el registro de asistencia (NFC), monitorización ambiental (temperatura, luz, detección de presencia) y control remoto de relés desde un backend Python (Flask) y dispositivos ESP32.

## Contenido del repositorio

- `Backend4/` — Backend en Python (Flask + WebSockets).
  - `appV4.py` — Servdor principal (endpoints REST, WebSocket server, lógica de difusión y control).
  - `database.py` — Función `conectar_db()` para obtener la conexión a la base de datos.
  - `config.py` — Configuraciones (credenciales DB, `SECRET_KEY` para JWT).
  - `templates/` — Plantillas HTML (`index.html`, `dashboard.html`, `conserjes.html`).
  - `static/` — CSS y assets estáticos.

- `SensorTempPresNFCMultithyRegistroLimpio/` — Código y sketches para ESP32 (lectura NFC, sensores, envío REST/WebSocket).
  - `SensorTempPresNFCMultithyRegistroLimpio.ino`, `api_rest.ino`, `leerNFC.ino`, `funciones_auxiliares.ino`, `pinesyvariablesauxiliares.h`, `UNIT_PN532.*`.

- `backupControlAsistencia.sql` — Dump / esquema de la base de datos (tablas: `usuarios`, `aulas`, `clases`, `asistencias`, etc.).

## Resumen funcional

- Registro de asistencia: el dispositivo (ESP32 con lector NFC PN532) envía el UID al backend en `/registro` para registrar la asistencia en la BD.
- Monitorización de aulas: el ESP32 envía telemetría a `/datos_aula` (temperatura, luz, personas, si hay clase) y el backend mantiene un estado en memoria (`aulas_estado`) y difunde actualizaciones a los clientes web conectados vía WebSocket.
- Control remoto de relés: la web o la API pueden cambiar el estado del relé por aula (`/control_relay`), y el backend lo propaga a los clientes conectados.
- Autenticación: JWT (via `flask_jwt_extended`) en endpoints que lo requieren. `config.py` contiene `SECRET_KEY`.

## Requisitos

- Python 3.10+ (se recomienda 3.11 o 3.12 según el entorno).
- MySQL / MariaDB para la base de datos.
- Para el firmware: entorno de Arduino/PlatformIO con soporte ESP32 y librerías para PN532, BME280, BH1750, etc.

## Dependencias del backend (pip)

- flask
- flask-jwt-extended
- websockets
- mysql-connector-python

Ejemplo para instalar en un entorno virtual (PowerShell en Windows):

```powershell
# Crear y activar venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install --upgrade pip
pip install flask flask-jwt-extended websockets mysql-connector-python
```

Si prefieres, crea un `requirements.txt` con esas dependencias.

## Configuración

1. Edita `Backend4/config.py` y establece las credenciales correctas para la base de datos y una `SECRET_KEY` segura para JWT. Ejemplo (no poner datos en texto plano en producción):

```py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'tu_usuario',
    'password': 'tu_password',
    'database': 'control_asistencia',
    'port': 3306
}
SECRET_KEY = 'cambia_esto_por_una_clave_secreta_larga'
```

2. Importa la base de datos (desde un cliente MySQL en Windows):

```powershell
mysql -u root -p control_asistencia < backupControlAsistencia.sql
```

Ajusta `root` / `control_asistencia` según tu instalación.

## Ejecutar el backend

En PowerShell (desde la raíz del repo o la carpeta que prefieras):

```powershell
# Activar entorno (si existe)
.\.venv\Scripts\Activate.ps1

# Ejecutar
python Backend4/appV4.py
```

- Flask servirá en: http://0.0.0.0:5000
- WebSockets escuchan en: ws://0.0.0.0:5678

Nota: `appV4.py` arranca Flask y un servidor WebSocket en paralelo (usa `asyncio` + `websockets` y un hilo para Flask).

## Endpoints principales

- GET `/` — Página de inicio (render `index.html`).
- POST `/login` — Login de usuario (correo + password). Devuelve `token` (JWT) y `rol`.
- POST `/login_aula` — Login de aula (nombre_aula + password_aula). Devuelve token de aula.
- POST `/registro` — Registrar asistencia desde el ESP32. Body JSON: `{ "uid": "...", "nombre_aula": "Aula 101" }`.
- GET `/asistencias` — Devuelve asistencias; requiere JWT. El contenido depende del rol (profesor vs conserje/administrador).
- GET `/proxima_clase?aula=NombreAula` — Devuelve la próxima clase para un aula.
- POST `/datos_aula` — El ESP32 publica la telemetría: `{ "aula": "Aula 101", "temperatura": 23.5, "luz": 300, "personas": 2, "clase_en_curso": true }`.
- POST `/control_relay` — Cambiar estado del relé: `{ "aula": "Aula 101", "relay": true }`.
- GET `/estado_aulas` — Estado en memoria de todas las aulas.

## WebSockets

- El backend mantiene `connected_clients` y difunde actualizaciones en formato JSON mediante la función `broadcast(event)`.
- Mensajes comunes:
  - `{"tipo":"estado_inicial","data": { ... }}` — enviado al conectar para poblar UI.
  - `{"tipo":"actualizacion_aula","aula":"Aula 101", "temperatura":..}` — telemetría.
  - `{"tipo":"actualizacion_relay","aula":"Aula 101", "relay": true}` — cambio de relé.

## Integración ESP32 (firmware)

- El firmware usa los endpoints `/obtenerToken` (implementado en los sketches como `obtenerToken`), `/proxima_clase` y los endpoints anteriores (`/datos_aula`, `/registro`).
- Flujo típico:
  1. ESP32 obtiene token de aula o de usuario.
  2. Envía telemetría periódica a `/datos_aula`.
  3. Cuando se detecta una tarjeta NFC, llama a `/registro` para guardar asistencia.
  4. El firmware puede suscribirse a WebSockets para recibir cambios de relé (si está implementado en el sketch).

Revisar la carpeta `SensorTempPresNFCMultithyRegistroLimpio/` para funciones y ejemplos de uso.

## Seguridad y buenas prácticas

- No almacenar contraseñas en texto plano. En producción, guarda hashes (bcrypt/argon2) y valida usando funciones de verificación.
- Servir Flask detrás de un proxy (nginx) con HTTPS para proteger JWT y credenciales.
- Revisar límites de tamaño y validaciones en los endpoints (por ejemplo, longitudes de UID, tipos numéricos).
- Limitar los orígenes y autenticar clientes WebSocket si se desea mayor seguridad.

## Depuración y comprobaciones rápidas

- Ver logs en consola: `appV4.py` tiene logging activado (`logging.basicConfig(level=logging.DEBUG)`).
- Si WebSockets no llegan, comprobar que el puerto 5678 no esté bloqueado por firewall.
- Comprobar que la base de datos acepta conexiones con las credenciales de `config.py`.

## Contribuir

1. Fork/Clone del repositorio.
2. Crear rama feature/bugfix.
3. PR con descripción y pasos para reproducir / probar.

## Licencia

Licencia: añade aquí la licencia deseada (por ejemplo MIT) o deja para coordinar con el equipo.

## Contacto

Para dudas o issues, crea un issue en el repositorio con logs y pasos para reproducir el comportamiento.

---

Este README es un punto de arranque: puedo añadir ejemplos curl, un `requirements.txt`, `docker-compose.yml` o instrucciones para CI/CD si quieres que los agregue ahora.