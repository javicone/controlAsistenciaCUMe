# Control de Asistencia y Monitorización de Aulas (IoT)

![Logo de la aplicación](imagenes/image.png)  
https://wokwi.com/projects/446089574014956545

Repositorio con el backend en Python (Flask/FastAPI + WebSockets) y el código para dispositivos ESP32 que permiten:
- Registrar asistencia vía NFC.
- Monitorizar temperatura, iluminación y presencia en aulas.
- Control remoto de relés por aula.
Este README recoge: estructura del repo, cómo configurar y ejecutar el backend, y notas útiles para trabajar con el firmware.

## Estado actual (resumen)
- Migración en curso del monolito Flask a FastAPI con routers, middlewares y WebSockets (ver `Server/appFastApi.py` y `Server/routers/*`).
- La base de datos MySQL se ha movido a Docker. Ya no necesitas instalar MySQL localmente si usas el contenedor.
- El código antiguo de Flask se conserva en `Server/antiguasVersiones/` como referencia.

## Estructura principal
- `Database/` — Dump SQL: `backupControlAsistencia.sql` y utilidades (`docker comando.txt`).
- `DatosAnalisisHorario/` — Script `clases.py` y salidas (CSV/XLSX) con estadísticas por aula, carrera, día/hora y cuatrimestre.
- `Device_ESP32_app/` — Firmware para ESP32 (PN532 NFC, BME280, BH1750, radar LD2410, LEDs, buzzer, relé, WebSocket). Archivos clave: `Device_ESP32_app.ino`, `NFC_module.ino`, `BME_module.ino`, `LightMeter_module.ino`, `radar_module.ino`, `setupSensores.ino`, `webSocketEvent.ino`, `api_rest.ino`, `funciones_auxiliares.ino`, `UNIT_PN532.*`, `globals.h/.cpp`, `indicators.ino`.
- `Server/` — Backend Python (FastAPI + WebSockets):
  - `appFastApi.py` — servidor principal actual (endpoints REST, websockets y templates).
  - `routers/`, `models/`, `services/`, `middleware/`, `utils/`, `static/`, `templates/` — nueva arquitectura modular.
  - `antiguasVersiones/` — versiones previas en Flask (por compatibilidad/histórico).
- `imagenes/` — recursos estáticos (por ejemplo, `imagenes/image.png`).
- `README.md` — (este fichero)
- `Sensor para Aula.docx` — documentación adicional.

## Estructura del repositorio (actual)

```
ControlAsistencia/
├── cert.pem
├── key.pem
├── imagenes/
│   └── image.png
├── Database/
│   ├── backupControlAsistencia.sql
│   └── docker comando.txt
├── DatosAnalisisHorario/
├── Device_ESP32_app/
│   ├── Device_ESP32_app.ino
│   ├── api_rest.ino
│   ├── BME_module.ino
│   ├── LightMeter_module.ino
│   ├── NFC_module.ino
│   ├── radar_module.ino
│   ├── setupSensores.ino
│   ├── webSocketEvent.ino
│   ├── funciones_auxiliares.ino
│   ├── globals.h
│   ├── globals.cpp
│   ├── indicators.ino
│   ├── UNIT_PN532.h
│   └── UNIT_PN532.cpp
└── Server/
    ├── appFastApi.py
    ├── config.py
    ├── database.py
    ├── requirements.txt
    ├── antiguasVersiones/
    │   ├── appFastApi_MONOLITO.py
    │   └── appFlask.py
    ├── middleware/
    │   ├── __init__.py
    │   ├── cors.py
    │   └── logging.py
    ├── models/
    │   ├── __init__.py
    │   ├── asistencia.py
    │   ├── aula.py
    │   ├── clase.py
    │   └── user.py
    ├── routers/
    │   ├── __init__.py
    │   ├── asistencias.py
    │   ├── aulas.py
    │   ├── auth.py
    │   ├── clases.py
    │   ├── views.py
    │   └── websockets.py
    ├── services/
    │   ├── __init__.py
    │   ├── asistencia_service.py
    │   ├── aula_service.py
    │   ├── auth_service.py
    │   └── clase_service.py
    ├── static/
    │   └── css/
    │       └── styles.css
    ├── templates/
    │   ├── administrador.html
    │   ├── conserjes.html
    │   ├── dashboard.html
    │   ├── gestion_aulas.html
    │   └── index.html
    └── utils/
        ├── __init__.py
        ├── database_pool.py
        └── websocket_manager.py
```

## Base de datos en Docker (MySQL)

La base de datos se ejecuta ahora en un contenedor Docker de MySQL. Desde PowerShell, sitúate en la carpeta `Database` y ejecuta el siguiente comando (Windows):

```powershell
# En: D:\UEX\ControlAsistencia\Database
docker run --name control-asistencia-mysql ^
  -e MYSQL_ROOT_PASSWORD=1234 ^
  -e MYSQL_DATABASE=control-asistencia ^
  -v "%cd%:/docker-entrypoint-initdb.d" ^
  -p 3306:3306 ^
  -d mysql:latest
```

Qué hace cada parámetro:
- `MYSQL_ROOT_PASSWORD`: contraseña del usuario root de MySQL dentro del contenedor.
- `MYSQL_DATABASE`: crea automáticamente la BD `control-asistencia` si no existe.
- `-v "%cd%:/docker-entrypoint-initdb.d"`: vincula la carpeta actual (donde está `backupControlAsistencia.sql`) a la ruta de auto-inicialización de MySQL en el contenedor. Cualquier `.sql` en esa carpeta se ejecutará automáticamente en el primer arranque del contenedor.
- `-p 3306:3306`: expone MySQL en el puerto 3306 del host.

### Cargar el backup de la base de datos

Tienes dos opciones:

1) Auto-inicialización (primer arranque del contenedor)
- Asegúrate de que `Database/backupControlAsistencia.sql` está en la carpeta `Database` antes de lanzar el `docker run` anterior. MySQL ejecutará ese SQL automáticamente al iniciar por primera vez.

2) Importación manual (si el contenedor ya existe o quieres reimportar)
- Ejecuta el cliente MySQL dentro del contenedor leyendo el SQL desde el host:

```powershell
# Desde la raíz del repo o dentro de Database
# Importa el backup dentro del contenedor MySQL
Get-Content Database\backupControlAsistencia.sql | docker exec -i control-asistencia-mysql mysql -u root -p1234 control-asistencia
```

Comprobación rápida (opcional, si tienes cliente mysql en el host):
```powershell
mysql -h 127.0.0.1 -P 3306 -u root -p1234 -e "SHOW DATABASES;"
```

## Requisitos (backend)
- Python 3.10+ (3.11/3.12 recomendadas).
- MySQL/MariaDB para la base de datos (recomendado vía Docker, ver sección anterior).
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

3) Base de datos en Docker: sigue la sección "Base de datos en Docker (MySQL)" de este README. Si prefieres MySQL instalado localmente, puedes seguir usando el cliente y redirigiendo el SQL como alternativa.

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

