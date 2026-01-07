/*
 * ════════════════════════════════════════════════════════════════════════════
 * MÓDULO DE PANTALLA TFT - LovyanGFX 1.2.x
 * ════════════════════════════════════════════════════════════════════════════
 * 
 * Conexiones ESP32:
 *   SCK  -> GPIO 18 (compartido con NFC)
 *   MOSI -> GPIO 23 (compartido con NFC)
 *   DC   -> GPIO 13 
 *   RST  -> GPIO 4
 *   CS   -> GPIO 15
 * 
 * Autor: Sistema de Control de Asistencia
 * Fecha: 2025
 * ════════════════════════════════════════════════════════════════════════════
 */

#define LGFX_USE_V1
#include <LovyanGFX.hpp>
#include "config.h"
#include "globals.h"

// ============================================================================
// CONFIGURACIÓN LGFX PARA ESP32
// ============================================================================

class LGFX : public lgfx::LGFX_Device {
  lgfx::Panel_ST7789 _panel_instance;
  lgfx::Bus_SPI _bus_instance;

public:
  LGFX(void) {
    {
      auto cfg = _bus_instance.config();
      cfg.spi_host = VSPI_HOST;
      cfg.spi_mode = 0;
      cfg.freq_write = 40000000;
      cfg.freq_read  = 16000000;
      cfg.spi_3wire  = false;
      cfg.use_lock   = true;
      cfg.dma_channel = SPI_DMA_CH_AUTO;
      cfg.pin_sclk = TFT_SCK;
      cfg.pin_mosi = TFT_MOSI;
      cfg.pin_miso = -1;
      cfg.pin_dc   = TFT_DC;
      _bus_instance.config(cfg);
      _panel_instance.setBus(&_bus_instance);
    }
    {
      auto cfg = _panel_instance.config();
      cfg.pin_cs   = TFT_CS;
      cfg.pin_rst  = TFT_RST;
      cfg.pin_busy = -1;
      cfg.panel_width   = 240;
      cfg.panel_height  = 320;
      cfg.offset_x      = 0;
      cfg.offset_y      = 0;
      cfg.offset_rotation = 0;
      cfg.dummy_read_pixel = 8;
      cfg.dummy_read_bits  = 1;
      cfg.readable    = false;
      cfg.invert      = true;
      cfg.rgb_order   = false;
      cfg.dlen_16bit  = false;
      cfg.bus_shared  = true;
      _panel_instance.config(cfg);
    }
    setPanel(&_panel_instance);
  }
};

LGFX tft;

// ============================================================================
// COLORES (RGB565)
// ============================================================================
#define COLOR_FONDO       TFT_BLACK
#define COLOR_TITULO      TFT_CYAN
#define COLOR_TEXTO       TFT_WHITE
#define COLOR_EXITO       TFT_GREEN
#define COLOR_ERROR       TFT_RED
#define COLOR_ADVERTENCIA TFT_YELLOW
#define COLOR_INFO        TFT_BLUE
#define COLOR_GRIS        0x7BEF

#define PANTALLA_ANCHO    240
#define PANTALLA_ALTO     320

// Estados de pantalla
enum EstadoPantalla {
  PANTALLA_INICIO,
  PANTALLA_ESPERANDO,
  PANTALLA_FICHAJE_OK,
  PANTALLA_FICHAJE_ERROR,
  PANTALLA_DATOS_AULA,
  PANTALLA_CLASE_INFO,
  PANTALLA_ERROR_SENSOR,
  PANTALLA_SIN_CONEXION
};

EstadoPantalla estadoActualPantalla = PANTALLA_INICIO;
unsigned long tiempoUltimaPantalla = 0;
const unsigned long TIEMPO_MENSAJE = 3000;

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

void setupDisplay() {
  Serial.println("\n╔════════════════════════════════╗");
  Serial.println("║  INICIALIZANDO PANTALLA TFT    ║");
  Serial.println("╚════════════════════════════════╝");
  
  tft.init();
  tft.setRotation(0);
  tft.fillScreen(COLOR_FONDO);
  tft.setTextWrap(true);
  
  Serial.println("📺 Pantalla LovyanGFX inicializada");
  Serial.printf("   SCK:  GPIO %d\n", TFT_SCK);
  Serial.printf("   MOSI: GPIO %d\n", TFT_MOSI);
  Serial.printf("   DC:   GPIO %d\n", TFT_DC);
  Serial.printf("   RST:  GPIO %d\n", TFT_RST);
  Serial.printf("   CS:   GPIO %d\n", TFT_CS);
  
  mostrarPantallaInicio();
}

// ============================================================================
// PANTALLAS PRINCIPALES
// ============================================================================

void mostrarPantallaInicio() {
  estadoActualPantalla = PANTALLA_INICIO;
  tft.fillScreen(COLOR_FONDO);
  
  // Título
  tft.setTextColor(COLOR_TITULO);
  tft.setTextSize(2);
  tft.setCursor(20, 40);
  tft.println("CONTROL DE");
  tft.setCursor(30, 70);
  tft.println("ASISTENCIA");
  
  // Línea
  tft.drawFastHLine(20, 100, 200, COLOR_TITULO);
  
  // Aula
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(1);
  tft.setCursor(20, 120);
  tft.print("Aula: ");
  tft.setTextColor(COLOR_EXITO);
  tft.println(aula.length() > 0 ? aula : "Sin configurar");
  
  // Icono tarjeta
  dibujarIconoTarjeta(100, 160, COLOR_INFO);
  
  // Mensaje
  tft.setTextColor(COLOR_GRIS);
  tft.setTextSize(1);
  tft.setCursor(40, 250);
  tft.println("Acerque su tarjeta");
  tft.setCursor(60, 270);
  tft.println("al lector NFC");
  
  tft.setCursor(80, 300);
  tft.println("v1.0.0");
}

void mostrarPantallaEsperando() {
  estadoActualPantalla = PANTALLA_ESPERANDO;
  tft.fillScreen(COLOR_FONDO);
  
  mostrarHeader();
  dibujarIconoTarjeta(80, 100, COLOR_INFO);
  
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(2);
  tft.setCursor(30, 200);
  tft.println("ESPERANDO");
  tft.setCursor(50, 230);
  tft.println("TARJETA");
  
  if (claseEnCurso && claseActual.length() > 0) {
    tft.drawFastHLine(20, 270, 200, COLOR_GRIS);
    tft.setTextColor(COLOR_EXITO);
    tft.setTextSize(1);
    tft.setCursor(20, 280);
    tft.print("Clase: ");
    tft.println(claseActual);
  }
}

void mostrarFichajeOK(String nombreUsuario) {
  estadoActualPantalla = PANTALLA_FICHAJE_OK;
  tiempoUltimaPantalla = millis();
  
  tft.fillScreen(COLOR_FONDO);
  
  tft.fillCircle(120, 80, 40, COLOR_EXITO);
  tft.setTextColor(COLOR_FONDO);
  tft.setTextSize(4);
  tft.setCursor(100, 60);
  tft.println("OK");
  
  tft.setTextColor(COLOR_EXITO);
  tft.setTextSize(2);
  tft.setCursor(30, 150);
  tft.println("FICHAJE");
  tft.setCursor(30, 180);
  tft.println("CORRECTO");
  
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(1);
  tft.setCursor(20, 220);
  tft.print("Usuario: ");
  if (nombreUsuario.length() > 20) {
    nombreUsuario = nombreUsuario.substring(0, 17) + "...";
  }
  tft.println(nombreUsuario);
  
  tft.setCursor(20, 240);
  tft.print("Hora: ");
  tft.println(obtenerHoraActual());
}

void mostrarFichajeError(String motivo) {
  estadoActualPantalla = PANTALLA_FICHAJE_ERROR;
  tiempoUltimaPantalla = millis();
  
  tft.fillScreen(COLOR_FONDO);
  
  tft.fillCircle(120, 80, 40, COLOR_ERROR);
  tft.setTextColor(COLOR_FONDO);
  tft.setTextSize(4);
  tft.setCursor(105, 55);
  tft.println("X");
  
  tft.setTextColor(COLOR_ERROR);
  tft.setTextSize(2);
  tft.setCursor(50, 150);
  tft.println("ERROR");
  
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(1);
  tft.setCursor(20, 200);
  
  if (motivo.length() > 30) {
    tft.println(motivo.substring(0, 30));
    tft.setCursor(20, 215);
    tft.println(motivo.substring(30));
  } else {
    tft.println(motivo);
  }
}

void mostrarDatosAula(float temp, float hum, float lux, bool presencia) {
  estadoActualPantalla = PANTALLA_DATOS_AULA;
  tft.fillScreen(COLOR_FONDO);
  
  mostrarHeader();
  
  tft.setTextColor(COLOR_TITULO);
  tft.setTextSize(2);
  tft.setCursor(20, 50);
  tft.println("DATOS AULA");
  
  tft.drawFastHLine(20, 75, 200, COLOR_GRIS);
  
  int y = 90;
  int espaciado = 50;
  
  // Temperatura
  dibujarIconoTermometro(25, y, COLOR_ERROR);
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(2);
  tft.setCursor(60, y);
  char tempStr[10];
  sprintf(tempStr, "%.1f C", temp);
  tft.println(tempStr);
  tft.setTextSize(1);
  tft.setCursor(60, y + 20);
  tft.setTextColor(COLOR_GRIS);
  tft.println("Temperatura");
  
  y += espaciado;
  
  // Humedad
  dibujarIconoGota(25, y, COLOR_INFO);
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(2);
  tft.setCursor(60, y);
  char humStr[10];
  sprintf(humStr, "%.0f %%", hum);
  tft.println(humStr);
  tft.setTextSize(1);
  tft.setCursor(60, y + 20);
  tft.setTextColor(COLOR_GRIS);
  tft.println("Humedad");
  
  y += espaciado;
  
  // Luz
  dibujarIconoLuz(25, y, COLOR_ADVERTENCIA);
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(2);
  tft.setCursor(60, y);
  char luxStr[15];
  sprintf(luxStr, "%.0f lx", lux);
  tft.println(luxStr);
  tft.setTextSize(1);
  tft.setCursor(60, y + 20);
  tft.setTextColor(COLOR_GRIS);
  tft.println("Luminosidad");
  
  y += espaciado;
  
  // Presencia
  tft.fillCircle(35, y + 10, 10, presencia ? COLOR_EXITO : COLOR_GRIS);
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(2);
  tft.setCursor(60, y);
  tft.println(presencia ? "SI" : "NO");
  tft.setTextSize(1);
  tft.setCursor(60, y + 20);
  tft.setTextColor(COLOR_GRIS);
  tft.println("Presencia");
}

void mostrarInfoClase(String clase, String horaInicio, String horaFin) {
  estadoActualPantalla = PANTALLA_CLASE_INFO;
  tft.fillScreen(COLOR_FONDO);
  
  mostrarHeader();
  
  tft.fillRect(90, 50, 60, 50, COLOR_INFO);
  tft.setTextColor(COLOR_FONDO);
  tft.setTextSize(2);
  tft.setCursor(105, 65);
  tft.println("A+");
  
  tft.setTextColor(COLOR_TITULO);
  tft.setTextSize(2);
  tft.setCursor(20, 120);
  tft.println("CLASE ACTUAL");
  
  tft.drawFastHLine(20, 145, 200, COLOR_GRIS);
  
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(1);
  tft.setCursor(20, 160);
  tft.print("Asignatura:");
  tft.setTextSize(2);
  tft.setCursor(20, 180);
  if (clase.length() > 15) {
    tft.println(clase.substring(0, 15));
  } else {
    tft.println(clase);
  }
  
  tft.setTextSize(1);
  tft.setCursor(20, 220);
  tft.print("Horario: ");
  tft.setTextColor(COLOR_EXITO);
  tft.print(horaInicio);
  tft.print(" - ");
  tft.println(horaFin);
}

void mostrarErrorSensor(String sensor) {
  estadoActualPantalla = PANTALLA_ERROR_SENSOR;
  tiempoUltimaPantalla = millis();
  
  tft.fillScreen(COLOR_FONDO);
  
  tft.fillTriangle(120, 40, 70, 120, 170, 120, COLOR_ADVERTENCIA);
  tft.setTextColor(COLOR_FONDO);
  tft.setTextSize(3);
  tft.setCursor(112, 70);
  tft.println("!");
  
  tft.setTextColor(COLOR_ADVERTENCIA);
  tft.setTextSize(2);
  tft.setCursor(20, 150);
  tft.println("ERROR SENSOR");
  
  tft.setTextColor(COLOR_TEXTO);
  tft.setTextSize(1);
  tft.setCursor(20, 190);
  tft.print("Sensor: ");
  tft.println(sensor);
  
  tft.setCursor(20, 210);
  tft.println("Verifique conexiones");
}

void mostrarSinConexion() {
  estadoActualPantalla = PANTALLA_SIN_CONEXION;
  tft.fillScreen(COLOR_FONDO);
  
  dibujarIconoWiFi(100, 60, COLOR_ERROR, false);
  
  tft.setTextColor(COLOR_ERROR);
  tft.setTextSize(2);
  tft.setCursor(60, 150);
  tft.println("SIN");
  tft.setCursor(40, 180);
  tft.println("CONEXION");
  
  tft.setTextColor(COLOR_GRIS);
  tft.setTextSize(1);
  tft.setCursor(30, 230);
  tft.println("Reconectando...");
}

// ============================================================================
// FUNCIONES AUXILIARES
// ============================================================================

void mostrarHeader() {
  tft.fillRect(0, 0, PANTALLA_ANCHO, 30, COLOR_GRIS);
  tft.setTextColor(COLOR_FONDO);
  tft.setTextSize(1);
  tft.setCursor(10, 10);
  tft.println(obtenerHoraActual());
  
  bool wifiConectado = (WiFi.status() == WL_CONNECTED);
  dibujarIconoWiFi(200, 5, wifiConectado ? COLOR_EXITO : COLOR_ERROR, wifiConectado);
}

String obtenerHoraActual() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    return "--:--";
  }
  char buffer[10];
  strftime(buffer, sizeof(buffer), "%H:%M", &timeinfo);
  return String(buffer);
}

void actualizarPantalla() {
  if (estadoActualPantalla == PANTALLA_FICHAJE_OK || 
      estadoActualPantalla == PANTALLA_FICHAJE_ERROR ||
      estadoActualPantalla == PANTALLA_ERROR_SENSOR) {
    if (millis() - tiempoUltimaPantalla > TIEMPO_MENSAJE) {
      mostrarPantallaEsperando();
    }
  }
}

// ============================================================================
// ICONOS
// ============================================================================

void dibujarIconoTarjeta(int x, int y, uint32_t color) {
  tft.drawRect(x, y, 40, 30, color);
  tft.drawRect(x + 2, y + 2, 36, 26, color);
  tft.fillRect(x + 5, y + 8, 10, 8, color);
  tft.drawFastHLine(x + 20, y + 10, 15, color);
  tft.drawFastHLine(x + 20, y + 15, 15, color);
  tft.drawFastHLine(x + 20, y + 20, 10, color);
}

void dibujarIconoTermometro(int x, int y, uint32_t color) {
  tft.drawRect(x + 5, y, 10, 25, color);
  tft.fillCircle(x + 10, y + 30, 8, color);
  tft.fillRect(x + 7, y + 15, 6, 15, color);
}

void dibujarIconoGota(int x, int y, uint32_t color) {
  tft.fillCircle(x + 10, y + 20, 8, color);
  tft.fillTriangle(x + 10, y, x + 2, y + 18, x + 18, y + 18, color);
}

void dibujarIconoLuz(int x, int y, uint32_t color) {
  tft.fillCircle(x + 10, y + 10, 8, color);
  for (int i = 0; i < 8; i++) {
    float angulo = i * 3.14159 / 4;
    int x1 = x + 10 + 12 * cos(angulo);
    int y1 = y + 10 + 12 * sin(angulo);
    int x2 = x + 10 + 16 * cos(angulo);
    int y2 = y + 10 + 16 * sin(angulo);
    tft.drawLine(x1, y1, x2, y2, color);
  }
}

void dibujarIconoWiFi(int x, int y, uint32_t color, bool conectado) {
  if (conectado) {
    tft.drawCircle(x + 10, y + 20, 18, color);
    tft.drawCircle(x + 10, y + 20, 12, color);
    tft.drawCircle(x + 10, y + 20, 6, color);
  } else {
    tft.drawCircle(x + 10, y + 20, 18, COLOR_GRIS);
    tft.drawCircle(x + 10, y + 20, 12, COLOR_GRIS);
    tft.drawLine(x, y, x + 20, y + 20, color);
    tft.drawLine(x + 20, y, x, y + 20, color);
  }
  tft.fillCircle(x + 10, y + 20, 3, conectado ? color : COLOR_GRIS);
}

// ============================================================================
// TOAST (MENSAJES RÁPIDOS)
// ============================================================================

void mostrarToast(String mensaje, uint32_t colorFondo) {
  tft.fillRect(0, PANTALLA_ALTO - 40, PANTALLA_ANCHO, 40, colorFondo);
  tft.setTextColor(COLOR_FONDO);
  tft.setTextSize(1);
  int anchoTexto = mensaje.length() * 6;
  int xPos = (PANTALLA_ANCHO - anchoTexto) / 2;
  tft.setCursor(xPos, PANTALLA_ALTO - 25);
  tft.println(mensaje);
}

void toastExito(String mensaje) {
  mostrarToast(mensaje, COLOR_EXITO);
}

void toastError(String mensaje) {
  mostrarToast(mensaje, COLOR_ERROR);
}

void toastInfo(String mensaje) {
  mostrarToast(mensaje, COLOR_INFO);
}
