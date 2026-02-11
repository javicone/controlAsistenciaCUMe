# Frontend Review — Control de Asistencia UEx

**Fecha:** 2026-02-11  
**Evaluado con:** Frontend Design Skill  
**Alcance:** 6 templates HTML, 3 CSS, 3 JS

---

## Puntuación General: 5.2 / 10

| Categoría | Nota |
|-----------|------|
| Coherencia Visual & Identidad | 4.0/10 |
| Tipografía | 3.5/10 |
| Paleta de Color | 5.0/10 |
| Animaciones & Micro-interacciones | 4.5/10 |
| Composición Espacial | 6.0/10 |
| Calidad del JavaScript | 4.5/10 |
| Seguridad Frontend (XSS) | 3.0/10 |
| Mantenibilidad del Código | 4.0/10 |
| Responsive Design | 6.5/10 |
| Accesibilidad (a11y) | 5.0/10 |

---

## 🎨 PARTE 1: DISEÑO Y UX

### D1. 🔴 Tres Identidades Visuales Diferentes

El proyecto tiene **tres paletas de color completamente distintas** que rompen la coherencia:

| Página | Paleta | Fuente |
|--------|--------|--------|
| Login + Profesor | `#005942` verde UEx | system-ui stack |
| Administrador | `#667eea → #764ba2` gradiente púrpura | Segoe UI |
| Conserjes + Dashboard | `#28a745` / `#dc3545` Bootstrap | Arial, sans-serif |

**Impacto:** Un usuario que navega de login → admin → conserje siente que está en 3 aplicaciones distintas. No hay identidad institucional unificada.

**Recomendación:** Todas las páginas deberían usar la paleta UEx (`#005942` verde institucional) como base.

---

### D2. 🔴 Gradiente Púrpura en Administrador = Estética AI Genérica

```css
/* administrador.css */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

La skill de frontend-design marca explícitamente los **"purple gradients on white backgrounds"** como cliché de diseño AI. Es la combinación más común que genera cualquier herramienta automatizada.

**Recomendación:** Sustituir por el verde institucional UEx:
```css
background: linear-gradient(135deg, #005942 0%, #003d2e 50%, #001f17 100%);
```

---

### D3. 🔴 Tipografía Genérica en Todas las Páginas

La skill dice: *"Avoid generic fonts like Arial and Inter"*. Sin embargo:

- `styles.css` usa **Arial, sans-serif** — la fuente más genérica posible
- `administrador.css` usa **Segoe UI, Tahoma** — fuentes de sistema
- `login.css` usa **-apple-system, BlinkMacSystemFont** — stack de sistema

Ninguna página tiene una elección tipográfica con personalidad.

**Recomendación:** Usar Google Fonts con identidad propia:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```
```css
body { font-family: 'DM Sans', sans-serif; }
code, .device-id { font-family: 'JetBrains Mono', monospace; }
```

---

### D4. 🟡 Exceso de Inline Styles en `administrador.html`

Hay **~80 líneas de CSS inline** en el HTML del administrador (sección de sensores, diagnóstico, relés). Ejemplos:

```html
<div class="sensor-item" style="background: #f8f9fa; padding: 10px; border-radius: 8px;">
    <span style="font-size: 0.85em; color: #666;">🌡️ Temperatura</span>
    <div id="sensor-temp" style="font-size: 1.1em; font-weight: 600; color: #333;">N/A</div>
</div>
```

Esto está repetido para 5 sensores, 4 estados de diagnóstico, 2 relés y 3 métricas del sistema. Debería estar en `administrador.css`.

---

### D5. 🟡 Sin Animaciones de Entrada en Ninguna Página

La skill dice: *"One well-orchestrated page load with staggered reveals creates more delight than scattered micro-interactions."*

Actualmente solo hay:
- `translateY(-2px)` en hover del botón login (mínimo)
- `slideIn` para notificaciones del admin (correcto)
- **Nada** en conserjes ni dashboard

**Recomendación:** Añadir animación de entrada escalonada:
```css
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
.aula-card {
    animation: fadeUp 0.4s ease both;
}
.aula-card:nth-child(1) { animation-delay: 0.05s; }
.aula-card:nth-child(2) { animation-delay: 0.10s; }
.aula-card:nth-child(3) { animation-delay: 0.15s; }
```

---

### D6. 🟡 Panel de Conserjes Tiene Estilos Inline + Duplicados

`conserjes.html` duplica estilos que ya existen en `styles.css` dentro de un `<style>` en el `<head>`:

```html
<style>
    .status-connected { color: #28a745; ... }  /* Ya está en administrador.css */
    .button { padding: 10px 20px; ... }         /* Ya está en styles.css */
    #panel { display: grid; ... }               /* Debería estar en su propio CSS */
</style>
```

**Recomendación:** Crear `conserjes.css` con los estilos específicos.

---

### D7. 🟢 Login y Profesor — Buen Diseño Contextual

La página de login y la de `asistencias_profesor.html` tienen el **mejor diseño de todo el proyecto**:
- Fondo con foto real del Centro Universitario de Mérida
- `backdrop-filter: blur(12px)` para glass-morphism
- Variables CSS con naming en español (`--uex-verde`)
- Cards de fichajes con SVG icons bien integrados
- Estadísticas mensuales con gradiente verde institucional

Esto debería ser el **modelo a seguir** para unificar el resto de páginas.

---

## 💻 PARTE 2: REVISIÓN DEL JAVASCRIPT

### JS1. 🔴 XSS vía `.innerHTML` con Datos No Sanitizados

**Archivos:** `administrador.js`, `conserjes.js`, `dashboard.html`

Los tres archivos inyectan datos del servidor directamente en HTML sin sanitizar:

```javascript
// administrador.js — renderAulas()
card.innerHTML = `
    <span class="aula-name">${aulaKey}</span>        // ← aulaKey del servidor
    <span>${aula.device_id || 'N/A'}</span>          // ← device_id del servidor
`;

// conserjes.js — renderAulas()
aulaDiv.innerHTML = `<h3>${aulaName}</h3>...`;        // ← mismo problema

// dashboard.html
output += `<li>${asistencia.usuario_id} - ${asistencia.aula_id}</li>`;
```

**Impacto:** Si un nombre de aula contiene `<script>alert('xss')</script>`, se ejecutará en el navegador de todos los clientes conectados por WebSocket.

**Recomendación:** Sanitizar antes de inyectar:
```javascript
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// Uso:
card.innerHTML = `<span class="aula-name">${escapeHTML(aulaKey)}</span>`;
```

O mejor aún, usar `textContent` para texto y `createElement` para estructura.

---

### JS2. 🔴 `JSON.parse()` Sin Try/Catch

**Archivos:** `administrador.js:28`, `conserjes.js:28`

```javascript
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);  // 💥 Crash si el mensaje no es JSON válido
```

Un mensaje malformado del servidor o un error de red que corte un paquete causaría una excepción no manejada, matando el handler del WebSocket.

**Fix:**
```javascript
ws.onmessage = (event) => {
    let msg;
    try {
        msg = JSON.parse(event.data);
    } catch (e) {
        console.error('❌ JSON inválido:', event.data);
        return;
    }
    // ... switch(msg.tipo)
};
```

---

### JS3. 🔴 Inyección de Código vía `onclick` con Interpolación

**Archivo:** `conserjes.js` — `renderAulas()`

```javascript
aulaDiv.innerHTML = `
    <button onclick="cambiarRelay('${aulaName}', 1, ${!relay1State})">
        ${relay1State ? 'Apagar' : 'Encender'} Calefacción
    </button>
`;
```

Si `aulaName` contiene `'); alert('xss'); ('`, se ejecuta código arbitrario. Nunca usar interpolación de strings en atributos `onclick`.

**Fix:** Usar `addEventListener` en lugar de `onclick`:
```javascript
const btn = document.createElement('button');
btn.textContent = relay1State ? 'Apagar' : 'Encender';
btn.addEventListener('click', () => cambiarRelay(aulaName, 1, !relay1State));
aulaDiv.appendChild(btn);
```

---

### JS4. 🟡 Duplicación Masiva de Código entre Admin y Conserje

Funciones **idénticas o casi idénticas** en `administrador.js` y `conserjes.js`:

| Función | admin.js | conserjes.js | Diferencia |
|---------|----------|-------------|------------|
| `connectWebSocket()` | ✅ | ✅ | Solo endpoint (`/ws/admin` vs `/ws/conserje`) |
| `updateConnectionStatus()` | ✅ | ✅ | Idéntica |
| `actualizarAulaEnTiempoReal()` | ✅ | ✅ | ~90% idéntica |
| `actualizarRelayEnUI()` | ✅ | ✅ | ~95% idéntica |
| `renderAulas()` | ✅ | ✅ | Template diferente, lógica igual |
| `cerrarSesion()` | ✅ | ✅ | Idéntica, copiada carácter por carácter |
| Conversión `aulas_estado` | ✅ (3×) | ✅ (3×) | Mismo loop copiado 6 veces en total |

**Impacto:** 6 copias del mismo loop de conversión. Si cambia el formato del servidor, hay que corregir 6 sitios.

**Recomendación:** Crear `ws-common.js` con las funciones compartidas:
```javascript
// static/js/ws-common.js
export function convertirAulasEstado(aulasEstado) { ... }
export function connectWebSocket(role, onMessage) { ... }
export function cerrarSesion(ws) { ... }
export function updateConnectionStatus(connected) { ... }
export function escapeHTML(str) { ... }
```

---

### JS5. 🟡 `cerrarSesion()` vs `logout()` — Tres Implementaciones Diferentes

| Archivo | Función | Limpia storage | Llama /logout | Cierra WS |
|---------|---------|----------------|---------------|-----------|
| `administrador.js` | `cerrarSesion()` | ✅ | ✅ fetch | ✅ |
| `conserjes.js` | `cerrarSesion()` | ✅ | ✅ fetch | ✅ |
| `asistencias_profesor.html` | `logout()` | ✅ clear | ❌ Redirige directo | ❌ |
| `dashboard.html` | `logout()` | Solo token | ❌ Redirige directo | ❌ |

La función de profesor NO llama al endpoint `/logout` del servidor, así que la cookie del JWT no se invalida — la sesión permanece activa.

---

### JS6. 🟡 WebSocket Reconecta Sin Backoff Exponencial

```javascript
ws.onclose = () => {
    setTimeout(connectWebSocket, 5000); // Siempre 5 segundos, para siempre
};
```

Si el servidor está caído, esto genera una conexión fallida cada 5 segundos indefinidamente.

**Recomendación:**
```javascript
let reconnectDelay = 1000;
const MAX_DELAY = 30000;

ws.onclose = () => {
    updateConnectionStatus(false);
    setTimeout(() => {
        connectWebSocket();
        reconnectDelay = Math.min(reconnectDelay * 2, MAX_DELAY);
    }, reconnectDelay);
};

ws.onopen = () => {
    reconnectDelay = 1000; // Reset on success
};
```

---

### JS7. 🟡 `innerHTML +=` en Loop — Performance DOM

**Archivo:** `asistencias_profesor.html`

```javascript
fichajesOrdenados.forEach(fichaje => {
    fichajesContainer.innerHTML += cardHTML;  // Re-parsea TODO el HTML en cada iteración
});
```

Con 50 fichajes, el navegador parsea HTML 50 veces, cada vez con más contenido. Con 100+, se nota el lag.

**Fix:**
```javascript
const fragment = document.createDocumentFragment();
fichajesOrdenados.forEach(fichaje => {
    const card = document.createElement('div');
    card.className = 'fichaje-card';
    card.innerHTML = cardInnerHTML;  // Solo el interior, una vez
    fragment.appendChild(card);
});
fichajesContainer.appendChild(fragment);  // Un solo DOM write
```

---

### JS8. 🟡 Doble `DOMContentLoaded` en Conserjes

**Archivo:** `conserjes.js:282-292`

```javascript
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    btnActualizar.addEventListener('click', actualizarLista);
});
document.addEventListener('DOMContentLoaded', () => {   // ← SEGUNDO listener
    const btnLogout = document.getElementById('btn-logout');
    // ...
});
```

Funciona, pero evidencia código añadido a posteriori sin integrar.

---

### JS9. 🟡 `alert()` en Conserjes vs Notificaciones en Admin

`conserjes.js` usa `alert()` nativo para errores:
```javascript
alert('WebSocket no conectado');     // conserjes.js
alert('Error: ' + msg.mensaje);      // conserjes.js
```

Mientras que `administrador.js` tiene un sistema de notificaciones toast bien hecho. El conserje debería usar el mismo sistema.

---

### JS10. 🟡 `dashboard.html` Parece Obsoleto

```javascript
// dashboard.html
const token = localStorage.getItem("token");
fetch("/asistencias", {
    headers: { "Authorization": `Bearer ${localStorage.getItem("token")}` }
})
.then(response => response.json())  // Sin .ok check
.then(data => { ... });             // Sin .catch()
```

Este template:
- Usa `localStorage.getItem("token")` pero el sistema ahora usa cookies httpOnly
- No tiene `.catch()` en el fetch
- No verifica `response.ok`
- Parece un vestigio de la versión anterior que ya no funciona con el backend actual

---

### JS11. 🟢 `refrescarSensores` Usa Clave `tipo` en vez de `action`

```javascript
// administrador.js — refrescarSensores()
const mensaje = {
    tipo: 'solicitar_estado',    // ← Usa 'tipo'
    timestamp: Date.now()
};

// Pero TODOS los demás comandos admin usan:
const mensaje = {
    action: 'toggle_relay',      // ← Usa 'action'
    device_id: ...
};
```

Inconsistencia en el formato de mensajes. Podría fallar silenciosamente si el servidor espera `action`.

---

## 📐 Resumen de Problemas por Severidad

### 🔴 Críticos (Fix antes de producción)
1. **XSS via innerHTML** — 3 archivos afectados
2. **JSON.parse sin try/catch** — WebSocket se rompe con JSON malformado
3. **onclick con interpolación string** — código inyectable
4. **3 paletas de color incompatibles** — falta identidad visual

### 🟡 Importantes (Fix en 1-2 sprints)
5. Código duplicado masivo (~300 líneas repetidas)
6. `logout()` del profesor no invalida cookie servidor
7. Reconexión WebSocket sin backoff
8. `innerHTML +=` en loop de fichajes
9. `alert()` en conserjes en vez de notificaciones
10. `dashboard.html` obsoleto (usa localStorage tokens)
11. Inline styles masivos en administrador.html

### 🟢 Menores
12. Doble `DOMContentLoaded` en conserjes
13. Magic numbers sin constantes
14. Inconsistencia `tipo` vs `action` en mensajes WS

---

## 🎯 Plan de Acción

### Fase 1: Unificar Identidad Visual
1. Crear `static/css/variables.css` con la paleta UEx unificada
2. Eliminar el gradiente púrpura del admin, usar verde institucional
3. Importar Google Font con personalidad (DM Sans, Outfit, o similar)
4. Mover los inline styles de `administrador.html` a `administrador.css`
5. Crear `conserjes.css` para los estilos que están en `<style>` inline

### Fase 2: Segurizar el JavaScript
6. Crear función `escapeHTML()` y usarla en TODOS los innerHTML
7. O migrar a `textContent` + `createElement`
8. Añadir `try/catch` a todos los `JSON.parse()`
9. Eliminar `onclick` con interpolación en conserjes
10. Unificar `logout()` para que siempre llame a `/logout`

### Fase 3: Refactorizar JS
11. Crear `static/js/ws-common.js` con código compartido
12. Implementar backoff exponencial en reconexión WS
13. Usar `DocumentFragment` en loops de renderizado
14. Decidir si `dashboard.html` se elimina o se actualiza
15. Añadir sistema de notificaciones toast a conserjes

### Fase 4: Elevar el Diseño
16. Añadir animaciones de entrada escalonadas
17. Transiciones suaves en cambios de estado de sensores
18. Indicadores LED animados para estado de conexión
19. Dark mode toggle (CSS variables ya preparadas)
