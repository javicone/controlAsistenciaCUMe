// ========================================
// CONFIGURACIÓN Y VARIABLES GLOBALES
// ========================================

let aulasData = {};
let ws = null;

// ========================================
// WEBSOCKET - CONEXIÓN Y MANEJO
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
            case 'conserje_bienvenida':
                console.log('Dispositivos conectados:', msg.dispositivos_conectados);
                // ✅ Convertir aulas_estado (clave=device_id) a aulasData (clave=nombre_aula)
                aulasData = {};
                if (msg.aulas_estado) {
                    Object.keys(msg.aulas_estado).forEach(deviceId => {
                        const aulaData = msg.aulas_estado[deviceId];
                        const aulaNombre = aulaData.aula || aulaData.nombre || deviceId;
                        aulasData[aulaNombre] = { ...aulaData, device_id: deviceId };
                    });
                }
                console.log('📊 aulasData convertido:', aulasData);
                renderAulas();
                break;
            
            case 'comando_enviado':
                console.log(`✅ Comando ${msg.accion} enviado a ${msg.aula}`);
                break;
            
            case 'error':
                console.error('❌ Error:', msg.mensaje);
                alert('Error: ' + msg.mensaje);
                break;
            
            case 'actualizacion_aula':
                // Actualización en tiempo real del estado de un aula
                actualizarAulaEnTiempoReal(msg);
                break;
            
            case 'confirmacion_relay':
                // ✅ NUEVO: Confirmación del ESP32 de que el relé cambió
                console.log(`✅ Relé confirmado: ${msg.aula} relay${msg.relay_num}=${msg.relay_state}`);
                console.log('📊 Estado actual de aulasData antes de actualizar:', aulasData);
                actualizarRelayEnUI(msg.aula, msg.relay_num, msg.relay_state);
                console.log('📊 Estado actual de aulasData después de actualizar:', aulasData);
                break;
            
            case 'lista_dispositivos':
                console.log('Dispositivos conectados:', msg.dispositivos_conectados);
                // ✅ Convertir también aquí
                aulasData = {};
                if (msg.aulas_estado) {
                    Object.keys(msg.aulas_estado).forEach(deviceId => {
                        const aulaData = msg.aulas_estado[deviceId];
                        const aulaNombre = aulaData.aula || aulaData.nombre || deviceId;
                        aulasData[aulaNombre] = { ...aulaData, device_id: deviceId };
                    });
                }
                console.log('📊 aulasData convertido:', aulasData);
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
        // Reconectar en 5 segundos
        setTimeout(connectWebSocket, 5000);
    };
}

function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('ws-status');
    if (statusEl) {
        statusEl.textContent = connected ? '🟢 Conectado' : '🔴 Desconectado';
        statusEl.className = connected ? 'status-connected' : 'status-disconnected';
    }
}

// ========================================
// FUNCIONES DE ENVÍO
// ========================================

function cambiarRelay(aulaName, relayNum, nuevoEstado) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert('WebSocket no conectado');
        return false;
    }
    
    // ✅ FIX: Enviar por NOMBRE DE AULA, el servidor resuelve el device_id
    const mensaje = {
        action: 'toggle_relay',
        aula: aulaName,          // ← Enviamos el nombre del aula
        relay_num: relayNum,     // ← 1 = calefacción, 2 = iluminación
        relay_state: nuevoEstado // ← true/false
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
// FUNCIONES DE UI
// ========================================

function actualizarRelayEnUI(aulaKey, relayNum, relayState) {
    // ✅ Ahora aulasData usa el nombre del aula como clave directamente
    if (aulasData[aulaKey]) {
        if (relayNum === 1) aulasData[aulaKey].relay1 = relayState;
        if (relayNum === 2) aulasData[aulaKey].relay2 = relayState;
        console.log(`🔄 UI actualizada: ${aulaKey} relay${relayNum}=${relayState}`);
        renderAulas();
    } else {
        console.warn(`⚠️ Aula '${aulaKey}' no encontrada en aulasData para actualizar relay`);
    }
}

function actualizarAulaEnTiempoReal(msg) {
    const aulaKey = msg.aula;
    
    if (!aulasData[aulaKey]) {
        aulasData[aulaKey] = {};
    }
    
    // Actualizar campos del aula
    if (msg.temperatura !== undefined) aulasData[aulaKey].temperatura = msg.temperatura;
    if (msg.humedad !== undefined) aulasData[aulaKey].humedad = msg.humedad;
    if (msg.luz !== undefined) aulasData[aulaKey].luz = msg.luz;
    if (msg.personas !== undefined) aulasData[aulaKey].personas = msg.personas;
    if (msg.estado !== undefined) aulasData[aulaKey].estado = msg.estado;
    if (msg.relay1 !== undefined) aulasData[aulaKey].relay1 = msg.relay1;
    if (msg.relay2 !== undefined) aulasData[aulaKey].relay2 = msg.relay2;
    if (msg.clase_en_curso !== undefined) aulasData[aulaKey].clase_en_curso = msg.clase_en_curso;
    
    console.log(`🔄 Aula actualizada en tiempo real: ${aulaKey}`, aulasData[aulaKey]);
    renderAulas();
}

function renderAulas() {
    const panel = document.getElementById('panel');
    if (!panel) return;
    
    panel.innerHTML = '';
    
    if (Object.keys(aulasData).length === 0) {
        panel.innerHTML = '<p>No hay aulas disponibles</p>';
        return;
    }
    
    console.log('🎨 Renderizando aulas:', aulasData);
    
    Object.keys(aulasData).forEach(aulaKey => {
        const aula = aulasData[aulaKey];
        const aulaDiv = document.createElement('div');
        aulaDiv.classList.add('aula');
        
        const aulaName = aula.nombre || aula.aula || aulaKey;
        const temp = aula.temperatura !== undefined ? `${aula.temperatura}°C` : 'N/A';
        const luz = aula.luz !== undefined ? `${aula.luz} lux` : 'N/A';
        const personas = aula.personas !== undefined ? aula.personas : 'N/A';
        const claseEnCurso = aula.clase_en_curso ? 'Sí' : 'No';
        const relay1State = aula.relay1 || false;
        const relay2State = aula.relay2 || false;
        
        console.log(`📊 Renderizando ${aulaName}: relay1=${relay1State}, relay2=${relay2State}`);
        
        aulaDiv.innerHTML = `
            <h3>${aulaName}</h3>
            <p><strong>Temperatura:</strong> ${temp}</p>
            <p><strong>Luz:</strong> ${luz}</p>
            <p><strong>Personas:</strong> ${personas}</p>
            <p><strong>Clase en Curso:</strong> ${claseEnCurso}</p>
            <div class="relay-controls">
                <p><strong>Calefacción:</strong> ${relay1State ? 'Encendida' : 'Apagada'}</p>
                <button 
                    class="button ${relay1State ? 'button-off' : 'button-on'}" 
                    onclick="cambiarRelay('${aulaName}', 1, ${!relay1State})"
                >
                    ${relay1State ? 'Apagar' : 'Encender'} Calefacción
                </button>
                
                <p><strong>Iluminación:</strong> ${relay2State ? 'Encendida' : 'Apagada'}</p>
                <button 
                    class="button ${relay2State ? 'button-off' : 'button-on'}" 
                    onclick="cambiarRelay('${aulaName}', 2, ${!relay2State})"
                >
                    ${relay2State ? 'Apagar' : 'Encender'} Iluminación
                </button>
            </div>
        `;
        
        panel.appendChild(aulaDiv);
    });
}

function cerrarSesion() {
    if (ws) ws.close();
    sessionStorage.removeItem('token');
    localStorage.removeItem('token');
    window.location.href = '/';
}

// ========================================
// INICIALIZACIÓN
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando panel conserjes');
    connectWebSocket();
    
    // Botón actualizar lista (si existe)
    const btnActualizar = document.getElementById('btn-actualizar');
    if (btnActualizar) {
        btnActualizar.addEventListener('click', actualizarLista);
    }
});

window.addEventListener('beforeunload', () => {
    if (ws) ws.close();
});