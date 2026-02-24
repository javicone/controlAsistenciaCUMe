# Arquitectura JWT Dual: HS256 vs RS256

## 📋 Resumen Ejecutivo

El Sistema de Control de Asistencia implementa **dos algoritmos JWT diferentes** según el caso de uso:

- **HS256 (HMAC con SHA-256)** → Sesiones web (profesores, conserjes, administradores)
- **RS256 (RSA con SHA-256)** → Dispositivos IoT (ESP32)

Esta arquitectura dual **no es un error de diseño**, sino una decisión consciente de seguridad basada en el modelo de amenazas de cada contexto.

---

## 🔐 Modelo de Amenazas

### Sesiones Web (HS256)
**Contexto:**
- Tokens almacenados en cookies HttpOnly en navegadores
- Servidor backend seguro y controlado
- Acceso físico al servidor es restringido
- Sesiones de corta duración (típicamente 1-24 horas)

**Amenazas principales:**
- XSS (Cross-Site Scripting)
- CSRF (Cross-Site Request Forgery)
- Man-in-the-Middle
- Session hijacking

**Por qué HS256 es suficiente:**
- La clave secreta **nunca sale del servidor**
- Tokens se generan y validan en el mismo lugar
- Mayor velocidad de verificación (importante para alta carga)
- Menor overhead computacional

### Dispositivos IoT (RS256)
**Contexto:**
- Dispositivos ESP32 físicamente desplegados en aulas
- Susceptibles a robo o manipulación física
- Firmware puede ser extraído mediante técnicas de hardware hacking
- Operan 24/7 en entornos no controlados

**Amenazas principales:**
- **Extracción física del firmware** (mayor riesgo)
- Clonación de dispositivos
- Inyección de tokens falsos
- Replay attacks

**Por qué RS256 es necesario:**
- El dispositivo **solo tiene la clave pública**
- Incluso si roban el ESP32 y extraen el firmware:
  - ✅ Pueden verificar tokens (lo cual está bien)
  - ❌ **NO pueden firmar tokens nuevos** (crítico)
- La clave privada permanece segura en el servidor
- Previene fabricación de tokens por dispositivos comprometidos

---

## 🏗️ Implementación Actual

### HS256 - Sesiones Web

**Archivo:** `Server/routers/auth.py`

```python
# Clave simétrica (solo en servidor)
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Características:**
- Clave simétrica de 256 bits
- Firma y verificación con la misma clave
- Tokens de corta/media duración
- Renovables mediante refresh

### RS256 - Dispositivos IoT

**Archivos:** `Server/services/jwt_device_service.py`, `Device_ESP32_app/auth_device_jwt.ino`

**Servidor** (clave privada):
```python
PRIVATE_KEY_PATH = "keys/jwt_private.pem"
PUBLIC_KEY_PATH = "keys/jwt_public.pem"

def create_device_token(device_id: str, aula_id: int):
    payload = {
        "device_id": device_id,
        "aula_id": aula_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=365)
    }
    return jwt.encode(payload, private_key, algorithm="RS256")
```

**Dispositivo ESP32** (solo clave pública):
```cpp
const char* jwt_public_key = R"(
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
)";

bool verifyToken(String token) {
    // Solo puede VERIFICAR, no FIRMAR
    return jwt.verify(token, jwt_public_key);
}
```

**Características:**
- Par de claves RSA 2048 bits
- Clave privada **nunca abandona el servidor**
- Dispositivo solo verifica, no genera
- Tokens de larga duración (1 año)

---

## 🛡️ Análisis de Seguridad

### Escenario 1: Robo de Dispositivo ESP32 ❌→✅

**Con HS256 (simétrico):**
```
Atacante extrae firmware → Encuentra SECRET_KEY
→ Puede firmar tokens para CUALQUIER dispositivo
→ SISTEMA COMPROMETIDO 💥
```

**Con RS256 (asimétrico):**
```
Atacante extrae firmware → Encuentra PUBLIC_KEY
→ Solo puede verificar tokens (operación normal)
→ NO puede firmar tokens falsos
→ Sistema sigue seguro ✅
```

### Escenario 2: Compromiso del Servidor 💥

**Ambos sistemas fallan:**
- Con servidor comprometido, extraen tanto SECRET_KEY como PRIVATE_KEY
- **Mitigación:** Rotación periódica de claves, monitoreo, hardening

### Escenario 3: Sesión Web Robada (Cookie Hijacking)

**Con HS256:**
- Token robado permite acceso hasta expiración
- **Mitigación:** 
  - Tokens de corta duración (8h)
  - HttpOnly + Secure cookies
  - HTTPS obligatorio
  - Detección de anomalías (cambio de IP)

---

## 📊 Comparativa Técnica

| Criterio | HS256 (Web) | RS256 (IoT) |
|----------|-------------|-------------|
| **Velocidad firma** | ⚡⚡⚡ Muy rápido | ⚡ Más lento |
| **Velocidad verificación** | ⚡⚡⚡ Muy rápido | ⚡⚡ Rápido |
| **Tamaño token** | 🟢 Pequeño (~150 bytes) | 🟡 Medio (~350 bytes) |
| **Seguridad física** | 🟡 Requiere servidor seguro | 🟢 Resistente a robo |
| **Complejidad** | 🟢 Simple | 🟡 Media |
| **Escalabilidad** | 🟡 Servidor centralizado | 🟢 Verificación distribuida |
| **Caso de uso** | ✅ Sesiones de confianza | ✅ Dispositivos no confiables |

---

## 🔧 Mejores Prácticas Implementadas

### 1. Separación de Claves ✅
- `SECRET_KEY` para web → Variable de entorno
- `jwt_private.pem` para dispositivos → Archivo protegido en servidor
- `jwt_public.pem` embebido en firmware ESP32

### 2. Duración de Tokens ✅
- **Web:** 8 horas (renovable)
- **Dispositivos:** 1 año (largo despliegue)

### 3. Protección de Claves ✅
```bash
# Permisos restrictivos en servidor
chmod 600 keys/jwt_private.pem
chmod 644 keys/jwt_public.pem
```

### 4. Variables de Entorno ✅
```bash
# .env
SECRET_KEY=tu-clave-super-secreta-de-256-bits-minimo
```

### 5. HTTPS + Cookies Seguras ✅
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,      # No accesible desde JavaScript
    secure=True,        # Solo HTTPS
    samesite="lax"      # Protección CSRF
)
```

---

## 🚀 Recomendaciones Futuras

### Corto Plazo (3-6 meses)
1. **Implementar rotación de SECRET_KEY**
   - Mecanismo de rolling keys
   - Gracia period para tokens antiguos

2. **Logging y monitoreo**
   - Alertas de intentos de token inválidos
   - Detección de patrones anómalos

3. **Revocación de tokens**
   - Lista negra de tokens comprometidos
   - Cache Redis para verificación rápida

### Medio Plazo (6-12 meses)
1. **Rotación de claves RSA**
   - Generar nuevo par de claves anualmente
   - Actualización OTA de dispositivos

2. **Dispositivos con Secure Element**
   - Chip ATECC608A para almacenar claves
   - Protección hardware contra extracción

3. **OAuth2/OIDC para Web**
   - Migrar a estándar OAuth2
   - Soporte para SSO institucional

---

## 📚 Referencias y Estándares

- **RFC 7519** - JSON Web Token (JWT)
- **RFC 7515** - JSON Web Signature (JWS)
- **OWASP JWT Cheat Sheet**
- **NIST SP 800-57** - Recommendation for Key Management

---

## ❓ FAQ

**P: ¿Por qué no usar RS256 para todo?**
R: HS256 es más rápido y suficiente cuando ambas partes (firma y verificación) están en el mismo servidor seguro. RS256 añade overhead innecesario.

**P: ¿Y si quiero unificar a RS256?**
R: Es posible, pero tendrás ~30% más latencia en validación de tokens web sin ganancia de seguridad real.

**P: ¿Los dispositivos pueden generar tokens con la clave pública?**
R: **NO**. La criptografía asimétrica solo permite firmar con la clave privada. La pública solo verifica.

**P: ¿Qué pasa si roban la PRIVATE_KEY del servidor?**
R: Sistema comprometido. Debes rotar inmediatamente ambas claves y revocar todos los tokens activos.

**P: ¿Tokens nunca expiran?**
R: Los de dispositivos duran 1 año, pero puedes implementar revocación manual vía lista negra o actualizaciones OTA.

---

**Autor:** Sistema de Control de Asistencia - UEx  
**Última actualización:** 16 de Febrero de 2026  
**Versión:** 2.0
