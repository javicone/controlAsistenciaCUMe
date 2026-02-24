// Función para convertir una cadena de fecha/hora ("YYYY-MM-DD HH:MM:SS") a epoch (en segundos)
// IMPORTANTE: Esta función es un ejemplo. En un proyecto real, se recomienda sincronizar el ESP32 mediante NTP
// y utilizar una biblioteca de manejo de tiempo (por ejemplo, TimeLib) para realizar la conversión.
unsigned long epochFromString(String timeStr) {
  // Este es un ejemplo simplificado que debes ajustar según el formato y la zona horaria.
  // Supongamos que la fecha/hora es "2025-03-01 08:00:00"
  int year = timeStr.substring(0, 4).toInt();
  int month = timeStr.substring(5, 7).toInt();
  int day = timeStr.substring(8, 10).toInt();
  int hour = timeStr.substring(11, 13).toInt();
  int minute = timeStr.substring(14, 16).toInt();
  int second = timeStr.substring(17, 19).toInt();
  
  // Aquí se debe convertir a epoch. Puedes usar la función mktime si dispones de la estructura tm.
  // Por simplicidad, se asume que tienes una función que realice esta conversión.
  // Este es un pseudo-código:
  struct tm t;
  t.tm_year = year - 1900; // años desde 1900
  t.tm_mon = month - 1;    // meses 0-11
  t.tm_mday = day;
  t.tm_hour = hour;
  t.tm_min = minute;
  t.tm_sec = second;
  t.tm_isdst = -1;         // Desconocido
  time_t epoch = mktime(&t); // epoch en segundos
  return (unsigned long) epoch;
}

// Esta función convierte el array de bytes uid[] en un String hexadecimal
String uidToString(uint8_t *uidArray, size_t uidLength) {
  String uidString = "";
  for (size_t i = 0; i < uidLength; i++) {
    // Para cada byte, convertimos a hex y agregamos a la cadena
    if (uidArray[i] < 0x10) {
      uidString += "0";  // si es menor a 0x10, anteponer '0' para 2 dígitos
    }
    uidString += String(uidArray[i], HEX);
  }
  uidString.toUpperCase();  // Opcional: poner en mayúsculas
  return uidString;
}

// Función para hacer URL encode (simple)
String urlencode(String str) {
  const char *hex = "0123456789ABCDEF";
  String encodedMsg = "";
  const char* msg = str.c_str();
  while (*msg != '\0') {
    if (('a' <= *msg && *msg <= 'z') ||
        ('A' <= *msg && *msg <= 'Z') ||
        ('0' <= *msg && *msg <= '9')) {
      encodedMsg += *msg;
    } else {
      encodedMsg += '%';
      encodedMsg += hex[*msg >> 4];
      encodedMsg += hex[*msg & 15];
    }
    msg++;
  }
  return encodedMsg;
}

// ============================================
// SISTEMA DE TIMER PARA FIN DE CLASE
// ============================================

// ISR del timer - se ejecuta cuando termina la clase
void IRAM_ATTR onTimerFinClase() {
  timerFinClaseDisparado = true;  // Solo marcar el flag, el procesamiento se hace en loop()
}

// Calcula el tiempo restante hasta fin de clase e inicia el timer
void iniciarTimerFinClase() {
  if (horaFinClase.length() == 0) {
    Serial.println("⚠️ No hay hora de fin de clase definida");
    return;
  }
  
  // Obtener hora actual
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("❌ Error obteniendo hora local para timer");
    return;
  }
  
  // Parsear hora de fin de clase (formato "HH:MM" o "HH:MM:SS")
  int horaFin = horaFinClase.substring(0, 2).toInt();
  int minFin = horaFinClase.substring(3, 5).toInt();
  int segFin = 0;
  if (horaFinClase.length() >= 8) {
    segFin = horaFinClase.substring(6, 8).toInt();
  }
  
  // Calcular segundos restantes hasta fin de clase
  int segundosActual = timeinfo.tm_hour * 3600 + timeinfo.tm_min * 60 + timeinfo.tm_sec;
  int segundosFin = horaFin * 3600 + minFin * 60 + segFin;
  int segundosRestantes = segundosFin - segundosActual;
  
  // Si ya pasó la hora de fin, no iniciar timer
  if (segundosRestantes <= 0) {
    Serial.println("⚠️ La clase ya debería haber terminado");
    timerFinClaseDisparado = true;  // Forzar consulta de nueva clase
    return;
  }
  
  Serial.printf("⏱️ Timer configurado: %d minutos %d segundos hasta fin de clase (%s)\n", 
                segundosRestantes / 60, segundosRestantes % 60, horaFinClase.c_str());
  
  // Detener timer anterior si existe
  if (timerFinClase != NULL) {
    timerStop(timerFinClase);
    timerDetachInterrupt(timerFinClase);
    timerEnd(timerFinClase);
  }
  
  // Configurar timer hardware con la nueva API (ESP32 Core 3.x)
  // Frecuencia: 1 MHz (1 tick por microsegundo)
  timerFinClase = timerBegin(1000000);  // 1 MHz
  timerAttachInterrupt(timerFinClase, &onTimerFinClase);  // Adjuntar ISR
  timerAlarm(timerFinClase, (uint64_t)segundosRestantes * 1000000, false, 0);  // Alarma en microsegundos, no repetir
  timerStart(timerFinClase);  // Iniciar timer
  
  Serial.println("✅ Timer de fin de clase iniciado");
}

// Resetea el estado de fichaje y consulta nueva clase
void resetearEstadoFichaje() {
  Serial.println("\n🔄 === RESET DE ESTADO DE FICHAJE ===");
  
  // Resetear flags
  fichajeClaseCompletado = false;
  timerFinClaseDisparado = false;
  
  // Detener timer si está corriendo
  if (timerFinClase != NULL) {
    timerStop(timerFinClase);
  }
  
  // Consultar nueva clase
  obtenerProximaClase();
  
  if (claseEnCurso) {
    Serial.println("📚 Nueva clase detectada - NFC habilitado para fichaje");
  } else {
    Serial.println("😴 No hay clase - NFC permanece deshabilitado");
  }
}

// ====== MANEJO DE ERRORES DE SENSORES ======
// indicarEstado() se implementa en indicators.ino
// Eliminada definición duplicada