import sys, os
sys.path.insert(0, r'd:\UEX\ControlAsistencia\.claude\skills\docx')
from scripts.document import Document

# Fresh unpack
doc = Document(r'd:\UEX\ControlAsistencia\unpacked_template')
xml = doc["word/document.xml"]

def get_all_text(element):
    """Recursively get all text content from an element, handling entity refs."""
    result = []
    for child in element.childNodes:
        if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE):
            result.append(child.data)
        elif child.nodeType == child.ELEMENT_NODE:
            result.append(get_all_text(child))
    return ''.join(result)

def find_heading(dom, style, text_fragment, text_fragment2=None):
    """Find a paragraph by style and text content."""
    for p in dom.getElementsByTagName("w:p"):
        pPr = p.getElementsByTagName("w:pPr")
        if not pPr:
            continue
        pStyle = pPr[0].getElementsByTagName("w:pStyle")
        if not pStyle:
            continue
        if pStyle[0].getAttribute("w:val") != style:
            continue
        # Get full text including entities
        text_parts = []
        for t in p.getElementsByTagName("w:t"):
            text_parts.append(get_all_text(t))
        text = "".join(text_parts)
        if text_fragment in text:
            if text_fragment2 is None or text_fragment2 in text:
                return p
    return None

# ============ 1. Diagrama de Flujo del Nodo ============
node = find_heading(xml.dom, "Ttulo3", "Diagrama de Flujo")
assert node, "Could not find 'Diagrama de Flujo del Nodo'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t xml:space="preserve">El firmware del nodo ESP32 sigue una arquitectura de doble n\u00facleo (dual-core) que separa las tareas de comunicaci\u00f3n de las tareas de lectura de sensores:</w:t></w:r>
</w:p>
<w:p>
  <w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>N\u00facleo 0 (Core 0) - Comunicaciones:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Gesti\u00f3n de la conexi\u00f3n WiFi con reconexiones autom\u00e1ticas.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Autenticaci\u00f3n JWT contra el servidor para obtener tokens de acceso.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Mantenimiento de la conexi\u00f3n WebSocket persistente (WSS) para env\u00edo de datos de sensores y recepci\u00f3n de comandos.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Gesti\u00f3n de la cola de env\u00edo offline (NVS) para mensajes pendientes por falta de conexi\u00f3n.</w:t></w:r></w:p>
<w:p>
  <w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>N\u00facleo 1 (Core 1) - Sensores y Actuadores:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Lectura peri\u00f3dica de sensores ambientales: BME280 (temperatura, humedad, presi\u00f3n), BH1750 (luminosidad), LD2410 (presencia mediante radar 24GHz).</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Lectura continua del m\u00f3dulo NFC (PN532 por SPI) para detectar tarjetas RFID y registrar asistencias.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Control de actuadores: Rel\u00e9 1 (climatizaci\u00f3n) y Rel\u00e9 2 (iluminaci\u00f3n) con l\u00f3gica activa LOW.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Gesti\u00f3n de indicadores: LEDs de estado (rojo/amarillo/verde), buzzer para confirmaci\u00f3n de fichaje y pantalla OLED.</w:t></w:r></w:p>
<w:p>
  <w:r><w:t xml:space="preserve">El flujo principal es: Al encender, el ESP32 inicializa sensores y perif\u00e9ricos, se conecta a WiFi, solicita un token JWT mediante device_id y api_key, y establece conexi\u00f3n WebSocket. En operaci\u00f3n, cada 5 segundos lee sensores, cada 30 segundos env\u00eda datos agregados al servidor, y escucha continuamente el NFC para fichajes. Los comandos recibidos por WebSocket (rel\u00e9s, reset, configuraci\u00f3n) se procesan inmediatamente.</w:t></w:r>
</w:p>''')
print("1/9 Diagrama de Flujo OK")

# ============ 2. Mecanismos de Ciberseguridad aplicados ============
node = find_heading(xml.dom, "Ttulo3", "Mecanismos de Ciberseguridad")
assert node, "Could not find 'Mecanismos de Ciberseguridad'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>Se han implementado los siguientes mecanismos de ciberseguridad en el firmware del ESP32:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Autenticaci\u00f3n JWT (JSON Web Tokens) con RS256:</w:t></w:r></w:p>
<w:p><w:r><w:t>El nodo se autentica contra el servidor utilizando un device_id y una api_key \u00fanicos. El servidor genera un token JWT firmado con clave privada RSA (RS256) que el dispositivo almacena y utiliza en todas las comunicaciones posteriores. Si el token expira, el nodo solicita autom\u00e1ticamente uno nuevo.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Comunicaci\u00f3n cifrada HTTPS/WSS:</w:t></w:r></w:p>
<w:p><w:r><w:t>Todas las comunicaciones entre el ESP32 y el servidor se realizan sobre TLS, tanto para las peticiones REST (HTTPS) como para el canal WebSocket (WSS), mediante certificado SSL.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Validaci\u00f3n de datos de sensores:</w:t></w:r></w:p>
<w:p><w:r><w:t>Antes de enviar datos al servidor, el firmware valida los rangos (temperatura -40\u00b0C a 85\u00b0C, humedad 0-100%, luminosidad 0-65535 lux, presi\u00f3n 300-1100 hPa) para evitar lecturas err\u00f3neas.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Cola offline persistente (NVS):</w:t></w:r></w:p>
<w:p><w:r><w:t>Los mensajes de asistencia que no pueden enviarse se almacenan en la memoria NVS (Non-Volatile Storage) del ESP32 y se reenv\u00edan autom\u00e1ticamente al recuperar la conexi\u00f3n, garantizando que ning\u00fan fichaje se pierda.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Validaci\u00f3n de UID NFC:</w:t></w:r></w:p>
<w:p><w:r><w:t>Los identificadores de tarjetas NFC se validan en formato hexadecimal (ISO14443A) antes de ser enviados al servidor, previniendo inyecciones de datos maliciosos.</w:t></w:r></w:p>''')
print("2/9 Mecanismos Ciberseguridad OK")

# ============ 3. Servidor FastApi (Titulo2) ============
node = find_heading(xml.dom, "Ttulo2", "Servidor", "FastApi")
assert node, "Could not find 'Servidor FastApi'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>El backend del sistema est\u00e1 desarrollado en Python utilizando el framework FastAPI, ejecutado sobre el servidor ASGI Uvicorn en el puerto 8000. El servidor gestiona toda la l\u00f3gica de negocio, la autenticaci\u00f3n de usuarios y dispositivos, la comunicaci\u00f3n en tiempo real mediante WebSocket, el servicio de p\u00e1ginas web y la interacci\u00f3n con la base de datos MySQL.</w:t></w:r>
</w:p>
<w:p>
  <w:r><w:t>El sistema incorpora capas de seguridad middleware: validaci\u00f3n de entrada (InputValidationMiddleware) que previene inyecciones SQL, XSS y command injection; rate limiting mediante SlowAPI con l\u00edmites de 5 intentos/minuto en login, 10/minuto en autenticaci\u00f3n de dispositivos y 200/minuto global; configuraci\u00f3n CORS; y logging de peticiones para auditor\u00eda.</w:t></w:r>
</w:p>''')
print("3/9 Servidor FastApi OK")

# ============ 4. Por qué FastApi (Titulo3) ============
node = find_heading(xml.dom, "Ttulo3", "FastApi", "qu")
assert node, "Could not find 'Por qué FastApi'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>Se ha seleccionado FastAPI como framework por las siguientes razones:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Alto rendimiento as\u00edncrono:</w:t></w:r><w:r><w:t xml:space="preserve"> Basado en Starlette y Uvicorn (ASGI), permite manejar m\u00faltiples conexiones WebSocket simult\u00e1neas de forma eficiente, esencial para la comunicaci\u00f3n en tiempo real con los nodos ESP32.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Validaci\u00f3n autom\u00e1tica con Pydantic:</w:t></w:r><w:r><w:t xml:space="preserve"> Los modelos de datos se validan autom\u00e1ticamente en tipos, rangos y formatos, previniendo inyecciones y datos malformados.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Soporte nativo de WebSocket:</w:t></w:r><w:r><w:t xml:space="preserve"> A diferencia de Flask, FastAPI soporta nativamente conexiones WebSocket, imprescindible para la arquitectura de 3 roles del sistema.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Documentaci\u00f3n OpenAPI autom\u00e1tica:</w:t></w:r><w:r><w:t xml:space="preserve"> Genera Swagger UI interactivo, facilitando las pruebas y el mantenimiento.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Soporte SSL/TLS nativo:</w:t></w:r><w:r><w:t xml:space="preserve"> Uvicorn ofrece HTTPS integrado mediante certificados SSL, sin necesidad de proxy reverso.</w:t></w:r></w:p>
<w:p>
  <w:r><w:t>El proyecto inici\u00f3 con Flask pero se migr\u00f3 a FastAPI por sus limitaciones con WebSockets y conexiones as\u00edncronas.</w:t></w:r>
</w:p>''')
print("4/9 Por que FastApi OK")

# ============ 5. Endpoints (Titulo3) ============
node = find_heading(xml.dom, "Ttulo3", "Endpoints")
assert node, "Could not find 'Endpoints'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>El servidor expone los siguientes grupos de endpoints:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Autenticaci\u00f3n (/auth/):</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>POST /auth/login: Autenticaci\u00f3n de usuarios (correo + contrase\u00f1a) con devoluci\u00f3n de token JWT.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>POST /auth/device: Autenticaci\u00f3n de dispositivos ESP32 (device_id + api_key).</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Asistencias (/asistencias/):</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>POST /asistencias/registro: Registro de fichaje con UID de tarjeta NFC, device_id y timestamp.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /asistencias/historial: Consulta del historial de asistencias filtrado por aula y fecha.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Aulas (/aulas/):</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /aulas/estado_aulas: Estado de todas las aulas (temperatura, humedad, luminosidad, presencia, rel\u00e9s).</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>POST /aulas/control_relay: Control de rel\u00e9s de climatizaci\u00f3n e iluminaci\u00f3n (solo administradores y conserjes).</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Clases (/clases/):</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /clases/proxima_clase: Pr\u00f3xima clase programada para un aula.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /clases/por_profesor/{profesor}: Clases asignadas a un profesor.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>WebSocket (tiempo real):</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /ws?token=JWT: Conexi\u00f3n para dispositivos ESP32.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /ws/admin?token=JWT: Canal de administradores con control completo.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /ws/conserje?token=JWT: Canal de conserjes con monitorizaci\u00f3n y control de rel\u00e9s.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Vistas HTML:</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>GET /: Login. GET /dashboard: Panel principal. GET /administrador: Panel admin. GET /conserjes: Panel conserjes. GET /asistencias_profesor: Vista asistencias.</w:t></w:r></w:p>
<w:p>
  <w:r><w:t>Todos los endpoints protegidos requieren token JWT v\u00e1lido con el scope adecuado (admin, conserje, profesor o device) en la cabecera Authorization.</w:t></w:r>
</w:p>''')
print("5/9 Endpoints OK")

# ============ 6. Organización del código (Titulo3) ============
node = find_heading(xml.dom, "Ttulo3", "digo")
assert node, "Could not find 'Organizacion del codigo'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>El c\u00f3digo del servidor sigue una arquitectura en capas con separaci\u00f3n clara de responsabilidades:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>routers/:</w:t></w:r><w:r><w:t xml:space="preserve"> Definici\u00f3n de endpoints HTTP y WebSocket, agrupados por dominio (auth.py, asistencias.py, aulas.py, clases.py, websockets.py, views.py).</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>services/:</w:t></w:r><w:r><w:t xml:space="preserve"> L\u00f3gica de negocio por dominio (auth_service.py, asistencia_service.py, aula_service.py, clase_service.py).</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>models/:</w:t></w:r><w:r><w:t xml:space="preserve"> Modelos Pydantic con validaci\u00f3n de tipos, rangos y formatos (user.py, aula.py, asistencia.py, clase.py, webTokens.py).</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>repositories/:</w:t></w:r><w:r><w:t xml:space="preserve"> Capa de acceso a datos con consultas SQL parametrizadas contra MySQL.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>middleware/:</w:t></w:r><w:r><w:t xml:space="preserve"> Capas transversales de seguridad: cors.py, input_validation.py, logging.py, rate_limit.py.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>utils/:</w:t></w:r><w:r><w:t xml:space="preserve"> Pool de conexiones (database_pool.py) y gestor centralizado de WebSockets (websocket_manager.py).</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>security/:</w:t></w:r><w:r><w:t xml:space="preserve"> Utilidades JWT, hashing bcrypt y sanitizaci\u00f3n de entrada.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>templates/:</w:t></w:r><w:r><w:t xml:space="preserve"> Plantillas HTML Jinja2 para las interfaces web.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>static/:</w:t></w:r><w:r><w:t xml:space="preserve"> Archivos CSS y JavaScript para el frontend responsivo.</w:t></w:r></w:p>
<w:p>
  <w:r><w:t>El punto de entrada es appFastApi.py, que configura la aplicaci\u00f3n, registra routers y arranca Uvicorn con soporte SSL opcional.</w:t></w:r>
</w:p>''')
print("6/9 Organizacion del codigo OK")

# ============ 7. Persistencia. Base de datos SQL (Titulo2) ============
node = find_heading(xml.dom, "Ttulo2", "Persistencia")
assert node, "Could not find 'Persistencia'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>La persistencia se implementa mediante MySQL 8.0, desplegada en un contenedor Docker. La conexi\u00f3n desde FastAPI se realiza mediante un pool de conexiones as\u00edncronas (aiomysql) que optimiza el rendimiento reutilizando conexiones existentes.</w:t></w:r>
</w:p>
<w:p><w:r><w:t>El esquema consta de las siguientes tablas principales:</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>usuarios:</w:t></w:r><w:r><w:t xml:space="preserve"> Nombre, correo, contrase\u00f1a (bcrypt), rol (administrador/profesor/conserje) y UID de tarjeta NFC.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>asistencias:</w:t></w:r><w:r><w:t xml:space="preserve"> Registro hist\u00f3rico de fichajes con referencia a usuario, aula, clase en curso y timestamp.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>aulas:</w:t></w:r><w:r><w:t xml:space="preserve"> Nombre, edificio, planta, capacidad, device_id del nodo ESP32 y configuraci\u00f3n de rel\u00e9s.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>clases:</w:t></w:r><w:r><w:t xml:space="preserve"> Horario con asignatura, profesor, aula, d\u00eda de la semana, hora inicio y fin.</w:t></w:r></w:p>
<w:p><w:r><w:t>Todas las consultas SQL utilizan par\u00e1metros preparados (parameterized queries) a trav\u00e9s de la capa de repositorios, previniendo inyecci\u00f3n SQL. El backup se almacena en Database/backupControlAsistencia.sql.</w:t></w:r></w:p>''')
print("7/9 Persistencia OK")

# ============ 8. Flujo de datos y Arquitectura (Titulo2) ============
node = find_heading(xml.dom, "Ttulo2", "Flujo de datos")
assert node, "Could not find 'Flujo de datos'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>La arquitectura se basa en dos flujos de datos diferenciados:</w:t></w:r>
</w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Flujo REST (HTTPS) - Fichajes y autenticaci\u00f3n:</w:t></w:r></w:p>
<w:p><w:r><w:t>Cuando un profesor pasa su tarjeta NFC, el ESP32 env\u00eda POST a /asistencias/registro con el UID. El servidor valida el JWT, identifica al usuario, registra la asistencia y devuelve confirmaci\u00f3n con nombre y asignatura. Simult\u00e1neamente notifica por WebSocket a administradores y conserjes.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Flujo WebSocket (WSS) - Sensores, comandos y monitorizaci\u00f3n:</w:t></w:r></w:p>
<w:p><w:r><w:t>Arquitectura WebSocket de 3 roles gestionada por un ConnectionManager centralizado (patr\u00f3n Singleton):</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Dispositivos (/ws):</w:t></w:r><w:r><w:t xml:space="preserve"> Env\u00edan datos de sensores cada 30 segundos y notificaciones de fichaje. Reciben comandos de control de rel\u00e9s, reset, test y configuraci\u00f3n.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Administradores (/ws/admin):</w:t></w:r><w:r><w:t xml:space="preserve"> Reciben todos los datos en tiempo real. Pueden configurar nodos, resetear dispositivos y controlar rel\u00e9s.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Conserjes (/ws/conserje):</w:t></w:r><w:r><w:t xml:space="preserve"> Monitorizaci\u00f3n en tiempo real y control de rel\u00e9s, sin permisos de configuraci\u00f3n ni reset.</w:t></w:r></w:p>
<w:p><w:r><w:t>El ConnectionManager proporciona m\u00e9todos de enrutamiento: send_to_device() para unicast a un ESP32, notify_admins() y notify_conserjes() para broadcast selectivo, y notify_staff() para broadcast combinado a todo el personal.</w:t></w:r></w:p>''')
print("8/9 Flujo de datos OK")

# ============ 9. Diseño PCB, Carcasa, LoRa (Titulo2) ============
node = find_heading(xml.dom, "Ttulo2", "placa de circuito")
assert node, "Could not find 'Diseño de placa'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>Se ha dise\u00f1ado una PCB personalizada que integra: bus I2C (SDA GPIO21, SCL GPIO22) para BME280, BH1750 y OLED; bus SPI (MOSI GPIO23, MISO GPIO19, SCK GPIO18, CS GPIO5) para el NFC PN532; UART2 (RX GPIO16, TX GPIO17) para el radar LD2410; y salidas GPIO para rel\u00e9s (GPIO26, GPIO32), LEDs (GPIO25, GPIO27, GPIO14) y buzzer (GPIO33). Esto reemplaza la protoboard del prototipado, mejorando fiabilidad y facilitando la producci\u00f3n en serie.</w:t></w:r>
</w:p>''')

node = find_heading(xml.dom, "Ttulo2", "carcasa para el prototipo")
assert node, "Could not find 'Diseño de carcasa'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>Se ha dise\u00f1ado una carcasa para fabricaci\u00f3n mediante impresi\u00f3n 3D que aloja el prototipo completo. Contempla apertura para la pantalla OLED, zona de aproximaci\u00f3n para lectura NFC, orificios de ventilaci\u00f3n para el BME280, y ventana para los LEDs indicadores. Est\u00e1 pensada para montaje en pared junto a la entrada del aula.</w:t></w:r>
</w:p>''')

node = find_heading(xml.dom, "Ttulo2", "Viabilidad")
assert node, "Could not find 'Viabilidad LoRa'"
xml.insert_after(node, '''<w:p>
  <w:r><w:t>Se ha estudiado la viabilidad de sustituir WiFi por LoRa (Long Range) como medio de comunicaci\u00f3n, motivado por limitaciones del WiFi: dependencia de infraestructura de red, consumo energ\u00e9tico elevado y alcance limitado en edificios densos.</w:t></w:r>
</w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Estudio de espectro en banda ISM:</w:t></w:r></w:p>
<w:p><w:r><w:t>Se ha analizado la ocupaci\u00f3n de la banda ISM (868 MHz) en el Centro Universitario de M\u00e9rida para evaluar la disponibilidad de canales libres y el nivel de interferencia.</w:t></w:r></w:p>
<w:p><w:pPr><w:rPr><w:b/><w:bCs/></w:rPr></w:pPr>
  <w:r><w:rPr><w:b/><w:bCs/></w:rPr><w:t>Protocolo LoRaLAN:</w:t></w:r></w:p>
<w:p><w:r><w:t>Se ha iniciado el desarrollo del protocolo propietario LoRaLAN con topolog\u00eda en estrella centralizada y comunicaciones Full-Duplex, optimizado para:</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Baja latencia en transmisi\u00f3n de comandos y recepci\u00f3n de datos de sensores.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Seguridad mejorada al operar en red local cerrada, reduciendo la superficie de ataque.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Bajo consumo energ\u00e9tico para operaci\u00f3n con bater\u00edas.</w:t></w:r></w:p>
<w:p><w:pPr><w:pStyle w:val="Prrafodelista"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="8"/></w:numPr></w:pPr>
  <w:r><w:t>Independencia de la infraestructura WiFi existente.</w:t></w:r></w:p>
<w:p><w:r><w:t>Esta investigaci\u00f3n se alinea con el objetivo de innovaci\u00f3n (I+D+i) en la protecci\u00f3n de infraestructuras conectadas de la C\u00e1tedra INCIBE-UEX.</w:t></w:r></w:p>''')
print("9/9 LoRa OK")

# Save everything
doc.save(validate=False)
print("Document saved successfully!")
