void setupRadar(){
    RADAR_SERIAL.begin(256000, SERIAL_8N1, RADAR_RX_PIN, RADAR_TX_PIN);  //UART for monitoring the radar
    delay(500);

    Serial.print(F("\nConnect LD2410 radar TX to GPIO:"));
    Serial.println(RADAR_RX_PIN);
    Serial.print(F("Connect LD2410 radar RX to GPIO:"));
    Serial.println(RADAR_TX_PIN);
    Serial.print(F("LD2410 radar sensor initialising: "));


    if (radar.begin(RADAR_SERIAL)) {
        Serial.println(F("OK"));
        Serial.print(F("LD2410 firmware version: "));
        Serial.print(radar.firmware_major_version);
        Serial.print('.');
        Serial.print(radar.firmware_minor_version);
        Serial.print('.');
        Serial.println(radar.firmware_bugfix_version, HEX);
    } else {
        Serial.println(F("not connected"));
    }
}