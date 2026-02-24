
Preferences queuePrefs;

const int MAX_QUEUE_SIZE = 50;
const String QUEUE_NAMESPACE = "offline_q";

struct QueuedEvent {
  String tipo;
  String data;
  unsigned long timestamp;
  int intentos;
  bool pendiente;
};

// Guardar evento en cola
bool saveToQueue(String tipo, String jsonData, unsigned long eventTimestamp) {
  queuePrefs.begin(QUEUE_NAMESPACE.c_str(), false);
  
  int queueSize = queuePrefs.getInt("size", 0);
  if (queueSize >= MAX_QUEUE_SIZE) {
    Serial.println("⚠️ Cola llena, descartando evento más antiguo");
    queuePrefs.end();
    return false;
  }
  
  String key = "evt_" + String(queueSize);
  
  StaticJsonDocument<512> doc;
  doc["tipo"] = tipo;
  doc["data"] = jsonData;
  doc["timestamp"] = eventTimestamp;
  doc["intentos"] = 0;
  doc["pendiente"] = true;
  
  String serialized;
  serializeJson(doc, serialized);
  
  queuePrefs.putString(key.c_str(), serialized);
  queuePrefs.putInt("size", queueSize + 1);
  queuePrefs.end();
  
  Serial.println("💾 Evento guardado en cola: " + key);
  return true;
}

// Obtener eventos pendientes
int getPendingCount() {
  queuePrefs.begin(QUEUE_NAMESPACE.c_str(), true);
  int count = queuePrefs.getInt("size", 0);
  queuePrefs.end();
  return count;
}

// Funciones auxiliares para reenviar
bool reenviarFichaje(String jsonData, unsigned long timestamp) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonData);
  if (error) {
    Serial.println("❌ Error deserializando fichaje");
    return false;
  }
  
  String uid = doc["uid"];
  return registrarAsistenciaConTimestamp(uid, timestamp);
}

bool reenviarSensores(String jsonData, unsigned long timestamp) {
  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, jsonData);
  if (error) {
    Serial.println("❌ Error deserializando sensores");
    return false;
  }
  
  float temp = doc["temperatura"];
  float hum = doc["humedad"];
  float lux = doc["luz"];
  int personas = doc["personas"];
  
  return enviarValoresConTimestamp(temp, hum, lux, personas, timestamp);
}

// Procesar cola (reintento de envíos)
void processQueue() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  queuePrefs.begin(QUEUE_NAMESPACE.c_str(), false);
  int queueSize = queuePrefs.getInt("size", 0);
  
  if (queueSize == 0) {
    queuePrefs.end();
    return;
  }
  
  Serial.println("📤 Procesando cola offline (" + String(queueSize) + " eventos)");
  
  for (int i = 0; i < queueSize; i++) {
    String key = "evt_" + String(i);
    String serialized = queuePrefs.getString(key.c_str(), "");
    
    if (serialized.length() == 0) continue;
    
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, serialized);
    if (error) continue;
    
    String tipo = doc["tipo"];
    String data = doc["data"];
    unsigned long timestamp = doc["timestamp"];
    int intentos = doc["intentos"];
    
    bool exito = false;
    if (tipo == "fichaje") {
      exito = reenviarFichaje(data, timestamp);
    } else if (tipo == "sensores") {
      exito = reenviarSensores(data, timestamp);
    }
    
    if (exito) {
      queuePrefs.remove(key.c_str());
      Serial.println("✅ Evento reenviado: " + key);
    } else {
      doc["intentos"] = intentos + 1;
      
      if (intentos >= 5) {
        queuePrefs.remove(key.c_str());
        Serial.println("❌ Evento descartado (máx intentos): " + key);
      } else {
        String updated;
        serializeJson(doc, updated);
        queuePrefs.putString(key.c_str(), updated);
        Serial.println("⚠️ Reintento fallido (" + String(intentos + 1) + "/5): " + key);
      }
    }
    
    delay(100);
  }
  
  compactQueue();
  queuePrefs.end();
}

// Compactar cola eliminando huecos
void compactQueue() {
  int newSize = 0;
  for (int i = 0; i < MAX_QUEUE_SIZE; i++) {
    String key = "evt_" + String(i);
    String value = queuePrefs.getString(key.c_str(), "");
    
    if (value.length() > 0) {
      if (i != newSize) {
        String newKey = "evt_" + String(newSize);
        queuePrefs.putString(newKey.c_str(), value);
        queuePrefs.remove(key.c_str());
      }
      newSize++;
    }
  }
  queuePrefs.putInt("size", newSize);
}

// Limpiar toda la cola (para debugging)
void clearQueue() {
  queuePrefs.begin(QUEUE_NAMESPACE.c_str(), false);
  queuePrefs.clear();
  queuePrefs.end();
  Serial.println("🗑️ Cola limpiada");
}