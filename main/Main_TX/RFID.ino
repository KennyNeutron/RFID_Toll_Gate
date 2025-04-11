void RFID522_Setup() {
  rfid.PCD_Init();
  byte version = rfid.PCD_ReadRegister(rfid.VersionReg);

  if (version == 0x00 || version == 0xFF) {
    Serial.println("RFID522 not detected. Check wiring.");
    while (1)
      ;
  } else {
    Serial.print("RFID522 detected. Version: 0x");
    Serial.println(version, HEX);
  }
}