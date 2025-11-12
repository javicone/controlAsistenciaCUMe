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
String urlencode(const char* msg) {
  const char *hex = "0123456789ABCDEF";
  String encodedMsg = "";
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

// ====== MANEJO DE ERRORES DE SENSORES ======
// indicarEstado() se implementa en indicators.ino
// Eliminada definición duplicada