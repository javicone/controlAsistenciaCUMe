void setupBME(){
  Serial.println(F("BME280 test"));
  status = bme.begin(0x76);
  if (!status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1)
      ;
  }

  Serial.println("-- Default Test --");
}
    Serial.println();
      ;
  

}