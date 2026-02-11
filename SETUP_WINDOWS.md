# 🚀 GUÍA RÁPIDA DE INSTALACIÓN (Windows)

**Tiempo estimado:** 15-20 minutos

## Requisitos Previos

✅ **Windows 10/11** con PowerShell 5.1+  
✅ **Python 3.11** o superior instalado y en PATH  
✅ **Docker Desktop** instalado (para MySQL)  
✅ **Git** (opcional, para clonar repo)

Verificar:
```powershell
python --version    # 3.11+
docker --version    # 20.10+
```

---

## 📝 PASO 1: Preparar la Base de Datos

```powershell
# 1. Abrir PowerShell como administrador
# 2. Navegar a la carpeta Database
cd D:\UEX\ControlAsistencia\Database

# 3. Crear contenedor MySQL (comando en una línea)
docker run --name control-asistencia-mysql -e MYSQL_ROOT_PASSWORD=1234 -e MYSQL_DATABASE=control-asistencia -v "$PWD`:/docker-entrypoint-initdb.d" -p 3306:3306 -d mysql:latest

# 4. Esperar ~20 segundos y verificar
docker ps
# Debería mostrarse "control-asistencia-mysql" en estado "UP"
```

> **Nota:** Si el contenedor ya existe:
> ```powershell
> docker stop control-asistencia-mysql
> docker rm control-asistencia-mysql
> # Luego ejecutar el comando de arriba
> ```

---

## 🐍 PASO 2: Configurar Backend Python

```powershell
# 1. Navegar a raíz del proyecto
cd D:\UEX\ControlAsistencia

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno (los comandos siguientes son en este shell)
.\.venv\Scripts\Activate.ps1

# Debería mostrarse (.venv) al inicio de cada línea

# 4. Actualizar pip
python -m pip install --upgrade pip

# 5. Instalar dependencias
pip install -r Server/requirements.txt

# Esto tardará 1-2 minutos. Esperar a que termine "Successfully installed"
```

---

## 🔑 PASO 3: Configurar Variables de Entorno

```powershell
# 1. Copiar archivo ejemplo
Copy-Item Server\.env.example Server\.env

# 2. Editar el archivo (abrir con cualquier editor)
notepad Server\.env
```

**Valores mínimos a cambiar:**
```
DB_PASSWORD=1234              # ← Cambiar a tu contraseña real
SECRET_KEY=mi_clave_super_s ecreta_minimo_32_caracteres
DEVICE_PASSWORD=device_secret_cambiar
```

**Guardar y cerrar (Ctrl+S)**

---

## ▶️ PASO 4: Iniciar el Servidor

```powershell
# Asegurar que el venv está activo (debe mostrar .venv en el prompt)

# Ir a carpeta Server
cd Server

# Ejecutar servidor
python appFastApi.py

# Debería mostrar algo como:
# ✅ Servidor escuchando en: http://0.0.0.0:8000
# 🔒 SSL/TLS DESHABILITADO (o HABILITADO si existen certificados)
```

> ✅ **¡El servidor está en vivo!**

---

## 🌐 PASO 5: Acceder a la Interfaz

Abrir navegador:

- **Panel de Control:** http://localhost:8000
- **Documentación API:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📱 PASO 6 (Opcional): Configurar ESP32

### En Arduino IDE / PlatformIO:

1. Abrir `Device_ESP32_app/Device_ESP32_app.ino`

2. Editar `config.h`:
```cpp
#define SSID "TuWiFi"
#define PASSWORD "TuContraseña"
#define SERVER_IP "192.168.1.X"    // IP de tu máquina Windows
#define SERVER_PORT 8000
```

3. **Obtener IP de Windows:**
```powershell
ipconfig
# Buscar "IPv4 Address: 192.168.X.X"
```

4. Compilar y cargar en ESP32

5. Abrir Serial Monitor (115200 baud) para ver logs

---

## 🔍 VERIFICACIÓN RÁPIDA

### ✅ Verificar endpoints clave

```powershell
# En otra ventana PowerShell (sin cerrar el servidor):

# 1. Estado servidor
curl http://localhost:8000/docs

# 2. Probar login
curl -X POST http://localhost:8000/login `
  -H "Content-Type: application/json" `
  -d '{\"usuario\":\"admin\",\"contraseña\":\"admin\"}'

# Debería retornar un token JWT
```

### ✅ Verificar base de datos

```powershell
# Conectar a MySQL dentro del contenedor
docker exec -it control-asistencia-mysql mysql -u root -p1234 -e "SHOW DATABASES; USE control-asistencia; SHOW TABLES;"

# Debería mostrarse las tablas: usuarios, asistencias, aulas, clases, etc.
```

---

## 🛠️ Comandos Útiles

### Detener servicios
```powershell
# Detener servidor Python: Ctrl+C en la ventana

# Pausar Docker (sin borrar datos)
docker stop control-asistencia-mysql

# Reanudar Docker
docker start control-asistencia-mysql
```

### Ver logs del Docker
```powershell
docker logs control-asistencia-mysql
docker logs --follow control-asistencia-mysql  # Modo seguimiento
```

### Desactivar entorno Python
```powershell
deactivate
```

### Resetear todo (ojo, borra datos)
```powershell
# 1. Detener servidor Python (Ctrl+C)
# 2. Eliminar contenedor MySQL
docker stop control-asistencia-mysql
docker rm control-asistencia-mysql
# 3. Eliminar venv (opcional)
Remove-Item .venv -Recurse
```

---

## ❌ Problemas Comunes

### ❌ "Port 3306 is already in use"
```powershell
docker stop control-asistencia-mysql
# O cambiar puerto: -p 3307:3306 en el comando docker run
```

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
```powershell
# Asegurar venv está activado y ejecutar:
pip install -r Server/requirements.txt --force-reinstall
```

### ❌ "Can't connect to MySQL server"
```powershell
# Verificar que Docker está corriendo
docker ps

# Ver logs del contenedor
docker logs control-asistencia-mysql
```

### ❌ "SSL: CERTIFICATE_VERIFY_FAILED"
- Por ahora use `http://` (no `https://`)
- Para producción, generar certificados en la carpeta `Server/keys/`

---

## ✨ Siguiente Pasos

1. ✅ Crear usuarios de prueba en la BD
2. ✅ Configurar ESP32 y conectarlo
3. ✅ Revisar documentación en `/DOCS`
4. ✅ Personalizar templates en `/Server/templates`
5. ✅ Integrar con tu sistema académico

---

**¿Algo no funciona?** Revisar `README.md` sección "Troubleshooting" o logs en consola.
