#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>

struct data_encrypt {
  uint8_t header0 = 0xff;
  uint8_t header1 = 0xff;
  uint8_t SlaveRole = 0x00;
  char uid[9];
  uint8_t footer = 0xff;
};

typedef struct data_encrypt Data_en;
Data_en payload;

String inputString = "";
bool stringComplete = false;
uint8_t motorcycleCount = 0;
uint8_t carCount = 0;
uint8_t previous_motorcycleCount = 0;
uint8_t previous_carCount = 0;

struct vehicle_DataEncypt {
  uint8_t LR_Motorcycle = 0x00;
  uint8_t LR_Car = 0x00;
};

typedef struct vehicle_DataEncypt vehicle_DataEn;
vehicle_DataEn vehiclePayload;

void setup() {
  Serial.begin(9600);
  LED_Setup();
  LoRa02_Setup();
}

void loop() {
  // LoRa listening stays the same
  int packetSize = LoRa.parsePacket();
  if (packetSize == sizeof(payload)) {
    LED_BuiltIn_On();
    LoRa.readBytes((uint8_t*)&payload, sizeof(payload));
    sendToFlask(payload.SlaveRole, String(payload.uid));
    LED_BuiltIn_Off();
  }

  // Enhanced Serial: Wait for 'S' then read the full line
  static bool readingMessage = false;
  static String serialBuffer = "";

  // Replace inside loop()
  if (Serial.available()) {
    char inChar = (char)Serial.read();

    if (!readingMessage) {
      if (inChar == 'S') {
        readingMessage = true;
        serialBuffer = "";
      }
    } else {
      if (inChar == '\n') {
        // Full message received
        if (serialBuffer.length() > 0) {
          parseCounts(serialBuffer);
        }
        serialBuffer = "";
        readingMessage = false;
      } else {
        serialBuffer += inChar;
        if (serialBuffer.length() > 32) {  // Safety
          Serial.println("Serial buffer overflow. Clearing.");
          serialBuffer = "";
          readingMessage = false;
        }
      }
    }
  }
}


void sendToFlask(uint8_t role, String uid) {
  Serial.print("Role: ");
  Serial.println(role);
  Serial.print("UID: ");
  Serial.println(uid);
}

void parseCounts(String data) {
  if (!data.startsWith("M:") || data.indexOf(",C:") == -1) {
    Serial.println("Invalid input, not sending LoRa.");
    return;
  }

  int mIndex = data.indexOf("M:");
  int cIndex = data.indexOf(",C:");

  String mStr = data.substring(mIndex + 2, cIndex);
  String cStr = data.substring(cIndex + 3);

  motorcycleCount = mStr.toInt();
  carCount = cStr.toInt();

  Serial.print("Sending to LoRa: Motorcycles=");
  Serial.print(motorcycleCount);
  Serial.print(" | Cars=");
  Serial.println(carCount);

  vehiclePayload.LR_Motorcycle = motorcycleCount;
  vehiclePayload.LR_Car = carCount;

  LoRa.beginPacket();
  LoRa.write((uint8_t*)&vehiclePayload, sizeof(vehiclePayload));
  LoRa.endPacket();
  Serial.println("LoRa Payload Sent");
}
