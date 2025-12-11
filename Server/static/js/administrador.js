// ========================================
// CONFIGURACIÓN Y VARIABLES GLOBALES
// ========================================

let ws = null;
let aulaSeleccionada = null;
let aulasData = {};

// ========================================
// WEBSOCKET - CONEXIÓN Y MANEJO
// ========================================

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/admin`;  // ✅ SIN token en URL
    
    console.log('🔌 Conectando a:', wsUrl);
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('✅ WebSocket conectado (Admin)');
        updateConnectionStatus(true);
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log('📩 Mensaje:', msg);
        
        switch (msg.tipo) {
            case 'admin_bienvenida':
                console.log('Dispositivos conectados:', msg.dispositivos_conectados);
                // ✅ Convertir aulas_estado (clave=device_id) a aulasData
                aulasData = {};
                if (msg.aulas_estado) {
                    Object.keys(msg.aulas_estado).forEach(deviceId => {
                        const aulaData = msg.aulas_estado[deviceId];
                        const aulaNombre = aulaData.aula || aulaData.nombre || deviceId;
                        aulasData[aulaNombre] = { ...aulaData, device_id: deviceId };
                    });
                }
                console.log('📊 aulasData convertido:', aulasData);
                actualizarEstadoDispositivos(msg.dispositivos_conectados);
                renderAulas();
                break;
            
            case 'comando_enviado':
                console.log(`✅ Comando ${msg.accion} enviado a ${msg.device_id}`);
                mostrarNotificacion('success', `Comando ${msg.accion} enviado correctamente`);
                break;
            
            case 'error':
                console.error('❌ Error:', msg.mensaje);
                mostrarNotificacion('error', msg.mensaje);
                break;
            
            case 'test_respuesta':
                console.log('🧪 Test respuesta:', msg);
                mostrarResultadoTest(msg);
                break;
            
            case 'reset_confirmado':
                console.log('🔄 Dispositivo reiniciando:', msg.device_id);
                mostrarNotificacion('info', `Dispositivo ${msg.device_id} reiniciando...`);
                break;
            
            case 'config_confirmada':
                console.log('⚙️ Configuración actualizada:', msg);
                mostrarNotificacion('success', 'Configuración actualizada correctamente');
                break;
            
            case 'actualizacion_aula':
                actualizarAulaEnTiempoReal(msg);
                break;
            
            case 'confirmacion_relay':
                console.log(`✅ Relé confirmado: ${msg.aula} relay${msg.relay_num}=${msg.relay_state}`);
                actualizarRelayEnUI(msg.aula, msg.relay_num, msg.relay_state);
                break;
            
            case 'dispositivo_conectado':
                console.log(`🔌 Dispositivo conectado: ${msg.device_id} (${msg.aula})`);
                mostrarNotificacion('success', `Dispositivo ${msg.device_id} conectado`);
                // Solicitar lista actualizada
                solicitarListaDispositivos();
                break;
            
            case 'dispositivo_desconectado':
                console.log(`❌ Dispositivo desconectado: ${msg.device_id}`);
                mostrarNotificacion('warning', `Dispositivo ${msg.device_id} desconectado`);
                // Actualizar estado
                if (aulasData[msg.aula]) {
                    aulasData[msg.aula].estado = 'desconectada';
                    renderAulas();
                }
                break;
            
            case 'lista_dispositivos':
                console.log('📋 Lista dispositivos:', msg.dispositivos_conectados);
                aulasData = {};
                if (msg.aulas_estado) {
                    Object.keys(msg.aulas_estado).forEach(deviceId => {
                        const aulaData = msg.aulas_estado[deviceId];
                        const aulaNombre = aulaData.aula || aulaData.nombre || deviceId;
                        aulasData[aulaNombre] = { ...aulaData, device_id: deviceId };
                    });
                }
                actualizarEstadoDispositivos(msg.dispositivos_conectados);
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

function enviarComando(action, device_id, data = null) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        mostrarNotificacion('error', 'WebSocket no conectado');
        return false;
    }
    
    const mensaje = { action, device_id };
    if (data) mensaje.data = data;
    
    ws.send(JSON.stringify(mensaje));
    console.log('📤 Comando enviado:', mensaje);
    return true;
}

function solicitarListaDispositivos() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn('WebSocket no conectado');
        return;
    }
    
    ws.send(JSON.stringify({ action: 'listar_dispositivos' }));
    console.log('📤 Solicitando lista de dispositivos...');
}

function enviarToggleRelay(deviceId, relayNum, relayState) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        mostrarNotificacion('error', 'WebSocket no conectado');
        return false;
    }
    
    const mensaje = {
        action: 'toggle_relay',
        device_id: deviceId,
        relay_num: relayNum,
        relay_state: relayState
    };
    
    ws.send(JSON.stringify(mensaje));
    console.log('📤 Toggle relay enviado:', mensaje);
    return true;
}

// ========================================
// FUNCIONES DE UI - NOTIFICACIONES
// ========================================

function mostrarNotificacion(tipo, mensaje) {
    // Crear notificación
    const notif = document.createElement('div');
    notif.className = `notificacion notif-${tipo}`;
    
    const iconos = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    
    notif.innerHTML = `${iconos[tipo] || ''} ${mensaje}`;
    
    // Añadir al DOM
    let container = document.getElementById('notificaciones');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificaciones';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1000;';
        document.body.appendChild(container);
    }
    
    container.appendChild(notif);
    
    // Estilos inline para la notificación
    notif.style.cssText = `
        padding: 12px 20px;
        margin-bottom: 10px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease;
    `;
    
    const colores = {
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    };
    notif.style.backgroundColor = colores[tipo] || '#333';
    if (tipo === 'warning') notif.style.color = '#333';
    
    // Remover después de 4 segundos
    setTimeout(() => {
        notif.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notif.remove(), 300);
    }, 4000);
}

function mostrarResultadoTest(resultado) {
    const uptimeMin = resultado.uptime ? Math.floor(resultado.uptime / 60000) : 'N/A';
    const heapKB = resultado.free_heap ? Math.floor(resultado.free_heap / 1024) : 'N/A';
    
    mostrarNotificacion('info', 
        `Test ${resultado.device_id}: ${resultado.status || 'OK'} | Uptime: ${uptimeMin} min`
    );
}

// ========================================
// FUNCIONES DE ACTUALIZACIÓN DE ESTADO
// ========================================

function actualizarEstadoDispositivos(conectados) {
    console.log('🔄 Actualizando estado de dispositivos:', conectados);
    
    Object.keys(aulasData).forEach(aulaKey => {
        const aula = aulasData[aulaKey];
        const estaConectado = conectados.includes(aula.device_id);
        aula.estado = estaConectado ? 'disponible' : 'desconectada';
        aula.conectado = estaConectado;
    });
}

function actualizarRelayEnUI(aulaKey, relayNum, relayState) {
    if (aulasData[aulaKey]) {
        if (relayNum === 1) aulasData[aulaKey].relay1 = relayState;
        if (relayNum === 2) aulasData[aulaKey].relay2 = relayState;
        console.log(`🔄 UI actualizada: ${aulaKey} relay${relayNum}=${relayState}`);
        renderAulas();
        
        // Si el aula seleccionada es la que se actualizó, refrescar formulario
        if (aulaSeleccionada && aulaSeleccionada.aula === aulaKey) {
            document.getElementById('calefaccion-enabled').checked = aulasData[aulaKey].relay1 || false;
            document.getElementById('iluminacion-enabled').checked = aulasData[aulaKey].relay2 || false;
        }
    }
}

function actualizarAulaEnTiempoReal(msg) {
    const aulaKey = msg.aula;
    
    if (!aulasData[aulaKey]) {
        aulasData[aulaKey] = { device_id: msg.device_id };
    }
    
    // Actualizar campos del aula
    if (msg.temperatura !== undefined) aulasData[aulaKey].temperatura = msg.temperatura;
    if (msg.humedad !== undefined) aulasData[aulaKey].humedad = msg.humedad;
    if (msg.presion !== undefined) aulasData[aulaKey].presion = msg.presion;
    if (msg.luz !== undefined) aulasData[aulaKey].luz = msg.luz;
    if (msg.personas !== undefined) aulasData[aulaKey].personas = msg.personas;
    if (msg.estado !== undefined) aulasData[aulaKey].estado = msg.estado;
    if (msg.relay1 !== undefined) aulasData[aulaKey].relay1 = msg.relay1;
    if (msg.relay2 !== undefined) aulasData[aulaKey].relay2 = msg.relay2;
    
    console.log(`🔄 Aula actualizada en tiempo real: ${aulaKey}`, aulasData[aulaKey]);
    renderAulas();
}

// ========================================
// RENDERIZADO Y SELECCIÓN DE AULAS
// ========================================

function renderAulas() {
    const container = document.getElementById('aulas-list');
    if (!container) return;
    
    container.innerHTML = '';
    
    const aulasKeys = Object.keys(aulasData);
    
    if (aulasKeys.length === 0) {
        container.innerHTML = '<p class="empty-message">No hay dispositivos conectados</p>';
        return;
    }
    
    console.log('🎨 Renderizando aulas:', aulasData);

    aulasKeys.forEach(aulaKey => {
        const aula = aulasData[aulaKey];
        const card = document.createElement('div');
        const isSelected = aulaSeleccionada && aulaSeleccionada.device_id === aula.device_id;
        card.className = `aula-card ${isSelected ? 'active' : ''} ${aula.conectado ? '' : 'disconnected'}`;
        card.onclick = () => seleccionarAula(aulaKey, aula);
        
        const estado = aula.conectado ? 'conectado' : 'desconectado';
        const estadoClass = aula.conectado ? 'disponible' : 'desconectada';
        const temp = aula.temperatura !== undefined ? `${aula.temperatura}°C` : 'N/A';
        const humedad = aula.humedad !== undefined ? `${aula.humedad}%` : 'N/A';
        const presion = aula.presion !== undefined ? `${aula.presion} hPa` : 'N/A';
        const luz = aula.luz !== undefined ? `${aula.luz} lux` : 'N/A';
        const personas = aula.personas !== undefined ? aula.personas : 0;
        const capacidad = aula.capacidad || '?';
        
        card.innerHTML = `
            <div class="aula-header">
                <span class="aula-name">${aulaKey}</span>
                <span class="status-badge ${estadoClass}">${estado.toUpperCase()}</span>
            </div>
            <div class="aula-info">
                <div class="info-item">
                    <span class="info-label">Device ID:</span>
                    <span>${aula.device_id || 'N/A'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Personas:</span>
                    <span>${personas}/${capacidad}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Temp:</span>
                    <span>${temp}</span>
                </div>
                
                <div class="info-item">
                    <span class="info-label">Humedad:</span>
                    <span>${humedad}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Presión:</span>
                    <span>${presion}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Luz:</span>
                    <span>${luz}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Calefacción:</span>
                    <span>${aula.relay1 ? '🔥 ON' : '❄️ OFF'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Iluminación:</span>
                    <span>${aula.relay2 ? '💡 ON' : '🌑 OFF'}</span>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

function seleccionarAula(aulaKey, aula) {
    aulaSeleccionada = { ...aula, aulaKey: aulaKey };
    
    document.getElementById('empty-state').classList.remove('active');
    document.getElementById('form-container').classList.add('active');
    
    // Llenar formulario
    document.getElementById('device-id').value = aula.device_id || '';
    document.getElementById('aula-nombre').value = aulaKey;
    document.getElementById('edificio').value = aula.edificio || '';
    document.getElementById('planta').value = aula.planta || '';
    document.getElementById('capacidad').value = aula.capacidad || '';
    document.getElementById('calefaccion-enabled').checked = aula.relay1 || false;
    document.getElementById('iluminacion-enabled').checked = aula.relay2 || false;
    document.getElementById('ip-address').value = aula.ip || 'N/A';
    
    renderAulas();
}

// ========================================
// EVENT LISTENERS
// ========================================

function setupEventListeners() {
    // Guardar cambios
    const form = document.getElementById('aula-form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            if (!aulaSeleccionada) return;
            
            const config = {
                nombre: document.getElementById('aula-nombre').value,
                edificio: document.getElementById('edificio').value,
                planta: parseInt(document.getElementById('planta').value) || 0,
                capacidad: parseInt(document.getElementById('capacidad').value) || 0,
                calefaccion: document.getElementById('calefaccion-enabled').checked,
                iluminacion: document.getElementById('iluminacion-enabled').checked
            };

            enviarComando('actualizar_config', aulaSeleccionada.device_id, config);
            
            // Actualizar localmente
            const aulaKey = aulaSeleccionada.aulaKey;
            if (aulasData[aulaKey]) {
                Object.assign(aulasData[aulaKey], config);
            }
            
            mostrarNotificacion('info', 'Enviando configuración...');
        });
    }

    // Resetear nodo
    const btnReset = document.getElementById('btn-reset');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            if (!aulaSeleccionada) return;
            if (!confirm(`¿Resetear ${aulaSeleccionada.aulaKey}?`)) return;
            
            enviarComando('resetear_nodo', aulaSeleccionada.device_id);
        });
    }

    // Cancelar edición
    const btnCancel = document.getElementById('btn-cancel');
    if (btnCancel) {
        btnCancel.addEventListener('click', () => {
            aulaSeleccionada = null;
            document.getElementById('form-container').classList.remove('active');
            document.getElementById('empty-state').classList.add('active');
            renderAulas();
        });
    }

    // Test de conexión
    const btnTest = document.getElementById('btn-test');
    if (btnTest) {
        btnTest.addEventListener('click', () => {
            if (!aulaSeleccionada) return;
            enviarComando('test_conexion', aulaSeleccionada.device_id);
            mostrarNotificacion('info', 'Enviando test de conexión...');
        });
    }

    // Toggle Calefacción desde el formulario
    const calefaccionCheckbox = document.getElementById('calefaccion-enabled');
    if (calefaccionCheckbox) {
        calefaccionCheckbox.addEventListener('change', (e) => {
            if (!aulaSeleccionada) return;
            enviarToggleRelay(aulaSeleccionada.device_id, 1, e.target.checked);
        });
    }

    // Toggle Iluminación desde el formulario
    const iluminacionCheckbox = document.getElementById('iluminacion-enabled');
    if (iluminacionCheckbox) {
        iluminacionCheckbox.addEventListener('change', (e) => {
            if (!aulaSeleccionada) return;
            enviarToggleRelay(aulaSeleccionada.device_id, 2, e.target.checked);
        });
    }

    // Botón actualizar lista (si existe)
    const btnActualizar = document.getElementById('btn-actualizar');
    if (btnActualizar) {
        btnActualizar.addEventListener('click', solicitarListaDispositivos);
    }
}

// ========================================
// INICIALIZACIÓN
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando panel admin');
    
    // Añadir estilos para animaciones
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .aula-card.disconnected { opacity: 0.6; }
        .empty-message { text-align: center; color: #666; padding: 20px; }
    `;
    document.head.appendChild(style);
    
    setupEventListeners();
    connectWebSocket();
    renderAulas();
});

window.addEventListener('beforeunload', () => {
    if (ws) ws.close();
});

function cerrarSesion() {
    // 1. Cerrar WebSocket si está abierto
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close(1000, 'Logout');
    }
     // 2. Limpiar almacenamiento local y de sesión
    sessionStorage.clear();
    localStorage.clear();

    // 3. Llamar al endpoint de logout del servidor para borrar la cookie
    fetch('/logout', {
        method: 'GET',
        credentials: 'include'
    })
    .then(() => {
        // 4. Redirigir al usuario al inicio o login
        window.location.href = '/';
    })
    .catch(() => {
        window.location.href = '/';
    });
}
