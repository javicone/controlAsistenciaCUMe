// Datos de ejemplo (esto vendrá del backend)
let aulasData = [
    {
        id: 1,
        nombre: 'Aula A-101',
        mac: 'AA:BB:CC:DD:EE:01',
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
        id: 2,
        nombre: 'Aula B-203',
        mac: 'AA:BB:CC:DD:EE:02',
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
        id: 3,
        nombre: 'Laboratorio C-105',
        mac: 'AA:BB:CC:DD:EE:03',
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

let aulaSeleccionada = null;

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
                    <span class="info-label">MAC:</span>
                    <span>${aula.mac}</span>
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
    document.getElementById('mac-address').value = aula.mac;
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
document.getElementById('aula-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const datosActualizados = {
        nombre: document.getElementById('aula-nombre').value,
        edificio: document.getElementById('edificio').value,
        planta: parseInt(document.getElementById('planta').value),
        capacidad: parseInt(document.getElementById('capacidad').value),
        calefaccion: document.getElementById('calefaccion-enabled').checked,
        iluminacion: document.getElementById('iluminacion-enabled').checked
    };

    console.log('Guardando cambios para:', aulaSeleccionada.mac, datosActualizados);
    
    // TODO: Enviar al backend
    // await fetch(`/api/aulas/${aulaSeleccionada.id}`, {
    //     method: 'PUT',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(datosActualizados)
    // });

    // Actualizar datos locales
    Object.assign(aulaSeleccionada, datosActualizados);
    renderAulas();
    
    alert('✅ Cambios guardados correctamente');
});

// Resetear nodo
document.getElementById('btn-reset').addEventListener('click', async () => {
    if (!confirm(`¿Estás seguro de que deseas resetear el nodo ${aulaSeleccionada.nombre}?`)) {
        return;
    }

    console.log('Reseteando nodo:', aulaSeleccionada.mac);
    
    // TODO: Enviar comando de reset al ESP32
    // await fetch(`/api/aulas/${aulaSeleccionada.id}/reset`, { method: 'POST' });

    alert('🔄 Comando de reset enviado al dispositivo');
});

// Cancelar edición
document.getElementById('btn-cancel').addEventListener('click', () => {
    aulaSeleccionada = null;
    document.getElementById('form-container').classList.remove('active');
    document.getElementById('empty-state').classList.add('active');
    renderAulas();
});

// Test de conexión
document.getElementById('btn-test').addEventListener('click', async () => {
    console.log('Testeando conexión con:', aulaSeleccionada.mac);
    
    // TODO: Ping al dispositivo
    // const response = await fetch(`/api/aulas/${aulaSeleccionada.id}/ping`);
    
    alert('🧪 Prueba de conexión enviada. Revisa los logs del dispositivo.');
});

// Inicializar
renderAulas();
