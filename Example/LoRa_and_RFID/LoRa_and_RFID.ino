#include "Arduino.h"
#include <SPI.h>
#include <MFRC522.h>
#include <LoRa.h>

#define SS 5    // NSS
#define RST 14  // RESET
#define DIO0 4  // IRQ

#define LEDpin_BuiltIn 2

// Define pins
#define SS_PIN 21  // SDA pin of MFRC522
#define RST_PIN 22

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(9600);
  pinMode(LEDpin_BuiltIn, OUTPUT);
  digitalWrite(LEDpin_BuiltIn, LOW);

  while (!Serial)
    ;

  // SPI LoRa pins for ESP32
  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1)
      ;
  }
  LoRa.setSyncWord(0xF3);  // On both TX and RX

  Serial.println("LoRa Transmitter");
  rfid.PCD_Init();  // Init MFRC522
  Serial.println("Place your RFID card/tag near the reader...");
}

void loop() {
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  for (byte i = 0; i < rfid.uid.size; i++) {
    LED_On();
    LoRa.beginPacket();
    LoRa.print("RFID UID: ");
    for (byte i = 0; i < rfid.uid.size; i++) {
      LoRa.print(rfid.uid.uidByte[i], HEX);
      if (i < rfid.uid.size - 1) LoRa.print(":");
    }
    LoRa.endPacket();
    delay(300);
    LED_Off();
  }
  Serial.println();

  // Halt PICC
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

void LED_On() {
  digitalWrite(LEDpin_BuiltIn, HIGH);
}

void LED_Off() {
  digitalWrite(LEDpin_BuiltIn, LOW);
}
