#include <SPI.h>
#include <LoRa.h>

#define SS 5    // NSS
#define RST 14  // RESET
#define DIO0 4  // IRQ

#define LEDpin_BuiltIn 2

void setup() {
  Serial.begin(9600);
  Serial.println("LoRa Receiver");
  pinMode(LEDpin_BuiltIn, OUTPUT);
  digitalWrite(LEDpin_BuiltIn, LOW);

  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1)
      ;
  } else {
    Serial.print("RA02 Module Detected!");
  }
  LoRa.setSyncWord(0xF3);  // On both TX and RX
}

void loop() {
  //Serial.println("Waiting for packet... ");

  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    digitalWrite(LEDpin_BuiltIn, HIGH);
    Serial.print("Received packet: ");
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }
    Serial.println();

    digitalWrite(LEDpin_BuiltIn, LOW);
  }
  //delay(1500);
}
