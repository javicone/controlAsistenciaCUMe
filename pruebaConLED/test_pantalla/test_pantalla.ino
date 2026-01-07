/*
 * ════════════════════════════════════════════════════════════════════════════
 * TEST PANTALLA TFT ST7735 - LovyanGFX (ESP32)
 * ════════════════════════════════════════════════════════════════════════════
 * 
 * Conexiones ESP32:
 *   SCK  -> GPIO 18
 *   MOSI -> GPIO 23 (SDA)
 *   DC   -> GPIO 13
 *   RST  -> GPIO 4
 *   CS   -> GPIO 15
 *   LED  -> 5V  <-- IMPORTANTE!
 *   VCC  -> 3.3V
 *   GND  -> GND
 * 
 * ════════════════════════════════════════════════════════════════════════════
 */

#define LGFX_USE_V1
#include <LovyanGFX.hpp>

// Configuración de la pantalla
class LGFX : public lgfx::LGFX_Device {
  lgfx::Panel_ST7735S _panel;
  lgfx::Bus_SPI _bus;

public:
  LGFX(void) {
    // Configuración del bus SPI
    auto cfg = _bus.config();
    cfg.spi_host = VSPI_HOST;
    cfg.spi_mode = 0;
    cfg.freq_write = 16000000;
    cfg.pin_sclk = 18;
    cfg.pin_mosi = 23;
    cfg.pin_miso = -1;
    cfg.pin_dc   = 13;
    _bus.config(cfg);
    _panel.setBus(&_bus);

    // Configuración del panel
    auto cfg2 = _panel.config();
    cfg2.pin_cs   = 15;
    cfg2.pin_rst  = 4;
    cfg2.pin_busy = -1;
    cfg2.panel_width  = 128;
    cfg2.panel_height = 160;
    cfg2.offset_x = 0;
    cfg2.offset_y = 0;
    cfg2.invert   = false;
    cfg2.rgb_order = false;
    _panel.config(cfg2);
    
    setPanel(&_panel);
  }
};

LGFX tft;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n========================================");
  Serial.println("  TEST PANTALLA ST7735 - LovyanGFX");
  Serial.println("========================================");
  Serial.println("LED conectado a 5V? (IMPORTANTE!)");
  Serial.println("========================================\n");

  // Inicializar pantalla
  Serial.println("1. Inicializando TFT...");
  tft.init();
  tft.setRotation(0);
  Serial.println("   OK");

  // Test 1: Fondo ROJO
  Serial.println("2. Pantalla ROJA...");
  tft.fillScreen(TFT_RED);
  delay(1500);

  // Test 2: Fondo VERDE
  Serial.println("3. Pantalla VERDE...");
  tft.fillScreen(TFT_GREEN);
  delay(1500);

  // Test 3: Fondo AZUL
  Serial.println("4. Pantalla AZUL...");
  tft.fillScreen(TFT_BLUE);
  delay(1500);

  // Test 4: Fondo BLANCO con texto
  Serial.println("5. Pantalla BLANCA con texto...");
  tft.fillScreen(TFT_WHITE);
  tft.setTextColor(TFT_BLACK);
  tft.setTextSize(2);
  tft.setCursor(30, 50);
  tft.println("HOLA!");
  tft.setCursor(30, 80);
  tft.println("ESP32");
  delay(2000);

  // Test 5: Fondo NEGRO con texto blanco
  Serial.println("6. Pantalla NEGRA con texto...");
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(TFT_WHITE);
  tft.setTextSize(2);
  tft.setCursor(20, 60);
  tft.println("TEST OK");
  delay(2000);

  // Test 6: Dibujar formas
  Serial.println("7. Dibujando formas...");
  tft.fillScreen(TFT_BLACK);
  tft.fillRect(10, 10, 50, 30, TFT_RED);
  tft.fillCircle(100, 80, 25, TFT_GREEN);
  tft.drawLine(0, 150, 128, 150, TFT_BLUE);

  Serial.println("\n========================================");
  Serial.println("        TEST COMPLETADO");
  Serial.println("========================================");
}

void loop() {
  static unsigned long t = 0;
  if (millis() - t > 3000) {
    t = millis();
    Serial.println("ESP32 OK");
  }
}