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
    console.log('🔧 Mostrando diagnóstico:', resultado);
    
    // Mostrar sección de diagnóstico
    const diagSection = document.getElementById('diagnostico-section');
    if (diagSection) {
        diagSection.style.display = 'block';
    }
    
    // Info del sistema
    const rssi = resultado.wifi_rssi;
    const rssiText = rssi ? `${rssi} dBm` : '--';
    document.getElementById('diag-rssi').textContent = rssiText;
    
    // Uptime: puede venir en milisegundos o segundos
    let uptimeSec = resultado.uptime || 0;
    // Si es mayor a 100000, probablemente está en milisegundos
    if (uptimeSec > 100000) {
        uptimeSec = Math.floor(uptimeSec / 1000);
    }
    const uptimeText = formatUptime(uptimeSec);
    document.getElementById('diag-uptime').textContent = uptimeText;
    
    const heapBytes = resultado.free_heap || 0;
    const heapText = heapBytes ? `${Math.floor(heapBytes / 1024)} KB` : '--';
    document.getElementById('diag-heap').textContent = heapText;
    
    // Estado de sensores
    const sensores = resultado.sensores || {};
    actualizarEstadoSensor('status-nfc', sensores.nfc);
    actualizarEstadoSensor('status-radar', sensores.radar);
    actualizarEstadoSensor('status-bme', sensores.bme280);
    actualizarEstadoSensor('status-luz', sensores.bh1750);
    
    // Estado de relés (si viene en la respuesta)
    actualizarEstadoRelay('status-relay1', resultado.relay1);
    actualizarEstadoRelay('status-relay2', resultado.relay2);
    
    // Timestamp
    const timestamp = new Date().toLocaleTimeString('es-ES');
    document.getElementById('diag-timestamp').textContent = `Última consulta: ${timestamp}`;
    
    mostrarNotificacion('success', `Diagnóstico de ${resultado.device_id} completado`);
}

function formatUptime(segundos) {
    if (!segundos) return '--';
    const dias = Math.floor(segundos / 86400);
    const horas = Math.floor((segundos % 86400) / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    
    if (dias > 0) return `${dias}d ${horas}h ${minutos}m`;
    if (horas > 0) return `${horas}h ${minutos}m`;
    return `${minutos}m`;
}

function actualizarEstadoSensor(elementId, estado) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const statusText = element.querySelector('.status-text');
    
    if (estado === true) {
        element.style.borderLeftColor = '#28a745';
        element.style.background = '#d4edda';
        if (statusText) statusText.textContent = '✅ Operativo';
    } else if (estado === false) {
        element.style.borderLeftColor = '#dc3545';
        element.style.background = '#f8d7da';
        if (statusText) statusText.textContent = '❌ Error';
    } else {
        element.style.borderLeftColor = '#ffc107';
        element.style.background = '#fff3cd';
        if (statusText) statusText.textContent = '⚠️ Sin datos';
    }
}

function actualizarEstadoRelay(elementId, estado) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const stateText = element.querySelector('.relay-state');
    
    if (estado === true) {
        element.style.borderColor = '#28a745';
        element.style.background = '#d4edda';
        if (stateText) stateText.textContent = '🟢 ENCENDIDO';
    } else if (estado === false) {
        element.style.borderColor = '#6c757d';
        element.style.background = '#f8f9fa';
        if (stateText) stateText.textContent = '⚫ APAGADO';
    } else {
        element.style.borderColor = '#e0e0e0';
        element.style.background = '#f8f9fa';
        if (stateText) stateText.textContent = '--';
    }
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
        if (aulaSeleccionada && (aulaSeleccionada.aula === aulaKey || aulaSeleccionada.aulaKey === aulaKey)) {
            document.getElementById('calefaccion-enabled').checked = aulasData[aulaKey].relay1 || false;
            document.getElementById('iluminacion-enabled').checked = aulasData[aulaKey].relay2 || false;
            // Actualizar sensores también
            const aula = aulasData[aulaKey];
            document.getElementById('sensor-temp').textContent = aula.temperatura !== undefined ? `${aula.temperatura}°C` : 'N/A';
            document.getElementById('sensor-humedad').textContent = aula.humedad !== undefined ? `${aula.humedad}%` : 'N/A';
            document.getElementById('sensor-presion').textContent = aula.presion !== undefined ? `${aula.presion} hPa` : 'N/A';
            document.getElementById('sensor-luz').textContent = aula.luz !== undefined ? `${aula.luz} lux` : 'N/A';
            document.getElementById('sensor-personas').textContent = aula.personas !== undefined ? aula.personas : 'N/A';
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
    if (msg.ip !== undefined) aulasData[aulaKey].ip = msg.ip;
    
    console.log(`🔄 Aula actualizada en tiempo real: ${aulaKey}`, aulasData[aulaKey]);
    renderAulas();
    
    // Si el aula seleccionada es la que se actualizó, refrescar sensores en el panel
    if (aulaSeleccionada && (aulaSeleccionada.aulaKey === aulaKey || aulaSeleccionada.aula === aulaKey)) {
        const aula = aulasData[aulaKey];
        document.getElementById('sensor-temp').textContent = aula.temperatura !== undefined ? `${aula.temperatura}°C` : 'N/A';
        document.getElementById('sensor-humedad').textContent = aula.humedad !== undefined ? `${aula.humedad}%` : 'N/A';
        document.getElementById('sensor-presion').textContent = aula.presion !== undefined ? `${aula.presion} hPa` : 'N/A';
        document.getElementById('sensor-luz').textContent = aula.luz !== undefined ? `${aula.luz} lux` : 'N/A';
        document.getElementById('sensor-personas').textContent = aula.personas !== undefined ? aula.personas : 'N/A';
        document.getElementById('ip-address').value = aula.ip || 'N/A';
        document.getElementById('calefaccion-enabled').checked = aula.relay1 || false;
        document.getElementById('iluminacion-enabled').checked = aula.relay2 || false;
    }
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
        
        const personas = aula.personas !== undefined ? aula.personas : 0;
        const hayClase = personas > 0;
        
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
                    <span class="info-label">Clase:</span>
                    <span>${hayClase ? '📚 EN CLASE' : '🚫 SIN CLASE'}</span>
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
    
    document.getElementById('empty-state').classList.add('hidden');
    document.getElementById('form-container').classList.add('active');
    
    // Ocultar sección de diagnóstico al cambiar de aula
    const diagSection = document.getElementById('diagnostico-section');
    if (diagSection) diagSection.style.display = 'none';
    
    // Llenar formulario
    document.getElementById('device-id').value = aula.device_id || '';
    document.getElementById('aula-nombre').value = aulaKey;
    document.getElementById('calefaccion-enabled').checked = aula.relay1 || false;
    document.getElementById('iluminacion-enabled').checked = aula.relay2 || false;
    document.getElementById('ip-address').value = aula.ip || 'N/A';
    
    // Llenar datos de sensores
    document.getElementById('sensor-temp').textContent = aula.temperatura !== undefined ? `${aula.temperatura}°C` : 'N/A';
    document.getElementById('sensor-humedad').textContent = aula.humedad !== undefined ? `${aula.humedad}%` : 'N/A';
    document.getElementById('sensor-presion').textContent = aula.presion !== undefined ? `${aula.presion} hPa` : 'N/A';
    document.getElementById('sensor-luz').textContent = aula.luz !== undefined ? `${aula.luz} lux` : 'N/A';
    document.getElementById('sensor-personas').textContent = aula.personas !== undefined ? aula.personas : 'N/A';
    
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
            document.getElementById('empty-state').classList.remove('hidden');
            // Ocultar diagnóstico
            const diagSection = document.getElementById('diagnostico-section');
            if (diagSection) diagSection.style.display = 'none';
            renderAulas();
        });
    }

    // Diagnóstico de sensores
    const btnDiagnostico = document.getElementById('btn-diagnostico');
    if (btnDiagnostico) {
        btnDiagnostico.addEventListener('click', () => {
            if (!aulaSeleccionada) return;
            
            // Feedback visual
            btnDiagnostico.disabled = true;
            btnDiagnostico.innerHTML = '⏳ Consultando...';
            
            enviarComando('test_conexion', aulaSeleccionada.device_id);
            mostrarNotificacion('info', 'Solicitando diagnóstico del nodo...');
            
            // Restaurar botón después de 3 segundos
            setTimeout(() => {
                btnDiagnostico.disabled = false;
                btnDiagnostico.innerHTML = '🔧 Diagnóstico';
            }, 3000);
        });
    }

    // Refrescar sensores
    const btnRefresh = document.getElementById('btn-refresh');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            refrescarSensores();
        });
    }

    // Toggle Calefacción desde el formulario
    const calefaccionCheckbox = document.getElementById('calefaccion-enabled');
    if (calefaccionCheckbox) {
        calefaccionCheckbox.addEventListener('change', (e) => {
            if (!aulaSeleccionada) {
                e.preventDefault();
                e.target.checked = !e.target.checked;
                return;
            }
            
            const nuevoEstado = e.target.checked;
            console.log(`🔥 Toggle calefacción: ${nuevoEstado} para ${aulaSeleccionada.device_id}`);
            
            // Enviar comando
            const exito = enviarToggleRelay(aulaSeleccionada.device_id, 1, nuevoEstado);
            
            // Si falla el envío, revertir el checkbox
            if (!exito) {
                console.warn('❌ Fallo al enviar comando, revirtiendo checkbox');
                e.target.checked = !nuevoEstado;
            }
        });
    }

    // Toggle Iluminación desde el formulario
    const iluminacionCheckbox = document.getElementById('iluminacion-enabled');
    if (iluminacionCheckbox) {
        iluminacionCheckbox.addEventListener('change', (e) => {
            if (!aulaSeleccionada) {
                e.preventDefault();
                e.target.checked = !e.target.checked;
                return;
            }
            
            const nuevoEstado = e.target.checked;
            console.log(`💡 Toggle iluminación: ${nuevoEstado} para ${aulaSeleccionada.device_id}`);
            
            // Enviar comando
            const exito = enviarToggleRelay(aulaSeleccionada.device_id, 2, nuevoEstado);
            
            // Si falla el envío, revertir el checkbox
            if (!exito) {
                console.warn('❌ Fallo al enviar comando, revirtiendo checkbox');
                e.target.checked = !nuevoEstado;
            }
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

// Función para refrescar sensores
function refrescarSensores() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        mostrarNotificacion('error', 'WebSocket no conectado');
        return;
    }

    console.log('🔃 Solicitando actualización de sensores...');
    
    const mensaje = {
        tipo: 'solicitar_estado',
        timestamp: Date.now()
    };

    ws.send(JSON.stringify(mensaje));
    console.log('📡 Solicitud de estado enviada:', mensaje);
    
    // Mostrar feedback visual
    const btnRefresh = document.getElementById('btn-refresh');
    if (btnRefresh) {
        const textoOriginal = btnRefresh.innerHTML;
        btnRefresh.innerHTML = '⏳ Actualizando...';
        btnRefresh.disabled = true;
        
        setTimeout(() => {
            btnRefresh.innerHTML = textoOriginal;
            btnRefresh.disabled = false;
        }, 2000);
    }
    
    mostrarNotificacion('info', 'Solicitando actualización de sensores...');
}
