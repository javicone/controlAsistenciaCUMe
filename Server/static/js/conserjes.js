// ========================================
// CONFIGURACIÓN Y VARIABLES GLOBALES
// ========================================

let ws = null;
let aulasData = {};



// ========================================
// WEBSOCKET - CONEXIÓN Y MANEJO
// ========================================

function connectWebSocket() {
    // Nota: Ya no ponemos ?token=... en la URL si usamos cookies
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/conserje`; 
    
    console.log('🔌 Conectando a:', wsUrl);
    
    const ws = new WebSocket(wsUrl);
    
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
                aulasData = msg.aulas_estado || {};
                renderAulas();
                break;
            
            case 'comando_enviado':
                console.log(`✅ Comando ${msg.accion} enviado`);
                break;
            
            case 'error':
                console.error('❌ Error:', msg.mensaje);
                alert('Error: ' + msg.mensaje);
                break;
            
            case 'actualizacion_aula':
                // Actualización en tiempo real del estado de un aula
                actualizarAulaEnTiempoReal(msg);
                break;
            
            case 'lista_dispositivos':
                console.log('Dispositivos conectados:', msg.dispositivos_conectados);
                aulasData = msg.aulas_estado || {};
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
    
    // Buscar device_id del aula por su nombre
    const aula = Object.values(aulasData).find(a => a.nombre === aulaName || a.aula === aulaName);
    if (!aula || !aula.device_id) {
        alert('No se encontró el device_id del aula');
        return false;
    }
    
    const mensaje = {
        action: 'toggle_relay',
        device_id: aula.device_id,
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
// FUNCIONES DE UI
// ========================================

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
    
    Object.keys(aulasData).forEach(aulaKey => {
        const aula = aulasData[aulaKey];
        const aulaDiv = document.createElement('div');
        aulaDiv.classList.add('aula');
        
        const aulaName = aula.nombre || aula.aula || aulaKey;
        const temp = aula.temperatura !== undefined ? `${aula.temperatura}°C` : 'N/A';
        const luz = aula.luz !== undefined ? (aula.luz ? 'Encendida' : 'Apagada') : 'N/A';
        const personas = aula.personas !== undefined ? aula.personas : 'N/A';
        const claseEnCurso = aula.clase_en_curso ? 'Sí' : 'No';
        const relay1State = aula.relay1 || false;
        const relay2State = aula.relay2 || false;
        
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
