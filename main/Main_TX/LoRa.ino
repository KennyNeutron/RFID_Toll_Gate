//LoRa
#define LORA_SS 5    // NSS
#define LORA_RST 14  // RESET
#define LORA_DIO0 4  // IRQ

void LoRa02_Setup() {
  // SPI LoRa pins for ESP32
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1)
      ;
  }else{
    Serial.println("RA02 Module Detected!");
  }
  LoRa.setSyncWord(0xF3);  // On both TX and RX
}

