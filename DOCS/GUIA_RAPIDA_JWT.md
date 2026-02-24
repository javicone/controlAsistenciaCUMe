# 🔐 Guía Rápida: Sistema JWT Dual

## TL;DR (Resumen de 30 segundos)

```
🌐 Sesiones Web    → HS256 (simétrico)   → Rápido, servidor seguro
🤖 Dispositivos IoT → RS256 (asimétrico) → Resistente a robo físico
```

**¿Por qué no uno solo?**
- Si usáramos HS256 para dispositivos → Roban ESP32 → Extraen clave → **Pueden firmar tokens falsos** 💥
- Con RS256 → Roban ESP32 → Solo tienen clave pública → **No pueden firmar tokens** ✅

---

## Tabla Comparativa Rápida

| Aspecto | Web (HS256) | IoT (RS256) |
|---------|-------------|-------------|
| **Dónde se usa** | Login profesores/admins | ESP32 en aulas |
| **Clave** | Secreta única | Par público/privado |
| **Velocidad** | ⚡⚡⚡ Muy rápido | ⚡⚡ Rápido |
| **Seguridad física** | No relevante (servidor) | 🛡️ Crítica (robo posible) |
| **Duración token** | 8 horas | 1 año |
| **Archivo** | `routers/auth.py` | `security/jwt.py` |

---

## Flujos de Autenticación

### 🌐 Web (Profesor/Admin)
```
1. POST /auth/login
   Body: { correo, password }
   
2. Backend valida con bcrypt
3. Genera token HS256 con SECRET_KEY
4. Devuelve cookie HttpOnly
5. Navegador incluye cookie en requests
6. Backend verifica con misma SECRET_KEY
```

### 🤖 Dispositivo ESP32
```
1. POST /auth/device
   Body: { device_id, api_key }
   
2. Backend valida con DB
3. Genera token RS256 con PRIVATE_KEY
4. Devuelve token al ESP32
5. ESP32 almacena token en memoria
6. Backend verifica con PUBLIC_KEY
```

---

## Escenarios de Seguridad

### ❌ Ataque: Robo de ESP32 (con HS256 hipotético)
```
Atacante extrae firmware
  ↓
Encuentra SECRET_KEY del algoritmo HS256
  ↓
Puede firmar tokens para CUALQUIER dispositivo
  ↓
SISTEMA COMPROMETIDO 💥
```

### ✅ Defensa: Robo de ESP32 (con RS256 actual)
```
Atacante extrae firmware
  ↓
Encuentra PUBLIC_KEY del algoritmo RS256
  ↓
Solo puede VERIFICAR tokens (operación normal)
  ↓
NO puede FIRMAR tokens nuevos
  ↓
Sistema sigue seguro ✅
```

---

## Ubicación de Claves

```bash
# Web HS256
SERVER:
  .env → SECRET_KEY=xxxx

# IoT RS256
SERVER:
  keys/jwt_priv.pem → Clave privada (NUNCA sale)
  keys/jwt_pub.pem  → Clave pública

ESP32:
  auth_device_jwt.ino → jwt_public_key (solo verifica)
```

---

## Generación de Claves RSA

```bash
# Generar par de claves (solo una vez)
cd Server/keys

# Clave privada (2048 bits)
openssl genrsa -out jwt_priv.pem 2048

# Clave pública (derivada de la privada)
openssl rsa -in jwt_priv.pem -pubout -out jwt_pub.pem

# Permisos restrictivos
chmod 600 jwt_priv.pem
chmod 644 jwt_pub.pem
```

---

## FAQ Ultra-Rápido

**P: ¿Por qué no RS256 para todo?**
R: Más lento sin beneficio (sesiones web están en servidor seguro)

**P: ¿Por qué no HS256 para dispositivos?**
R: Vulnerable a extracción de clave por robo físico

**P: ¿Puedo usar RS256 para web también?**
R: Sí, pero innecesario y más lento (~30% overhead)

**P: ¿Los dispositivos pueden generar tokens?**
R: **NO**. Solo pueden verificarlos (tienen clave pública)

**P: ¿Qué pasa si roban jwt_priv.pem?**
R: Todo comprometido. Rotar claves inmediatamente.

---

## Código de Ejemplo

### Generar Token Web (HS256)
```python
# Server/routers/auth.py
from jose import jwt
from config import SECRET_KEY, ALGORITHM

token = jwt.encode(
    {"sub": user_id, "rol": "admin", "exp": datetime.utcnow() + timedelta(hours=8)},
    SECRET_KEY,
    algorithm="HS256"
)
```

### Generar Token Dispositivo (RS256)
```python
# Server/security/jwt.py
from jose import jwt
from pathlib import Path

PRIV = Path("keys/jwt_priv.pem").read_text()

token = jwt.encode(
    {"sub": "ESP32_001", "scope": "device", "exp": datetime.utcnow() + timedelta(days=365)},
    PRIV,
    algorithm="RS256"
)
```

### Verificar Token en ESP32 (RS256)
```cpp
// Device_ESP32_app/auth_device_jwt.ino
#include <JWT.h>

const char* jwt_public_key = R"(
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
)";

bool verifyToken(String token) {
    // Solo puede VERIFICAR, nunca FIRMAR
    JWT jwt(jwt_public_key);
    return jwt.verify(token);
}
```

---

## Lectura Completa

📖 **Documentación detallada:** [ARQUITECTURA_JWT_DUAL.md](ARQUITECTURA_JWT_DUAL.md)

Incluye:
- Análisis de modelo de amenazas
- Benchmarks de rendimiento
- Mejores prácticas de rotación de claves
- Roadmap de actualizaciones
- Referencias RFC y OWASP

---

**Versión:** 1.0 | **Fecha:** 16 Feb 2026 | **Mantenedor:** Sistema Control Asistencia UEx
