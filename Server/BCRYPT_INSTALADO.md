# 🔐 Sistema de Verificación de Contraseñas - Instalado

## ✅ Archivos Creados

1. **`security/password.py`** - Módulo de hashing con bcrypt
2. **`scripts/migrate_passwords.py`** - Script de migración de contraseñas existentes
3. **`scripts/create_user.py`** - Utilidad para crear usuarios con contraseñas hasheadas

## 🚀 Pasos para Activar

### 1. Instalar Dependencia

```powershell
# Activar entorno virtual primero
.\.venv\Scripts\Activate.ps1

# Instalar passlib con soporte bcrypt
pip install passlib[bcrypt]
```

### 2. Vista Previa de la Migración (Opcional)

Antes de migrar, puedes ver qué usuarios serían afectados:

```powershell
python Server\scripts\migrate_passwords.py --preview
```

Esto mostrará:
- Cuántos usuarios tienen contraseñas en texto plano
- Cuántos ya tienen bcrypt
- Lista de usuarios a migrar

### 3. Hacer Backup de la Base de Datos

**⚠️ MUY IMPORTANTE - No saltar este paso**

```powershell
# Opción A: Backup con mysqldump
mysqldump -u root -p control-asistencia > backup_antes_bcrypt.sql

# Opción B: Backup desde Docker
docker exec control-asistencia-mysql mysqldump -u root -p1234 control-asistencia > backup_antes_bcrypt.sql
```

### 4. Ejecutar la Migración

```powershell
python Server\scripts\migrate_passwords.py
```

El script te pedirá confirmación dos veces:
1. Confirmación inicial (escribir "SI")
2. Confirmación antes de hashear (escribir "HASHEAR")

**Ejemplo de salida:**
```
🔐 MIGRACIÓN DE CONTRASEÑAS A BCRYPT
======================================================================

⚠️  ADVERTENCIAS:
   - Este script modificará la tabla 'usuarios'
   - Las contraseñas en texto plano serán reemplazadas por hashes bcrypt
   ...

📊 Estado actual:
   ✅ Ya hasheadas:  0 usuarios
   🔄 Por hashear:   15 usuarios
   📈 Total:         15 usuarios

🔒 Hasheando 15 contraseñas...
   ✅ 1/15 - admin@uex.es
   ✅ 2/15 - profesor1@uex.es
   ...

🎉 MIGRACIÓN COMPLETADA
```

### 5. Verificar Login

Después de la migración, probar login:

```powershell
# Desde navegador
http://localhost:8000

# O con curl
curl -X POST http://localhost:8000/login `
  -H "Content-Type: application/json" `
  -d '{\"correo\":\"admin@uex.es\",\"contraseña\":\"Admin123!\"}'
```

## 🔍 Cómo Funciona

### Antes (Inseguro ❌)
```python
# services/auth_service.py (versión antigua)
if user["password"] != password:  # Comparación directa
    raise HTTPException(...)
```

**Problemas:**
- Contraseñas visibles en BD
- Si se filtra la BD, todas las contraseñas están expuestas
- No hay protección adicional

### Después (Seguro ✅)
```python
# services/auth_service.py (versión nueva)
from security.password import verify_password

if not verify_password(password, user["password"]):
    raise HTTPException(...)
```

**Mejoras:**
- Contraseñas hasheadas con bcrypt (12 rounds)
- Hash diferente cada vez (salt automático)
- Resistente a timing attacks
- Incluso con acceso a BD, imposible obtener contraseñas originales

### Ejemplo de Hash

```
Contraseña original:  "MiContraseña123!"
Hash bcrypt:          "$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdI17lhWy"
                       │  │  │                                                          
                       │  │  └─ Salt (aleatorio, único)
                       │  └──── Rounds (12 = 2^12 = 4096 iteraciones)
                       └─────── Algoritmo (bcrypt versión 2b)
```

## 🛡️ Compatibilidad Durante Migración

El código tiene **retrocompatibilidad temporal**:

```python
# Si la contraseña YA está hasheada
if is_hashed(stored_password):
    verify_password(password, stored_password)  # ✅ Bcrypt
else:
    # ⚠️ Texto plano (solo durante migración)
    stored_password == password
```

Esto permite:
- ✅ Usuarios migrados pueden loguearse inmediatamente
- ✅ Usuarios no migrados siguen funcionando (temporal)
- ✅ Migración gradual si es necesario
- ✅ Cero downtime

## 📊 Crear Nuevos Usuarios

Para crear usuarios nuevos con contraseñas ya hasheadas:

```powershell
python Server\scripts\create_user.py
```

O editarlo para crear usuarios específicos:

```python
# En create_user.py
asyncio.run(create_user(
    nombre="Juan Pérez",
    correo="juan.perez@uex.es",
    password="Contraseña123!",
    rol="profesor"
))
```

## 🧪 Testing

### Test Manual

```python
from security.password import hash_password, verify_password

# Hashear
hashed = hash_password("MiContraseña123!")
print(hashed)  # $2b$12$...

# Verificar correcta
verify_password("MiContraseña123!", hashed)  # True

# Verificar incorrecta
verify_password("OtraContraseña", hashed)    # False
```

### Test con Usuario Real

1. Crear usuario de prueba:
```sql
INSERT INTO usuarios (nombre, correo, password, rol)
VALUES ('Test User', 'test@test.com', '$2b$12$...', 'profesor');
```

2. Intentar login desde el navegador con esas credenciales

## 🔄 Rollback (Si algo sale mal)

Si necesitas volver atrás:

```powershell
# Restaurar desde backup
mysql -u root -p control-asistencia < backup_antes_bcrypt.sql

# O desde Docker
cat backup_antes_bcrypt.sql | docker exec -i control-asistencia-mysql mysql -u root -p1234 control-asistencia
```

## 📈 Próximos Pasos

Después de implementar bcrypt:

- [ ] ✅ Contraseñas seguras
- [ ] ⬜ Rate limiting en login (5 intentos/minuto)
- [ ] ⬜ JWT unificado (HS256 o RS256)
- [ ] ⬜ Validación de inputs con Pydantic
- [ ] ⬜ Logs de intentos fallidos
- [ ] ⬜ Sistema de recuperación de contraseña

## ⚠️ Notas Importantes

1. **No ejecutar dos veces** - El script detecta contraseñas ya hasheadas
2. **Backup obligatorio** - Siempre hacer backup antes de migrar
3. **Testing en dev primero** - Probar en desarrollo antes de producción
4. **No compartir hashes** - Los hashes siguen siendo información sensible
5. **Logging seguro** - Nunca loguear contraseñas (ni en texto plano ni hasheadas)

## 📞 Troubleshooting

### Error: "No module named 'passlib'"
```powershell
pip install passlib[bcrypt]
```

### Error: "Can't connect to MySQL"
```powershell
# Verificar que Docker está corriendo
docker ps

# Iniciar contenedor si está detenido
docker start control-asistencia-mysql
```

### Login falla después de migración
1. Verificar que la contraseña fue hasheada:
```sql
SELECT correo, LEFT(password, 10) as password_prefix FROM usuarios;
-- Debe mostrar: $2b$12$...
```

2. Verificar logs del servidor:
```
✅ Login exitoso (bcrypt): usuario@email.com
```

---

**Implementado el:** 2026-02-11  
**Última actualización:** 2026-02-11
