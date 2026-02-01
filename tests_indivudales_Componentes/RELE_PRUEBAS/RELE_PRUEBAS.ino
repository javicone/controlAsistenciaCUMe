// Definición de los pines GPIO conectados a los relés
const int RELAY_PIN_1 = 26; // Conectado al Relé 1
const int RELAY_PIN_2 = 32; // Conectado al Relé 2

// Constante para el tiempo de espera (2 segundos)
const int DELAY_TIME = 2000; 

// Nota: Los módulos de relé comunes se activan con LOW (nivel bajo).
// Si tus relés se activan con HIGH, simplemente invierte las constantes 
// en el código (ej: HIGH por LOW).
const int RELAY_ON = LOW;  // Estado para activar el relé (asumiendo relé activo bajo)
const int RELAY_OFF = HIGH; // Estado para desactivar el relé

void setup() {
  // Inicialización de la comunicación serial para depuración
  Serial.begin(115200);
  Serial.println("--- ESP32: Control de Reles ---");
  
  // Configurar los pines como salida
  pinMode(RELAY_PIN_1, OUTPUT);
  pinMode(RELAY_PIN_2, OUTPUT);
  
  // Asegurarse de que los relés estén inicialmente apagados
  digitalWrite(RELAY_PIN_1, RELAY_OFF);
  digitalWrite(RELAY_PIN_2, RELAY_OFF);
  
  Serial.println("Pines inicializados. Reles apagados.");
}

void loop() {
  
  // ===================================
  // 1. ENCENDER AMBOS RELÉS
  // ===================================
  Serial.println("Activando ambos reles (26 y 32)...");
  digitalWrite(RELAY_PIN_1, RELAY_ON);
  digitalWrite(RELAY_PIN_2, RELAY_ON);
  
  delay(DELAY_TIME); // Esperar 2 segundos
  
  // ===================================
  // 2. APAGAR AMBOS RELÉS
  // ===================================
  Serial.println("Desactivando ambos reles (26 y 32)...");
  digitalWrite(RELAY_PIN_1, RELAY_OFF);
  digitalWrite(RELAY_PIN_2, RELAY_OFF);
  
  delay(DELAY_TIME); // Esperar 2 segundos
  
  
  // ===================================
  // 3. SECUENCIA ALTERNADA
  // ===================================
  
  // Encender Relé 1, Apagar Relé 2
  Serial.println("Relé 1 ON, Relé 2 OFF...");
  digitalWrite(RELAY_PIN_1, RELAY_ON);
  digitalWrite(RELAY_PIN_2, RELAY_OFF);
  delay(DELAY_TIME);
  
  // Apagar Relé 1, Encender Relé 2
  Serial.println("Relé 1 OFF, Relé 2 ON...");
  digitalWrite(RELAY_PIN_1, RELAY_OFF);
  digitalWrite(RELAY_PIN_2, RELAY_ON);
  delay(DELAY_TIME);

}