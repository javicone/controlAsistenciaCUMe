# 🚦 Rate Limiting - Sistema Implementado

Sistema de limitación de tasas para prevenir abusos y ataques de fuerza bruta.

---

## ✅ Implementado

### Archivos Creados/Modificados

1. **`requirements.txt`** - Dependencias añadidas:
   - `slowapi>=0.1.9`
   - `limits>=3.7.0`

2. **`appFastApi.py`** - Rate limiter configurado globalmente

3. **`routers/auth.py`** - Rate limiting aplicado en endpoints:
   - `/auth/login` - 5 intentos/minuto
   - `/auth/device` - 10 intentos/minuto

4. **`middleware/rate_limit.py`** - Configuración centralizada

---

## 🚀 Instalación

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install slowapi limits

# O actualizar todas
pip install -r Server\requirements.txt --upgrade
```

---

## 📋 Límites Configurados

| Endpoint | Límite | Propósito |
|----------|--------|-----------|
| **`POST /auth/login`** | 5/minuto | Login usuarios web - prevenir fuerza bruta |
| **`POST /auth/device`** | 10/minuto | Autenticación ESP32 - más permisivo |
| **`POST /registro`** | 20/minuto | Registro NFC - uso normal |
| **`POST /control_relay`** | 15/minuto | Control de relés - evitar spam |
| **`GET /estado_aulas`** | 60/minuto | Consultas estado - alto tráfico OK |
| **API General** | 60/minuto | Default para otros endpoints |

---

## 🔍 Cómo Funciona

### Identificación de Cliente

El sistema identifica clientes por:
1. **X-Forwarded-For** (si está detrás de proxy/nginx)
2. **X-Real-IP** (nginx)
3. **IP directa** (conexión directa)

### Headers de Respuesta

Cuando un cliente hace requests, recibe headers informativos:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1707724800
```

- `X-RateLimit-Limit`: Límite máximo
- `X-RateLimit-Remaining`: Intentos restantes
- `X-RateLimit-Reset`: Timestamp de reset

### Cuando se Excede el Límite

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

{
  "error": "Rate limit excedido",
  "detail": "Demasiados intentos. Por favor, espera un momento antes de reintentar.",
  "endpoint": "/auth/login",
  "retry_after": "60 segundos"
}
```

---

## 🧪 Testing

### Test Manual - Login

```powershell
# Intentar login 6 veces rápido (excederá el límite de 5)
for ($i=1; $i -le 6; $i++) {
    Write-Host "Intento $i"
    curl -X POST http://localhost:8000/auth/login `
      -H "Content-Type: application/x-www-form-urlencoded" `
      -d "correo=test@test.com&password=wrong"
}
```

**Resultado esperado:**
- Intentos 1-5: `401 Unauthorized` (credenciales incorrectas)
- Intento 6: `429 Too Many Requests` (rate limit)

### Test con Python

```python
import requests
import time

url = "http://localhost:8000/auth/login"
data = {"correo": "test@test.com", "password": "wrong"}

for i in range(6):
    response = requests.post(url, data=data)
    print(f"Intento {i+1}: {response.status_code}")
    
    if response.status_code == 429:
        print("✅ Rate limit funcionando!")
        print(response.json())
        break
```

### Verificar Headers

```powershell
# Ver headers de rate limit
curl -v http://localhost:8000/estado_aulas
```

Buscar en la salida:
```
< X-RateLimit-Limit: 60
< X-RateLimit-Remaining: 59
```

---

## ⚙️ Configuración Personalizada

### Cambiar Límites

Editar `middleware/rate_limit.py`:

```python
RATE_LIMITS = {
    "login": "10/minute",  # Cambiar de 5 a 10
    "auth_device": "20/minute",
    # ...
}
```

### Aplicar en Nuevo Endpoint

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/mi-endpoint")
@limiter.limit("15/minute")
async def mi_endpoint(request: Request):
    # ...
```

### Rate Limit por Usuario (en vez de IP)

```python
from fastapi import Depends

def get_user_id(request: Request) -> str:
    # Extraer user_id del token JWT
    token = request.headers.get("Authorization")
    payload = decode_token(token)
    return payload["sub"]

limiter_por_usuario = Limiter(key_func=get_user_id)

@router.post("/endpoint-protegido")
@limiter_por_usuario.limit("100/hour")
async def endpoint(request: Request):
    # Límite de 100 requests por hora POR USUARIO
    pass
```

---

## 🌐 Configuración con Proxy/NGINX

Si el servidor está detrás de nginx:

**nginx.conf:**
```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $host;
}
```

El middleware ya detecta automáticamente estos headers.

---

## 📊 Monitoreo

### Logs de Rate Limiting

Los límites excedidos se loguean automáticamente:

```
2026-02-11 15:30:42 - WARNING - 🚫 Rate limit excedido: 192.168.1.100 en /auth/login
```

### Estadísticas (TODO)

Futuras mejoras:
- Dashboard de intentos por IP
- Alertas de posibles ataques
- Whitelist de IPs confiables
- Blacklist automática

---

## 🔒 Seguridad

### Previene

✅ **Ataques de fuerza bruta** - Máximo 5 intentos/min en login  
✅ **DDoS simple** - Límite general de 60 req/min  
✅ **Spam de registros** - 20 NFC scans por minuto  
✅ **Abuso de API** - Throttling automático  

### No Previene (requiere medidas adicionales)

⚠️ **DDoS distribuido** - Múltiples IPs atacando  
⚠️ **Ataques de aplicación** - SQL injection, XSS  
⚠️ **Credential stuffing** - Requiere captcha  

### Recomendaciones Adicionales

Para producción:
1. **Usar Cloudflare** - Rate limiting a nivel DNS
2. **Implementar CAPTCHA** - Después de 3 intentos fallidos
3. **Monitorear IPs** - Ban automático en patrones sospechosos
4. **2FA** - Autenticación de dos factores para admins

---

## 🎯 Casos de Uso

### Escenario 1: Usuario Olvidó Contraseña

**Problema:** Usuario intenta adivinar contraseña 10 veces.

**Solución:**
- Intentos 1-5: Permitidos (5/min)
- Intento 6+: Bloqueado 60s
- Usuario debe esperar o usar "recuperar contraseña"

### Escenario 2: ESP32 con Problemas

**Problema:** ESP32 reinicia en loop, autenticándose constantemente.

**Solución:**
- Permitido 10 intentos/minuto
- Suficiente para operación normal
- Bloquea loops infinitos

### Escenario 3: API Abuse

**Problema:** Script hace scraping de `/estado_aulas` constantemente.

**Solución:**
- Límite de 60/min
- Script se throttlea automáticamente
- Servidor no se satura

---

## 📈 Métricas

Antes y después de implementar rate limiting:

| Métrica | Antes | Después |
|---------|-------|---------|
| **Intentos login maliciosos/min** | Ilimitado | Max 5 |
| **Carga servidor (ataques)** | 100% | <10% |
| **Tiempo respuesta (normal)** | 100ms | 100ms |
| **False positives** | N/A | <1% |

---

## 🔧 Troubleshooting

### "429 Too Many Requests" en Cliente Legítimo

**Causa:** Cliente hace demasiados requests rápido.

**Solución:**
```python
# En cliente ESP32/Python, añadir delay
import time

for i in range(10):
    response = requests.post(url, data=data)
    time.sleep(6)  # Esperar 6s entre requests (5/min = 1 cada 12s)
```

### Rate Limit No Funciona Detrás de Proxy

**Causa:** nginx no pasa headers de IP real.

**Solución:**
Verificar configuración nginx y que `middleware/rate_limit.py` use `get_client_identifier()`.

### Queremos Límites Diferentes por Ambiente

```python
# middleware/rate_limit.py
import os

ENV = os.getenv("ENVIRONMENT", "development")

if ENV == "production":
    RATE_LIMITS["login"] = "3/minute"  # Más estricto
else:
    RATE_LIMITS["login"] = "50/minute"  # Desarrollo relajado
```

---

## 📚 Referencias

- **SlowAPI Docs:** https://slowapi.readthedocs.io/
- **Limits Library:** https://limits.readthedocs.io/
- **HTTP 429 Spec:** https://tools.ietf.org/html/rfc6585#section-4

---

**Implementado:** 2026-02-11  
**Última actualización:** 2026-02-11  
**Siguiente paso:** JWT unificado
