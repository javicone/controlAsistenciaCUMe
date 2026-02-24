// ================================================================
// CONSERJES — Panel de Control de Aulas
// WebSocket connection + real-time room management
// ================================================================

// ========================================
// GLOBAL STATE
// ========================================

let aulasData = {};
let ws = null;

// ========================================
// WEBSOCKET — CONNECTION & HANDLING
// ========================================

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/conserje`;

    console.log('🔌 Conectando a:', wsUrl);
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket conectado (Conserje)');
        updateConnectionStatus(true);
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log('📩 Mensaje:', msg);

        switch (msg.tipo) {
            case 'error':
                console.error('❌ Error:', msg.mensaje);
                alert('Error: ' + msg.mensaje);
                if (msg.mensaje.includes('autenticado') || msg.mensaje.includes('autorizado') || msg.mensaje.includes('Token')) {
                    setTimeout(() => { window.location.href = '/'; }, 2000);
                }
                break;

            case 'conserje_bienvenida':
                updateDeviceCount(msg.dispositivos_conectados || 0);
                aulasData = {};
                if (msg.aulas_estado) {
                    Object.keys(msg.aulas_estado).forEach(deviceId => {
                        const aulaData = msg.aulas_estado[deviceId];
                        const aulaNombre = aulaData.aula || aulaData.nombre || deviceId;
                        aulasData[aulaNombre] = { ...aulaData, device_id: deviceId };
                    });
                }
                renderAulas();
                break;

            case 'comando_enviado':
                console.log(`✅ Comando ${msg.accion} enviado a ${msg.aula}`);
                break;

            case 'actualizacion_aula':
                actualizarAulaEnTiempoReal(msg);
                break;

            case 'confirmacion_relay':
                console.log(`✅ Relé confirmado: ${msg.aula} relay${msg.relay_num}=${msg.relay_state}`);
                actualizarRelayEnUI(msg.aula, msg.relay_num, msg.relay_state);
                break;

            case 'lista_dispositivos':
                updateDeviceCount(msg.dispositivos_conectados || 0);
                aulasData = {};
                if (msg.aulas_estado) {
                    Object.keys(msg.aulas_estado).forEach(deviceId => {
                        const aulaData = msg.aulas_estado[deviceId];
                        const aulaNombre = aulaData.aula || aulaData.nombre || deviceId;
                        aulasData[aulaNombre] = { ...aulaData, device_id: deviceId };
                    });
                }
                renderAulas();
                break;
        }
    };

    ws.onerror = (error) => {
        console.error('❌ Error WebSocket:', error);
        updateConnectionStatus(false);
    };

    ws.onclose = () => {
        console.log('❌ WebSocket cerrado');
        updateConnectionStatus(false);
        setTimeout(connectWebSocket, 5000);
    };
}

// ========================================
// UI STATUS UPDATES
// ========================================

function updateConnectionStatus(connected) {
    const el = document.getElementById('ws-status');
    if (!el) return;

    if (connected) {
        el.innerHTML = '<i class="bi bi-circle-fill"></i> Conectado';
        el.className = 'ws-badge ws-badge--on';
    } else {
        el.innerHTML = '<i class="bi bi-circle-fill"></i> Desconectado';
        el.className = 'ws-badge ws-badge--off';
    }
}

function updateDeviceCount(count) {
    const el = document.getElementById('device-count-text');
    if (el) {
        el.textContent = `${count} dispositivo${count !== 1 ? 's' : ''}`;
    }
}

// ========================================
// WEBSOCKET ACTIONS
// ========================================

function cambiarRelay(aulaName, relayNum, nuevoEstado) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket no conectado');
        return false;
    }

    const mensaje = {
        action: 'toggle_relay',
        aula: aulaName,
        relay_num: relayNum,
        relay_state: nuevoEstado
    };

    ws.send(JSON.stringify(mensaje));
    console.log('📤 Comando toggle_relay enviado:', mensaje);
    return true;
}

function actualizarLista() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket no conectado');
        return;
    }
    ws.send(JSON.stringify({ action: 'listar_dispositivos' }));
    console.log('📤 Solicitando lista de dispositivos...');
}

// ========================================
// STATE UPDATES
// ========================================

function actualizarRelayEnUI(aulaKey, relayNum, relayState) {
    if (aulasData[aulaKey]) {
        if (relayNum === 1) aulasData[aulaKey].relay1 = relayState;
        if (relayNum === 2) aulasData[aulaKey].relay2 = relayState;
        console.log(`🔄 UI actualizada: ${aulaKey} relay${relayNum}=${relayState}`);
        renderAulas();
    } else {
        console.warn(`⚠️ Aula '${aulaKey}' no encontrada en aulasData`);
    }
}

function actualizarAulaEnTiempoReal(msg) {
    const aulaKey = msg.aula;
    if (!aulasData[aulaKey]) aulasData[aulaKey] = {};

    const fields = ['temperatura', 'humedad', 'luz', 'personas', 'estado', 'relay1', 'relay2', 'clase_en_curso', 'presion'];
    fields.forEach(f => {
        if (msg[f] !== undefined) aulasData[aulaKey][f] = msg[f];
    });

    console.log(`🔄 Aula actualizada en tiempo real: ${aulaKey}`);
    renderAulas();
}

// ========================================
// RENDER — Room Cards
// ========================================

function renderAulas() {
    const panel = document.getElementById('panel');
    if (!panel) return;

    const keys = Object.keys(aulasData);

    if (keys.length === 0) {
        panel.innerHTML = `
            <div class="panel-empty">
                <i class="bi bi-router"></i>
                <h3>Sin dispositivos conectados</h3>
                <p>Los dispositivos ESP32 aparecerán aquí cuando se conecten</p>
            </div>`;
        return;
    }

    panel.innerHTML = '';

    keys.forEach((aulaKey, index) => {
        const aula = aulasData[aulaKey];
        const name = aula.nombre || aula.aula || aulaKey;
        const escapedName = name.replace(/'/g, "\\'");

        // Sensor values with fallbacks
        const temp     = aula.temperatura !== undefined ? `${aula.temperatura}°C` : '—';
        const humedad  = aula.humedad     !== undefined ? `${aula.humedad}%`      : '—';
        const luz      = aula.luz         !== undefined ? `${aula.luz} lux`       : '—';
        const presion  = aula.presion     !== undefined ? `${aula.presion} hPa`   : '—';
        const personas = aula.personas    !== undefined ? `${aula.personas}`      : '—';

        const claseEnCurso = aula.clase_en_curso || false;
        const relay1 = aula.relay1 || false;
        const relay2 = aula.relay2 || false;

        const delay = Math.min(index * 0.06, 0.35);

        const card = document.createElement('article');
        card.className = 'room-card';
        card.style.animationDelay = `${delay}s`;

        card.innerHTML = `
            <div class="room-card__header">
                <h3 class="room-card__name">${name}</h3>
                <span class="room-card__badge room-card__badge--${claseEnCurso ? 'active' : 'inactive'}">
                    ${claseEnCurso ? '<i class="bi bi-mortarboard"></i> Clase en curso' : 'Sin clase'}
                </span>
            </div>

            <div class="room-card__sensors">
                <div class="sensor">
                    <div class="sensor__icon"><i class="bi bi-thermometer-half"></i></div>
                    <div class="sensor__data">
                        <span class="sensor__value">${temp}</span>
                        <span class="sensor__label">Temp</span>
                    </div>
                </div>
                <div class="sensor">
                    <div class="sensor__icon"><i class="bi bi-droplet-half"></i></div>
                    <div class="sensor__data">
                        <span class="sensor__value">${humedad}</span>
                        <span class="sensor__label">Humedad</span>
                    </div>
                </div>
                <div class="sensor">
                    <div class="sensor__icon"><i class="bi bi-sun"></i></div>
                    <div class="sensor__data">
                        <span class="sensor__value">${luz}</span>
                        <span class="sensor__label">Luz</span>
                    </div>
                </div>
                <div class="sensor">
                    <div class="sensor__icon"><i class="bi bi-speedometer2"></i></div>
                    <div class="sensor__data">
                        <span class="sensor__value">${presion}</span>
                        <span class="sensor__label">Presión</span>
                    </div>
                </div>
                <div class="sensor">
                    <div class="sensor__icon"><i class="bi bi-people"></i></div>
                    <div class="sensor__data">
                        <span class="sensor__value">${personas}</span>
                        <span class="sensor__label">Personas</span>
                    </div>
                </div>
            </div>

            <div class="room-card__controls">
                <div class="relay-row">
                    <div class="relay-row__info">
                        <i class="bi bi-fire"></i>
                        <span>Calefacción</span>
                        <span class="relay-row__state relay-row__state--${relay1 ? 'on' : 'off'}">${relay1 ? 'ON' : 'OFF'}</span>
                    </div>
                    <label class="toggle">
                        <input type="checkbox" ${relay1 ? 'checked' : ''} onchange="cambiarRelay('${escapedName}', 1, this.checked)">
                        <span class="toggle__track"></span>
                    </label>
                </div>
                <div class="relay-row">
                    <div class="relay-row__info">
                        <i class="bi bi-lightbulb"></i>
                        <span>Iluminación</span>
                        <span class="relay-row__state relay-row__state--${relay2 ? 'on' : 'off'}">${relay2 ? 'ON' : 'OFF'}</span>
                    </div>
                    <label class="toggle">
                        <input type="checkbox" ${relay2 ? 'checked' : ''} onchange="cambiarRelay('${escapedName}', 2, this.checked)">
                        <span class="toggle__track"></span>
                    </label>
                </div>
            </div>
        `;

        panel.appendChild(card);
    });
}

// ========================================
// LOGOUT
// ========================================

function cerrarSesion() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Logout');
    }
    sessionStorage.clear();
    localStorage.clear();

    fetch('/logout', { method: 'GET', credentials: 'include' })
        .then(() => { window.location.href = '/'; })
        .catch(() => { window.location.href = '/'; });
}

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando panel conserjes');
    connectWebSocket();

    const btnActualizar = document.getElementById('btn-actualizar');
    if (btnActualizar) {
        btnActualizar.addEventListener('click', actualizarLista);
    }

    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
        btnLogout.addEventListener('click', (e) => {
            e.preventDefault();
            cerrarSesion();
        });
    }
});

window.addEventListener('beforeunload', () => {
    if (ws) ws.close();
});
