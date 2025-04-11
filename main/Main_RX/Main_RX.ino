#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>

void setup() {
  Serial.begin(9600);
  LED_Setup();
  LoRa02_Setup();
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    LED_BuiltIn_On();
    Serial.print("Received packet: ");
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }
    Serial.println();
    LED_BuiltIn_Off();
  }

}
