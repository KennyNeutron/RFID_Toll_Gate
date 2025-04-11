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
    LED_BuiltIn_On();

    LoRa.readBytes((uint8_t*)&payload, sizeof(payload));

    Serial.println(">> Structured Packet Received <<");
    Serial.print("Header: ");
    Serial.print(payload.header0, HEX);
    Serial.print(" ");
    Serial.println(payload.header1, HEX);

    Serial.print("Role: 0x");
    Serial.println(payload.SlaveRole, HEX);

    Serial.print("UID : ");
    Serial.println(payload.uid);

    Serial.print("Footer: 0x");
    Serial.println(payload.footer, HEX);

    LED_BuiltIn_Off();
  }
}