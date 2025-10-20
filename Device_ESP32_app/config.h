
#ifndef CONFIG_H
#define CONFIG_H

// WiFi y servidor
const char* ssid = "Nothing";
const char* password = "12345678";

// Configuración WebSocket Seguro (WSS) - Librería WebSocketsClient
const char* wsHost = "10.25.186.94";
const int wsPort = 5000;
const char* wsPath = "/ws";

// Configuración para HTTP (usado en algunas funciones)
const char* serverUrl = "https://10.25.186.94:5000";
const char* datos_aula = "/datos_aula";
const char* registro = "/registro";

// --- Certificado del Servidor (Root CA Certificate) ---
const char* server_certificate = \
 
"-----BEGIN CERTIFICATE-----\n" \
"MIIF0zCCA7ugAwIBAgIULRoDJiE2M4Kh8d1R9Zg4ZWTQzWQwDQYJKoZIhvcNAQEL\n" \
"BQAweTELMAkGA1UEBhMCRVMxEDAOBgNVBAgMB0JhZGFqb3oxEDAOBgNVBAcMB03C\n" \
"gnJpZGExDDAKBgNVBAoMA1VFWDENMAsGA1UECwwEQ1VNZTENMAsGA1UEAwwEQ1VN\n" \
"ZTEaMBgGCSqGSIb3DQEJARYLY3VtZUB1ZXguZXMwHhcNMjUxMDE2MDkyNTIxWhcN\n" \
"MjYxMDE2MDkyNTIxWjB5MQswCQYDVQQGEwJFUzEQMA4GA1UECAwHQmFkYWpvejEQ\n" \
"MA4GA1UEBwwHTcKCcmlkYTEMMAoGA1UECgwDVUVYMQ0wCwYDVQQLDARDVU1lMQ0w\n" \
"CwYDVQQDDARDVU1lMRowGAYJKoZIhvcNAQkBFgtjdW1lQHVleC5lczCCAiIwDQYJ\n" \
"KoZIhvcNAQEBBQADggIPADCCAgoCggIBAKX5TaPm+ITmxNIceZd+8h7TIvNUfG/Y\n" \
"MVkCqVQPwYGFL/ce0A4muNq7LdCs/UDiYypZdxIwcHtQpvuxnlM8zQwKsHeabxbn\n" \
"RdkxxXDFLUX9rZaw9XdtThFKJWyorFLsKy3dgSF50CQeX9+c8+d590GLbEBWyPIU\n" \
"F3kk+Xr4ChCeka9OTz166GhEzrjn8QxorWFZbEmbohfFzT6hneadxGiHI4t2AoIO\n" \
"8/u18Ja5CKxO65Fe/7MfUM66ANbTnudgCT9PKSK3TbLtx2VZF8dwotXdaCBvdbEu\n" \
"2zgE9/kqijzFtkcjEOwonUo7MZuHdBjKJAOmdPEWLaFAOwh0eqq8eBGnUTewl4Pd\n" \
"JsolrlO4flVfCrIIEOvKna7GhteOuv2sJalK3AFoODWF31RhAciL3nMgbnoJahHB\n" \
"/WMa0xTaHkODIqXMuCudddK8XwVcKyKZ+ppwQ7zZmE3ktepX0RfbLrhJvYbKr9bf\n" \
"1DTyfz5r1HIIE+Pu3bv6ulj5sw6XYfCPtGTL+cbCo/6jcf/1Nxd5TReyJo+pMLf9\n" \
"rh6zxQnlzq6bqbFSWKYKnNOyQ8XOrNRgL9YDF8Id+JK5Aw5zQDLIPvDG6bBHwpm+\n" \
"6+s49Krp3Bs5HBIO7VQhIE6ygO0N4Fd5ZEBSrltKdDLd0LFqxq4mAs28Gu9shO3e\n" \
"ntx2ZmJmzCoBAgMBAAGjUzBRMB0GA1UdDgQWBBQU5JRB0mi8pQhoMuSEHudzhueP\n" \
"dzAfBgNVHSMEGDAWgBQU5JRB0mi8pQhoMuSEHudzhuePdzAPBgNVHRMBAf8EBTAD\n" \
"AQH/MA0GCSqGSIb3DQEBCwUAA4ICAQCLP5AUshQ+m9v4y8kCT5gBuQ3+2FeIOheL\n" \
"Lh6P8oNJDj99SQNlwGR5p4Frstu6nRu8KoEWluK5pGS1gne1EZ5jii1rcpm2QXwT\n" \
"P9Tiu7Ek8DJqpYB1oUkSRvm3jVcH8EL9/KQkDoRF9BboC/fZtXdm6YC3i7+uPKsi\n" \
"Mg0OYb+RxbcGtFchSMV8XMnpNLsZvRhKOntNsArDFYu7vfBfwresUyct4nBHtYzd\n" \
"XtumL7Sgx40e8/iBb0neY6T064KVTdIbbwDP568wJ9T6r5LdGhMFcDR9FiP25lrQ\n" \
"fTCZ7Kk/x3BsIYH4SrNiEzhQVEE4is+8mQlNhECbY7fRRatTEYe4mzqw/dwsTaWC\n" \
"JA6+0ZijPBJOK1j3e5hRjm/Y8j1IdleLdwgBh3KzZsp9QgiwkDqzUnxsL3w3nXTJ\n" \
"9waoCfd72MjifHTXNYkhLmeHWoPvTzJ+KEEjwagGoKQWCjjGF0U6T34VZof40pbd\n" \
"YYRvBG/q59qyJkZTh2gWRihPC2g470spdn1D/BZtXNd1A4C7LxQQ1OB8AEoRDebD\n" \
"EnCrz5PEQLBe/C6bWs31rBdsQxAm7KsO1452dt62cuSb0DzOXxRfx8xwVpdxee2C\n" \
"FfPr6oIvUXrQTUkT21F9xh+lT5HVHoZ4E5PaWknznbtGYRoVrY+3fIuLDepXOgbN\n" \
"hVPNShtnpg==\n" \
"-----END CERTIFICATE-----\n";

const char* tzInfo = "CET-1CEST,M3.5.0/2,M10.5.0/3";

// Aula y pines
const char* aula = "Aula 101";
const int relayPin = 26;

// Constantes de sensores
#define SEALEVELPRESSURE_HPA (1013.25)
#define RADAR_RX_PIN 16
#define RADAR_TX_PIN 17
#define RADAR_SERIAL Serial1

// Conexiones SPI del ESP32
#define PN532_SCK (18)
#define PN532_MOSI (23)
#define PN532_SS (5)

#endif // CONFIG_H