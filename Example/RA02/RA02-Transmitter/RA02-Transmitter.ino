#include <SPI.h>
#include <LoRa.h>

#define SS 5    // NSS
#define RST 14  // RESET
#define DIO0 4  // IRQ

#define LEDpin_BuiltIn 2

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
}

void loop() {
  Serial.println("Sending packet...");
  digitalWrite(LEDpin_BuiltIn, HIGH);
  LoRa.beginPacket();
  LoRa.print("Hello from ESP32!");
  LoRa.endPacket();
  delay(500);
  digitalWrite(LEDpin_BuiltIn, LOW);
  delay(2500);
}
