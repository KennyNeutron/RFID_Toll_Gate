#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>
#include <MFRC522.h>

//RFID
#define RFID_SS 21   // SDA pin of MFRC522
#define RFID_RST 22  // RESET pin of MFRC522

MFRC522 rfid(RFID_SS, RFID_RST);

void setup() {
  Serial.begin(9600);
  LED_Setup();
  LoRa02_Setup();
  RFID522_Setup();
}

void loop() {
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  for (byte i = 0; i < rfid.uid.size; i++) {
    LED_BuiltIn_On();
    LoRa.beginPacket();
    LoRa.print("RFID UID: ");
    for (byte i = 0; i < rfid.uid.size; i++) {
      LoRa.print(rfid.uid.uidByte[i], HEX);
      if (i < rfid.uid.size - 1) LoRa.print(":");
    }
    LoRa.endPacket();
    delay(300);
    LED_BuiltIn_Off();
  }
  Serial.println();

  // Halt PICC
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
