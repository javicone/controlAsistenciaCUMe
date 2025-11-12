import logging
import asyncio
import threading
import json
from flask import Flask, request, jsonify, render_template
import websockets
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
from database import conectar_db
from config import SECRET_KEY
from datetime import datetime

# Configuración de logging para que se muestren todos los mensajes en consola
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
                    
app = Flask(__name__, template_folder="templates", static_folder="static")
##app.config["JWT_SECRET_KEY"] = SECRET_KEY
jwt = JWTManager(app)

# Diccionario en memoria para almacenar el estado de cada aula
aulas_estado = {}

# Conjunto de clientes WebSocket conectados
connected_clients = set()

###############################################################################
# FLASK: ENDPOINTS REST
###############################################################################
@app.route('/')
def index():
    # Retorna la plantilla index.html como portal de inicio
    return render_template('index.html')

# Login de usuario basado en correo y contraseña
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    correo = data.get("correo")
    password = data.get("password")
    
    conexion = conectar_db()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, uid_tarjeta, rol, correo, password FROM usuarios WHERE correo = %s",
        (correo,)
    )
    usuario = cursor.fetchone()
    conexion.close()

    if usuario:
        # Validar contraseña (en producción, usar hash y una función de verificación)
        if usuario["password"] != password:
            return jsonify({"error": "Contraseña incorrecta"}), 401

        # Generar el token usando el id (como cadena) e incluyendo el rol y el correo en los claims adicionales
        #token = create_access_token(identity={"id": usuario["id"]})
        
        token = create_access_token(identity=str(usuario["id"]),
            additional_claims={"rol": usuario["rol"], "correo": usuario["correo"]}
        )
        return jsonify({"token": token, "rol": usuario["rol"]})
    else:
        return jsonify({"error": "Correo no encontrado"}), 401

# Login de usuario basado en correo y contraseña
@app.route('/login_aula', methods=['POST'])
def login_aula():
    data = request.get_json()
    nombre_aula = data.get("nombre_aula")
    password_aula = data.get("password_aula")
    
    logging.debug("Recibido nombre de aula: %s", nombre_aula)
    
    conexion = conectar_db()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, nombre, password_aula FROM aulas WHERE nombre = %s",
        (nombre_aula,)
    )
    aula = cursor.fetchone()
    conexion.close()

    if aula:
        # Validar contraseña (en producción, usar hash y una función de verificación)
        if aula["password_aula"] != password_aula:
            return jsonify({"error": "Contraseña incorrecta"}), 401

        # Generar el token usando el id (como cadena) e incluyendo el rol y el correo en los claims adicionales
        #token = create_access_token(identity={"id": usuario["id"]})
        
        token_aula = create_access_token(identity=str(aula["id"]),
            additional_claims={"nombre_aula": aula["nombre"], "password_aula": aula["password_aula"]}
        )
        return jsonify({"token": token_aula})
    else:
        return jsonify({"error": "Aula no encontrada"}), 401
        
# Página de dashboard después del login
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
    
# Página de dashboard después del login
@app.route('/conserjes')
def conserjes():
    return render_template('conserjes.html')

# Ruta para que los dispositivos registren asistencia desde el aula
@app.route('/registro', methods=['POST'])

def registrar_asistencia():
    
    data = request.get_json()
    uid = data.get("uid")
    nombre_aula = data.get("nombre_aula")

    if not uid or len(uid) > 20:
        return jsonify({"error": "UID inválido"}), 400
        
    logging.debug("Recibido UID válido", uid)
    
    conexion = conectar_db()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    cursor = conexion.cursor(dictionary=True)
    
    # Consultar la tabla de usuarios para obtener el usuario_id basado en el UID de la tarjeta
    cursor.execute("SELECT id FROM usuarios WHERE uid_tarjeta = %s", (uid,))
    usuario = cursor.fetchone()
    if not usuario:
        conexion.close()
        return jsonify({"error": "Profesor no encontrado"}), 404
    usuario_id = usuario["id"]
    
    # Consultar la tabla de aulas para obtener el aula_id basado en el nombre del aula
    cursor.execute("SELECT id FROM aulas WHERE nombre = %s", (nombre_aula,))
    aula = cursor.fetchone()
    if not aula:
        conexion.close()
        return jsonify({"error": "Aula no encontrada"}), 404
    aula_id = aula["id"]
    
    #Obtengo los datos del registro de profesor
    profesor = cursor.fetchone()
    
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Insertar el registro de asistencia en la tabla
        cursor.execute(
            "INSERT INTO asistencias (usuario_id, aula_id, fecha_hora) VALUES (%s, %s, %s)",
            (usuario_id, aula_id, fecha_hora)
        )
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        conexion.close()
        return jsonify({"error": "Error al insertar asistencia", "detalle": str(e)}), 500
    
    conexion.close()
    return jsonify({
        "mensaje": "Asistencia registrada",
        "usuario_id": usuario_id,
        "aula_id": aula_id,
        "fecha_hora": fecha_hora
    }), 200

# Consultar asistencias (según rol)
@app.route('/asistencias', methods=['GET'])
@jwt_required()
def obtener_asistencias():
    claims = get_jwt()
    rol = claims.get("rol")
    
    logging.debug("Obteniendo asistencias para rol: %s", rol)
    
    conexion = conectar_db()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500
    
    cursor = conexion.cursor(dictionary=True)
    
    try:
    
        if rol == "profesor":
            profesor_id = get_jwt_identity()
            logging.debug("Obteniendo asistencias para profesor: %s", profesor_id)
            
            cursor.execute("SELECT * FROM asistencias WHERE usuario_id = %s", (profesor_id,))
            #cursor.execute("SELECT * FROM asistencias")
            
        elif rol in ["conserje", "administrador"]:
            cursor.execute("SELECT * FROM asistencias")
        else:
            return jsonify({"error": "Acceso denegado"}), 403
            
        asistencias = cursor.fetchall()
        logging.debug("Registros de asistencias: %s", asistencias)
        conexion.close()
        return jsonify(asistencias)
    
    except Exception as e:
        logging.error("Error al ejecutar la consulta: %s", e)
        print("Error al ejecutar la consulta:", e)
        return jsonify({"error": "Error interno en el servidor"}), 500

# Endpoint para obtener la próxima clase en un aula
@app.route('/proxima_clase', methods=['GET'])
def proxima_clase():
    aula = request.args.get("aula")
    
    logging.debug("Obteniendo el nombre de aula: %s", aula)
    
    if not aula:
        return jsonify({"error": "Aula requerida"}), 400

    conexion = conectar_db()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    cursor = conexion.cursor(dictionary=True)
    # Consulta: se asume que la tabla 'clases' tiene las columnas:
    # asignatura, hora_inicio, hora_fin, y que existe una relación con la tabla aulas.
    query = """
    SELECT c.asignatura, c.hora_inicio, c.hora_fin 
    FROM clases c 
    JOIN aulas a ON c.aula_id = a.id 
    WHERE a.nombre = %s AND c.hora_inicio > NOW() 
    ORDER BY c.hora_inicio ASC LIMIT 1
    """
    cursor.execute(query, (aula,))
    clase = cursor.fetchone()
    conexion.close()
    
    if not clase:
        return jsonify({"error": "No hay clases proximas"}), 404

    # Convertir las fechas a cadena
    clase["hora_inicio"] = clase["hora_inicio"].strftime("%Y-%m-%d %H:%M:%S")
    clase["hora_fin"] = clase["hora_fin"].strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(clase)
    
@app.route('/datos_aula', methods=['POST'])
def recibir_datos_aula():
    data = request.get_json()
    aula = data.get("aula")
    temperatura = data.get("temperatura")
    luz = data.get("luz")
    personas = data.get("personas")
    clase_en_curso = data.get("clase_en_curso")

    if not aula or temperatura is None or luz is None or personas is None or clase_en_curso is None:
        return jsonify({"error": "Faltan datos necesarios"}), 400

    # Actualizar en memoria
    aulas_estado[aula] = {
        "temperatura": temperatura,
        "luz": luz,
        "personas": personas,
        "clase_en_curso": clase_en_curso,
        "relay": aulas_estado.get(aula, {}).get("relay", False),
    }

    # Difundir a todos los clientes WebSocket
    asyncio.run_coroutine_threadsafe(
        broadcast({
            "tipo": "actualizacion_aula",
            "aula": aula,
            **aulas_estado[aula]
        }),
        loop
    )
    return jsonify({"mensaje": "Datos actualizados correctamente"}), 200

@app.route('/estado_aulas', methods=['GET'])
def obtener_estado_aulas():
    return jsonify(aulas_estado)

@app.route('/control_relay', methods=['POST'])
def controlar_relay():
    data = request.get_json()
    aula = data.get("aula")
    estado_relay = data.get("relay")

    if aula not in aulas_estado:
        return jsonify({"error": "Aula no encontrada"}), 404

    if aulas_estado[aula].get("relay") != estado_relay:
        aulas_estado[aula]["relay"] = estado_relay

        # Difundir a todos los clientes WebSocket
        asyncio.run_coroutine_threadsafe(
            broadcast({
                "tipo": "actualizacion_relay",
                "aula": aula,
                "relay": estado_relay
            }),
            loop
        )

        return jsonify({"mensaje": "Estado del relé actualizado", "aula": aula, "relay": estado_relay})
    else:
        return jsonify({"mensaje": "El estado del relé ya está actualizado"}), 200
        
def listar_clientes_conectados():
    """
    Retorna una lista con la dirección remota de cada cliente conectado.
    Por ejemplo: ['192.168.246.120:62653', '192.168.246.46:57833', ...]
    """
    listado = []
    for ws in connected_clients:
        # ws.remote_address suele ser una tupla (host, port)
        if ws.remote_address:
            host, port = ws.remote_address
            listado.append(f"{host}:{port}")
    return listado

###############################################################################
# WEBSOCKETS PUROS
###############################################################################
async def ws_handler(websocket):
    """
    Manejador de conexiones WebSocket:
    - Agrega al cliente a connected_clients.
    - Envía el estado_inicial si quieres.
    - Recibe mensajes del cliente (si enviaran algo).
    """
    print("✅ Un cliente WebSocket se ha conectado.")
    connected_clients.add(websocket)

    # Al conectar, podemos mandarles el estado actual de todas las aulas
    # para que la web renderice todo de inmediato.
    await websocket.send(json.dumps({
        "tipo": "estado_inicial",
        "data": aulas_estado
    }))

    try:
        async for message in websocket:
            # Si el cliente envía algo (raro en la web),
            # podrías parsear y responder.
            print("📩 Mensaje recibido del cliente:", message)
    except Exception as e:
        print("❌ Error en la conexión WS:", e)
        print("Lista actual de clientes conectados:", listar_clientes_conectados())
    finally:
        connected_clients.remove(websocket)
        print("❌ Un cliente WS se ha desconectado.")
        print("Lista actual de clientes conectados:", listar_clientes_conectados())
       

async def broadcast(event: dict):
    if not connected_clients:
        return
    message = json.dumps(event)
    print(f"Enviando mensaje WebSocket a todos: {message}")

    for ws in connected_clients:
        try:
            await ws.send(message)
            # Confirmación de envío
            print(f"✔️ Enviado con éxito a {ws.remote_address}")
        except Exception as e:
            # Si algo falla, lo registras
            print(f"❌ Error al enviar a {ws.remote_address}: {e}")

###############################################################################
# ARRANQUE CONCURRENTE: FLASK + WEBSOCKETS
###############################################################################
async def start_websocket_server():
    """
    Arranca el servidor de websockets en el puerto 5678 (por ejemplo).
    """
    #server = await websockets.serve(ws_handler, "0.0.0.0", 5678)
    server = await websockets.serve(ws_handler, "0.0.0.0", 5678, ping_interval=None)
    print("Servidor WebSocket en puerto 5678")
    await server.wait_closed()

def run_flask():
    """
    Ejecuta Flask en el puerto 5000.
    """
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    # Usamos new_event_loop para evitar deprecation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Iniciar websockets en paralelo
    ws_task = loop.create_task(start_websocket_server())

    # Iniciar Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Mantener el bucle de eventos (websockets) corriendo
    loop.run_forever()
