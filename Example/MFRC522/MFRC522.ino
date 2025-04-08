#include "Arduino.h"
#include <SPI.h>
#include <MFRC522.h>

// Define pins
#define SS_PIN    21  // SDA pin of MFRC522
#define RST_PIN   22

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(9600);
  SPI.begin();                  // Init SPI bus
  rfid.PCD_Init();              // Init MFRC522
  Serial.println("Place your RFID card/tag near the reader...");
}

void loop() {
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  // Show UID
  Serial.print("Card UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();

  // Halt PICC
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
