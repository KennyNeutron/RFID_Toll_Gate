#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>

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
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize == sizeof(payload)) {
    LoRa.readBytes((uint8_t*)&payload, sizeof(payload));

    // Extracted data
    uint8_t role = payload.SlaveRole;
    String uid = String(payload.uid);

    // Now send `role` and `uid` to Flask
    sendToFlask(role, uid);
  }
}

void sendToFlask(uint8_t role, String uid) {
  // Send `role` and `uid` to Flask
  Serial.print("Role: ");
  Serial.println(role);
  Serial.print("UID: ");
  Serial.println(uid);
}