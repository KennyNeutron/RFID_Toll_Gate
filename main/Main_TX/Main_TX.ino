#include "Arduino.h"
#include <SPI.h>
#include <LoRa.h>
#include <MFRC522.h>
#include <ESP32Servo.h>

Servo myservo;

//RFID
#define RFID_SS 21   // SDA pin of MFRC522
#define RFID_RST 22  // RESET pin of MFRC522

MFRC522 rfid(RFID_SS, RFID_RST);

struct data_encrypt {
  uint8_t header0 = 0xff;
  uint8_t header1 = 0xff;
  uint8_t SlaveRole = 0x00;
  char uid[9];
  uint8_t footer = 0xff;
};

typedef struct data_encrypt Data_en;

Data_en payload;


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
  RFID522_Setup();
  payload.header0 = 0xaa;
  payload.header1 = 0xbb;
  payload.footer = 0xcc;
  payload.SlaveRole = 0x02;  //0x01 for Entrance and 0x02 for Exit

  myservo.setPeriodHertz(50);     // Standard 50Hz
  myservo.attach(32, 500, 2400);  // Attach GPIO 32, safe PWM range
  Servo_Unlock();

  RelayLight_Setup();
  RelayLight_MotorRed_On();
  delay(300);
  RelayLight_MotorRed_Off();
  delay(300);
  RelayLight_MotorGreen_On();
  delay(300);
  RelayLight_MotorGreen_Off();
  delay(300);


  RelayLight_CarRed_On();
  delay(300);
  RelayLight_CarRed_Off();
  delay(300);
  RelayLight_CarGreen_On();
  delay(300);
  RelayLight_CarGreen_Off();
  delay(300);
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize == sizeof(vehiclePayload)) {
    LED_BuiltIn_On();
    //RelayLight_CarGreen_On();
    delay(500);
    //RelayLight_CarGreen_Off();
    LED_BuiltIn_Off();

    LoRa.readBytes((uint8_t*)&vehiclePayload, sizeof(vehiclePayload));
    motorcycleCount = vehiclePayload.LR_Motorcycle;
    carCount = vehiclePayload.LR_Car;

    if (payload.SlaveRole == 0x01) {  // Entrance Gate
      if (carCount > previous_carCount || motorcycleCount > previous_motorcycleCount) {
        Servo_Unlock();
      }
      previous_carCount = carCount;
      previous_motorcycleCount = motorcycleCount;
    }

    if (payload.SlaveRole == 0x02) {  // Exit Gate
      if (carCount < previous_carCount || motorcycleCount < previous_motorcycleCount) {
        Servo_Unlock();
      }
      previous_carCount = carCount;
      previous_motorcycleCount = motorcycleCount;
    }



  } else {

    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

    String uidStr = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";  // pad single hex digits
      uidStr += String(rfid.uid.uidByte[i], HEX);
    }

    uidStr = uidStr.substring(0, 8);  // Trim to 8 characters
    uidStr.toCharArray(payload.uid, sizeof(payload.uid));

    LED_BuiltIn_On();
    RelayLight_OnAll();
    delay(1000);

    LoRa.beginPacket();
    LoRa.write((uint8_t*)&payload, sizeof(payload));
    LoRa.endPacket();
    RelayLight_OffAll();
    LED_BuiltIn_Off();

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
  }


  if (carCount >= 5) {
    RelayLight_CarRed_On();
    RelayLight_CarGreen_Off();
  } else {
    RelayLight_CarRed_Off();
    RelayLight_CarGreen_On();
  }

  if (motorcycleCount >= 45) {
    RelayLight_MotorRed_On();
    RelayLight_MotorGreen_Off();
  } else{
    RelayLight_MotorRed_Off();
    RelayLight_MotorGreen_On();
  }
}



// switch (carCount) {
//   case 1:
//     RelayLight_MotorRed_On();
//     RelayLight_MotorGreen_Off();
//     RelayLight_CarRed_Off();
//     RelayLight_CarGreen_Off();
//     break;
//   case 2:
//     RelayLight_MotorRed_On();
//     RelayLight_MotorGreen_On();
//     RelayLight_CarRed_Off();
//     RelayLight_CarGreen_Off();
//     break;
//   case 3:
//     RelayLight_MotorRed_On();
//     RelayLight_MotorGreen_On();
//     RelayLight_CarRed_On();
//     RelayLight_CarGreen_Off();
//     break;
//   case 4:
//     RelayLight_MotorRed_On();
//     RelayLight_MotorGreen_On();
//     RelayLight_CarRed_On();
//     RelayLight_CarGreen_On();
//     break;
//   default:
//     RelayLight_MotorRed_Off();
//     RelayLight_MotorGreen_Off();
//     RelayLight_CarRed_Off();
//     RelayLight_CarGreen_Off();
//     break;
// }