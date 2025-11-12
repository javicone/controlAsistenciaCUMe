# 🔐 Sistema JWT Unificado - Control de Asistencia

## 📋 Resumen

El sistema usa **UN SOLO sistema JWT** basado en **RS256** (criptografía asimétrica) con scopes para diferenciar roles.

---

## 🏗️ Arquitectura JWT

### **Algoritmo: RS256 (Clave Pública/Privada)**

```
┌──────────────────────────────────────┐
│      Sistema JWT Unificado           │
├──────────────────────────────────────┤
│  Algoritmo: RS256                    │
│  Clave Privada: keys/jwt_priv.pem    │
│  Clave Pública: keys/jwt_pub.pem     │
│  Audience: "api"                     │
└──────────────────────────────────────┘

Scopes disponibles:
  - "device"   → ESP32 nodes
  - "admin"    → Administradores
  - "teacher"  → Profesores
  - "conserje" → Conserjes
```

### **¿Por qué RS256 y no HS256?**

| Característica | HS256 (ANTIGUO) | RS256 (ACTUAL) |
|----------------|-----------------|----------------|
| Tipo de clave | Simétrica (SECRET_KEY compartida) | Asimétrica (pública/privada) |
| Seguridad | ⚠️ Si se filtra la clave, cualquiera puede firmar tokens | ✅ Solo el servidor puede firmar (clave privada), cualquiera puede verificar (clave pública) |
| Escalabilidad | ❌ Difícil distribuir la clave secreta | ✅ La clave pública puede distribuirse libremente |
| Uso típico | Apps simples monolíticas | ✅ Microservicios, APIs distribuidas |

---

## 🔑 Estructura del Token JWT

### **Payload Example:**
```json
{
  "sub": "admin@universidad.es",     // Subject: ID del usuario o device_id
  "scope": "admin",                   // Scope: device, admin, teacher, conserje
  "aud": "api",                       // Audience: Validación adicional
  "iat": 1699276800,                  // Issued At: Timestamp de creación
  "exp": 1699280400                   // Expiration: Timestamp de expiración (1h por defecto)
}
```

### **Mapeo Rol DB → Scope JWT:**

| Rol en DB (`usuarios.rol`) | Scope en JWT | Endpoint WebSocket |
|----------------------------|--------------|-------------------|
| `administrador` | `admin` | `/ws/admin` |
| `profesor` | `teacher` | `/ws/teacher` (futuro) |
| `conserje` | `conserje` | `/ws/conserje` |
| `device` (ESP32) | `device` | `/ws` |

---

## 🔧 Funciones del Sistema JWT

### **Archivo:** `Server/security/jwt.py`

#### 1️⃣ `issue_token(sub, scope, exp_seconds=3600) → str`
**Genera un nuevo token JWT**

```python
from security.jwt import issue_token

# Para un administrador
token = issue_token(sub="admin@universidad.es", scope="admin", exp_seconds=3600)

# Para un dispositivo ESP32
token = issue_token(sub="ESP32_AULA_A101", scope="device", exp_seconds=7200)

# Para un conserje
token = issue_token(sub="conserje@universidad.es", scope="conserje")
```

**Parámetros:**
- `sub` (str): Identificador único (email para usuarios, device_id para ESP32)
- `scope` (Literal): "device", "admin", "teacher", "conserje"
- `exp_seconds` (int): Tiempo de expiración en segundos (default: 3600 = 1 hora)

**Retorna:** String con el token JWT firmado

---

#### 2️⃣ `verify_token(token, required_scope) → dict`
**Valida un token JWT y verifica que tenga el scope correcto**

```python
from security.jwt import verify_token

# En endpoint /ws/admin
payload = verify_token(token, required_scope="admin")
# Si el token no tiene scope="admin", lanza HTTPException 403

# En endpoint /ws/conserje
payload = verify_token(token, required_scope="conserje")

# En endpoint /ws (devices)
payload = verify_token(token, required_scope="device")
```

**Parámetros:**
- `token` (str): Token JWT a validar
- `required_scope` (str): Scope requerido para acceder

**Retorna:** Dict con el payload del token `{"sub": "...", "scope": "...", "aud": "...", "iat": ..., "exp": ...}`

**Excepciones:**
- `HTTPException 401`: Token inválido, expirado o mal firmado
- `HTTPException 403`: Scope incorrecto (no autorizado)

---

#### 3️⃣ `bearer_auth(authorization) → dict`
**Extrae y valida token del header Authorization**

```python
from security.jwt import bearer_auth

# En endpoints REST protegidos
@router.get("/protected")
def protected_endpoint(payload: dict = Depends(bearer_auth)):
    device_id = payload["sub"]
    return {"message": f"Hello {device_id}"}
```

**Header esperado:**
```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

#### 4️⃣ `DevicePrincipal` (Dependency)
**Extrae el device_id del token en endpoints REST**

```python
from security.jwt import DevicePrincipal

@router.get("/device/status")
def get_device_status(device_id: str = DevicePrincipal):
    # device_id ya está extraído del JWT
    return {"device_id": device_id, "status": "online"}
```

---

## 🌐 Flujo de Autenticación por Tipo de Cliente

### 1️⃣ **Usuario Web (Admin/Conserje/Profesor)**

```
┌─────────────┐
│   Browser   │
└─────────────┘
      │
      │ POST /auth/login
      │ { "correo": "admin@universidad.es", "password": "..." }
      ▼
┌─────────────────────────────────────────┐
│  Server: /auth/login                    │
│  1. authenticate_user() → Verifica DB   │
│  2. Mapea rol DB → scope JWT:           │
│     "administrador" → "admin"           │
│     "conserje" → "conserje"             │
│  3. issue_token(sub=user_id, scope=...) │
└─────────────────────────────────────────┘
      │
      │ Response: { "token": "eyJ...", "rol": "administrador" }
      ▼
┌─────────────┐
│   Browser   │ Guarda en sessionStorage/localStorage
│   Token:    │
│   eyJ...    │
└─────────────┘
      │
      │ Conecta WebSocket con token en query
      │ wss://server/ws/admin?token=eyJ...
      ▼
┌─────────────────────────────────────────┐
│  Server: /ws/admin                      │
│  1. verify_token(token, "admin")        │
│  2. Si scope != "admin" → 403 Forbidden │
│  3. Si OK → Acepta conexión WebSocket   │
└─────────────────────────────────────────┘
```

---

### 2️⃣ **Dispositivo ESP32**

```
┌─────────────┐
│   ESP32     │
└─────────────┘
      │
      │ POST /auth/device
      │ { "device_id": "ESP32_AULA_A101", "api_key": "..." }
      ▼
┌─────────────────────────────────────────┐
│  Server: /auth/device                   │
│  1. get_device(device_id) → Verifica DB │
│  2. Compara api_key con DB              │
│  3. issue_token(sub=device_id,          │
│                 scope="device")         │
└─────────────────────────────────────────┘
      │
      │ Response: { "access_token": "eyJ..." }
      ▼
┌─────────────┐
│   ESP32     │ Guarda en Preferences (NVS)
│   Token:    │
│   eyJ...    │
└─────────────┘
      │
      │ Conecta WebSocket con token en query
      │ wss://server/ws?token=eyJ...
      ▼
┌─────────────────────────────────────────┐
│  Server: /ws                            │
│  1. verify_token(token, "device")       │
│  2. Si scope != "device" → 403 Forbidden│
│  3. Si OK → Acepta conexión WebSocket   │
└─────────────────────────────────────────┘
```

---

## 🔄 Migración del Sistema Antiguo (HS256) al Nuevo (RS256)

### **Cambios Realizados:**

#### ✅ `Server/security/jwt.py`
- Añadido scope `"conserje"` a la lista de scopes permitidos

#### ✅ `Server/services/auth_service.py`
- `create_access_token()`: Ahora usa `issue_token()` internamente con mapeo rol→scope
- `decode_access_token()`: Usa claves RS256 y mapea scope→rol para compatibilidad

#### ✅ `Server/routers/auth.py`
- Endpoint `/auth/login`: Usa `issue_token()` directamente con mapeo de roles

#### ✅ `Server/routers/websockets.py`
- Endpoint `/ws/admin`: Verifica `scope="admin"`
- Endpoint `/ws/conserje`: Verifica `scope="conserje"`
- Endpoint `/ws`: Verifica `scope="device"`

---

## 🔐 Generación de Claves RS256

### **Comandos PowerShell:**

```powershell
# 1. Crear directorio de claves (si no existe)
New-Item -ItemType Directory -Force -Path "Server\keys"

# 2. Generar clave privada (2048 bits)
openssl genrsa -out Server\keys\jwt_priv.pem 2048

# 3. Extraer clave pública de la privada
openssl rsa -in Server\keys\jwt_priv.pem -pubout -out Server\keys\jwt_pub.pem

# 4. Verificar claves
Get-Content Server\keys\jwt_priv.pem
Get-Content Server\keys\jwt_pub.pem
```

### **Contenido esperado:**

**`jwt_priv.pem`** (Clave Privada - ⚠️ NUNCA compartir):
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...
-----END RSA PRIVATE KEY-----
```

**`jwt_pub.pem`** (Clave Pública - ✅ Puede distribuirse):
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
...
-----END PUBLIC KEY-----
```

---

## 🛡️ Seguridad

### **Ventajas del Sistema Actual:**

1. ✅ **Criptografía Asimétrica**: Clave privada solo en el servidor
2. ✅ **Scopes Granulares**: Cada endpoint verifica permisos específicos
3. ✅ **Audience Validation**: Previene reutilización de tokens en otros servicios
4. ✅ **Expiración**: Tokens expiran en 1 hora por defecto
5. ✅ **Stateless**: No requiere almacenar sesiones en servidor

### **Buenas Prácticas:**

- ⚠️ **NUNCA commits `jwt_priv.pem`** al repositorio (añadir a `.gitignore`)
- ✅ Rotar claves periódicamente (cada 6-12 meses)
- ✅ Usar HTTPS/WSS siempre para transmitir tokens
- ✅ Tokens en query params solo para WebSocket (REST usa headers)
- ✅ Implementar refresh tokens si se necesitan sesiones largas

---

## 📊 Comparativa: Antiguo vs Nuevo

| Aspecto | HS256 (Antiguo) | RS256 (Actual) |
|---------|-----------------|----------------|
| **Algoritmo** | Simétrico | Asimétrico |
| **Claves** | SECRET_KEY hardcoded | jwt_priv.pem + jwt_pub.pem |
| **Seguridad** | ⚠️ Media | ✅ Alta |
| **Payload** | `{"sub": id, "rol": "admin"}` | `{"sub": id, "scope": "admin", "aud": "api"}` |
| **Validación** | Cualquier servidor con SECRET_KEY | Solo servidor con clave privada |
| **Scopes** | ❌ No soportados | ✅ device, admin, teacher, conserje |
| **Distribución** | ❌ Difícil compartir SECRET_KEY | ✅ Clave pública puede distribuirse |

---

## 🧪 Testing del Sistema JWT

### **Generar un token de prueba:**

```python
from security.jwt import issue_token

# Token de admin
admin_token = issue_token(sub="admin@test.es", scope="admin", exp_seconds=3600)
print(f"Admin Token: {admin_token}")

# Token de conserje
conserje_token = issue_token(sub="conserje@test.es", scope="conserje", exp_seconds=3600)
print(f"Conserje Token: {conserje_token}")

# Token de device
device_token = issue_token(sub="ESP32_TEST", scope="device", exp_seconds=7200)
print(f"Device Token: {device_token}")
```

### **Verificar un token:**

```python
from security.jwt import verify_token

# Debería funcionar
payload = verify_token(admin_token, required_scope="admin")
print(f"✅ Admin verified: {payload}")

# Debería lanzar 403 Forbidden
try:
    verify_token(admin_token, required_scope="device")
except Exception as e:
    print(f"❌ Expected error: {e}")
```

### **Decodificar token sin verificar (para debugging):**

```python
from jose import jwt

# Ver contenido del token sin validar firma
payload = jwt.decode(admin_token, options={"verify_signature": False})
print(f"Token payload: {payload}")
```

---

## 🎯 Resumen

**UN SOLO SISTEMA JWT (RS256)** con:
- ✅ **4 scopes**: device, admin, teacher, conserje
- ✅ **3 endpoints WebSocket**: /ws (device), /ws/admin (admin), /ws/conserje (conserje)
- ✅ **2 endpoints de autenticación**: /auth/login (usuarios), /auth/device (ESP32)
- ✅ **1 par de claves**: jwt_priv.pem (firma) + jwt_pub.pem (verifica)

**Todos usan el mismo token JWT**, solo cambia el **scope** que determina los permisos.
