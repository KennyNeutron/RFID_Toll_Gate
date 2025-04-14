#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>
#include <MFRC522.h>

//RFID
#define RFID_SS 21   // SDA pin of MFRC522
#define RFID_RST 22  // RESET pin of MFRC522

MFRC522 rfid(RFID_SS, RFID_RST);

struct data_encrypt{
  uint8_t header0 = 0xff;
  uint8_t header1 = 0xff;
  uint8_t SlaveRole = 0x00;
  char uid[9];
  uint8_t footer = 0xff;
};

typedef struct data_encrypt Data_en;

Data_en payload;

void setup() {
  Serial.begin(9600);
  LED_Setup();
  LoRa02_Setup();
  RFID522_Setup();
  payload.header0 = 0xaa;
  payload.header1 = 0xbb;
  payload.footer = 0xcc;
  payload.SlaveRole = 0x02;
}

void loop() {

  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  String uidStr = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";  // pad single hex digits
    uidStr += String(rfid.uid.uidByte[i], HEX);
  }
  
  uidStr = uidStr.substring(0, 8);  // Trim to 8 characters
  uidStr.toCharArray(payload.uid, sizeof(payload.uid));
  

  LED_BuiltIn_On();
  LoRa.beginPacket();
  LoRa.write((uint8_t*)&payload, sizeof(payload));
  LoRa.endPacket();
  LED_BuiltIn_Off();

  delay(300);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
