# Control de Asistencia y Monitorización de Aulas (IoT)

Repositorio con el backend en Python (Flask + WebSockets) y el código para dispositivos ESP32 que permiten:
- Registrar asistencia vía NFC.
- Monitorizar temperatura, iluminación y presencia en aulas.
- Control remoto de relés por aula.
Este README recoge: estructura del repo, cómo configurar y ejecutar el backend, y notas útiles para trabajar con el firmware.

## Estructura principal
- `Database/` — Dump SQL: `backupControlAsistencia.sql` con el esquema / datos de ejemplo.
- `Device/` — Sketches y código C++ para ESP32 (PN532, sensores, lógica de envío):
  - `api_rest.ino`, `leerNFC.ino`, `SensorTempPresNFCMultithyRegistroLimpio.ino`, `webSocketEvent.ino`, `funciones_auxiliares.ino`, `inicializacionsensores.ino`, `pinesyvariablesauxiliares.h`, `UNIT_PN532.*`.
- `Server/` — Backend Python (Flask + WebSockets):
  - `appV4.py` — servidor principal (endpoints REST y arranque de WebSocket server).
  - `config.py` — configuración (DB, SECRET_KEY).
- `README.md` — (este fichero)
- `Sensor para Aula.docx` — documentación adicional.

## Requisitos (backend)
- Python 3.10+ (3.11/3.12 recomendadas).
- MySQL/MariaDB para la base de datos.
- Entorno de Arduino/PlatformIO con soporte ESP32 y las librerías para PN532, BME280, BH1750 si se usa el firmware.

He añadido un `requirements.txt` básico con las dependencias del backend.
## Instalación rápida (Windows / PowerShell)

1) Crear y activar un entorno virtual:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

3) Importar la base de datos (desde un cliente MySQL):

```powershell
# Ajusta usuario/host y la ruta al .sql según tu entorno
mysql -u root -p control_asistencia < Database\backupControlAsistencia.sql
```

## Configuración

- Edita `Server/config.py` y pon las credenciales correctas en `DB_CONFIG` y una `SECRET_KEY` segura para JWT.
- Evita dejar credenciales en texto plano en repositorios públicos.

Ejemplo (no dejar como está en producción):

```py
DB_CONFIG = {
   'host': 'localhost',
   'user': 'tu_usuario',
   'password': 'tu_password',
   'database': 'control_asistencia',
   'port': 3306,
}

SECRET_KEY = 'CAMBIA_POR_UNA_CLAVE_LARGA_Y_SECRETA'
```

## Ejecutar el backend (desarrollo)

Desde la raíz del repositorio (PowerShell, con el venv activado):

```powershell
python Server\appV4.py
```

- Flask por defecto escucha en: http://0.0.0.0:5000
- El servidor WebSocket usa el puerto: 5678 (ajustable en `appV4.py`).

Notas: `appV4.py` arranca un bucle asyncio para websockets y ejecuta Flask en paralelo. Revisa la variable `loop` en `if __name__ == '__main__'`.

## Endpoints útiles

- GET `/` — Página inicial (render `index.html`).
- POST `/login` — Login de usuario. Devuelve JWT.
- POST `/login_aula` — Login de aula (genera token para el dispositivo/aula).
- POST `/registro` — Registrar asistencia desde ESP32. Body JSON: { "uid": "...", "nombre_aula": "Aula 101" }.
- POST `/datos_aula` — Telemetría periódica del ESP32: { "aula": "Aula 101", "temperatura": 23.5, "luz": 300, "personas": 2, "clase_en_curso": true }.
- POST `/control_relay` — Cambiar relé: { "aula": "Aula 101", "relay": true }.
- GET `/estado_aulas` — Estado en memoria de las aulas.

## WebSockets

- El backend mantiene `connected_clients` y difunde eventos (estado inicial, actualizaciones de aula y de relay) en JSON.
- Puerto por defecto: 5678.

## Revisión rápida del proyecto — hallazgos y recomendaciones

He revisado `Server/appV4.py`, `Server/config.py` y la estructura de `Device/` y `Database/`. Puntos relevantes:

1. Seguridad / buenas prácticas
  - Las contraseñas parecen compararse en texto plano en `/login` y en `/login_aula`. Se recomienda usar hashing (bcrypt/argon2) y verificar con funciones seguras.
  - `Server/config.py` contiene credenciales y `SECRET_KEY` por defecto; no subir estas claves a repositorios públicos.

2. Errores y detalles en `appV4.py` (posibles bugs a corregir):
  - En `registrar_asistencia()` se realizan varias llamadas a `cursor.fetchone()` que parecen fuera de orden; después de obtener `usuario` y luego ejecutar otra consulta, el código hace `profesor = cursor.fetchone()` sin una nueva `execute` previa — esto probablemente devuelve `None` y es innecesario.
  - `logging.debug("Recibido UID válido", uid)` usa firma de logging incorrecta; debería usar `logging.debug("Recibido UID válido: %s", uid)` o f-strings.
  - Validación de `uid` solo comprueba longitud y existencia; conviene validar formato y normalizar inputs.
  - `appV4.py` usa la variable `loop` en varias rutinas; asegúrate que `loop` esté definida antes de cualquier llamada que la use.

3. Experiencia de desarrollador
  - No existe `requirements.txt` (ahora añadido). Considera añadir un `README` separado para firmware con pasos de compilación y librerías necesarias.
  - Añadir `env.example` o usar variables de entorno para evitar poner secretos en `config.py`.

## Próximos pasos sugeridos (opcionales, puedo hacerlo yo):

1. Corregir los puntos mencionados en `appV4.py` (pequeñas modificaciones para evitar bugs y mejorar logging).
2. Reemplazar comparación de contraseñas por hashing (añadir `bcrypt` o `argon2-cffi`) y migrar la BD para almacenar hashes.
3. Añadir un script `run.sh` / `run.ps1` y un `docker-compose.yml` para facilitar despliegues.
4. Documentar el firmware: dependencias de Arduino/PlatformIO y flujos principales.

Si quieres, aplico ahora alguno de los siguientes cambios: (elige uno o di "déjalo así")
- Corregir los bugs menores en `Server/appV4.py` (logging y cursor.fetchone).
- Reforzar autenticación para usar hashes (añadir `bcrypt` y cambiar código de login).
- Añadir `env.example` y cargar la configuración desde variables de entorno.

## Contacto / Contribuir

1. Haz fork/clone.
2. Crear rama feature/bugfix.
3. PR con descripción y pasos para probar.

---

Archivo añadido: `requirements.txt` con las dependencias mínimas del backend.

Si quieres que actualice el código (por ejemplo corregir los bugs detectados), dime cuál de las tareas anteriores prefieres y lo hago.
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