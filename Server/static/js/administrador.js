// ========================================
// CONFIGURACIÓN Y VARIABLES GLOBALES
// ========================================

let ws = null;
let aulaSeleccionada = null;
let aulasData = [];

// ========================================
// WEBSOCKET - CONEXIÓN Y MANEJO
// ========================================

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/admin?token=${JWT_TOKEN}`;
    
    console.log('🔌 Conectando a:', wsUrl);
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        updateConnectionStatus(true);
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log('📩 Mensaje:', msg);
        
        switch (msg.tipo) {
            case 'admin_bienvenida':
                console.log('Dispositivos conectados:', msg.dispositivos_conectados);
                actualizarEstadoDispositivos(msg.dispositivos_conectados);
                break;
            
            case 'comando_enviado':
                console.log(`✅ Comando ${msg.accion} enviado`);
                break;
            
            case 'error':
                console.error('❌ Error:', msg.mensaje);
                alert('Error: ' + msg.mensaje);
                break;
            
            case 'test_respuesta':
                mostrarResultadoTest(msg);
                break;
            
            case 'reset_confirmado':
                console.log('🔄 Dispositivo reiniciando...');
                break;
            
            case 'config_confirmada':
                console.log('⚙️ Configuración actualizada');
                break;
            
            case 'actualizacion_aula':
                actualizarAulaEnTiempoReal(msg);
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
        alert('WebSocket no conectado');
        return false;
    }
    
    const mensaje = { action, device_id };
    if (data) mensaje.data = data;
    
    ws.send(JSON.stringify(mensaje));
    console.log('📤 Comando enviado:', mensaje);
    return true;
}

// ========================================
// FUNCIONES DE UI
// ========================================

function mostrarResultadoTest(resultado) {
    alert(`🧪 Test - ${resultado.device_id}\n\nEstado: ${resultado.estado}\nWiFi: ${resultado.wifi_rssi} dBm\nUptime: ${Math.floor(resultado.uptime / 60)} min\nRAM libre: ${Math.floor(resultado.free_heap / 1024)} KB`);
}

function actualizarEstadoDispositivos(conectados) {
    aulasData.forEach(aula => {
        aula.estado = conectados.includes(aula.device_id) ? 'disponible' : 'desconectada';
    });
    renderAulas();
}

function actualizarAulaEnTiempoReal(msg) {
    const aula = aulasData.find(a => a.nombre === msg.aula);
    if (aula) {
        if (msg.temperatura !== undefined) aula.temperatura = msg.temperatura;
        if (msg.humedad !== undefined) aula.humedad = msg.humedad;
        if (msg.luz !== undefined) aula.luz = msg.luz;
        if (msg.personas !== undefined) aula.personas = msg.personas;
        if (msg.estado !== undefined) aula.estado = msg.estado;
        renderAulas();
    }
}

// ========================================
// RENDERIZADO Y SELECCIÓN DE AULAS
// ========================================

// Datos de ejemplo
aulasData = [
    {
        device_id: 'ESP32_AULA_A101',
        nombre: 'Aula A-101',
        ip: '192.168.1.101',
        estado: 'disponible',
        edificio: 'Edificio A',
        planta: 1,
        capacidad: 30,
        calefaccion: true,
        iluminacion: true,
        personas: 0,
        temperatura: 22.5,
        luz: 450
    },
    {
        device_id: 'ESP32_AULA_B203',
        nombre: 'Aula B-203',
        ip: '192.168.1.102',
        estado: 'ocupada',
        edificio: 'Edificio B',
        planta: 2,
        capacidad: 40,
        calefaccion: true,
        iluminacion: false,
        personas: 25,
        temperatura: 23.1,
        luz: 380
    },
    {
        device_id: 'ESP32_LAB_C105',
        nombre: 'Laboratorio C-105',
        ip: '192.168.1.103',
        estado: 'desconectada',
        edificio: 'Edificio C',
        planta: 1,
        capacidad: 20,
        calefaccion: false,
        iluminacion: true,
        personas: 0,
        temperatura: null,
        luz: null
    }
];

// Renderizar lista de aulas
function renderAulas() {
    const container = document.getElementById('aulas-list');
    container.innerHTML = '';

    aulasData.forEach(aula => {
        const card = document.createElement('div');
        card.className = `aula-card ${aulaSeleccionada?.id === aula.id ? 'active' : ''}`;
        card.onclick = () => seleccionarAula(aula);
        
        card.innerHTML = `
            <div class="aula-header">
                <span class="aula-name">${aula.nombre}</span>
                <span class="status-badge ${aula.estado}">${aula.estado.toUpperCase()}</span>
            </div>
            <div class="aula-info">
                <div class="info-item">
                    <span class="info-label">Device ID:</span>
                    <span>${aula.device_id}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">IP:</span>
                    <span>${aula.ip}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Personas:</span>
                    <span>${aula.personas}/${aula.capacidad}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Temp:</span>
                    <span>${aula.temperatura ? aula.temperatura + '°C' : 'N/A'}</span>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// Seleccionar aula
function seleccionarAula(aula) {
    aulaSeleccionada = aula;
    document.getElementById('empty-state').classList.remove('active');
    document.getElementById('form-container').classList.add('active');
    
    // Llenar formulario
    document.getElementById('device-id').value = aula.device_id;
    document.getElementById('aula-nombre').value = aula.nombre;
    document.getElementById('edificio').value = aula.edificio;
    document.getElementById('planta').value = aula.planta;
    document.getElementById('capacidad').value = aula.capacidad;
    document.getElementById('calefaccion-enabled').checked = aula.calefaccion;
    document.getElementById('iluminacion-enabled').checked = aula.iluminacion;
    document.getElementById('ip-address').value = aula.ip;
    
    renderAulas();
}

// Guardar cambios
document.getElementById('aula-form').addEventListener('submit', (e) => {
    e.preventDefault();
    
    if (!aulaSeleccionada) return;
    
    const config = {
        nombre: document.getElementById('aula-nombre').value,
        edificio: document.getElementById('edificio').value,
        planta: parseInt(document.getElementById('planta').value),
        capacidad: parseInt(document.getElementById('capacidad').value),
        calefaccion: document.getElementById('calefaccion-enabled').checked,
        iluminacion: document.getElementById('iluminacion-enabled').checked
    };

    enviarComando('actualizar_config', aulaSeleccionada.device_id, config);
    Object.assign(aulaSeleccionada, config);
    renderAulas();
});

// Resetear nodo
document.getElementById('btn-reset').addEventListener('click', () => {
    if (!aulaSeleccionada) return;
    if (!confirm(`¿Resetear ${aulaSeleccionada.nombre}?`)) return;
    
    enviarComando('resetear_nodo', aulaSeleccionada.device_id);
});

// Cancelar edición
document.getElementById('btn-cancel').addEventListener('click', () => {
    aulaSeleccionada = null;
    document.getElementById('form-container').classList.remove('active');
    document.getElementById('empty-state').classList.add('active');
    renderAulas();
});

// Test de conexión
document.getElementById('btn-test').addEventListener('click', () => {
    if (!aulaSeleccionada) return;
    enviarComando('test_conexion', aulaSeleccionada.device_id);
});

// ========================================
// INICIALIZACIÓN
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando panel admin');
    connectWebSocket();
    renderAulas();
});

window.addEventListener('beforeunload', () => {
    if (ws) ws.close();
});
