#define relayPin_1 25  //MotorRed
#define relayPin_2 13  //CarGreen
#define relayPin_3 26  //CarRed
#define relayPin_4 27  //MotorGreen

void RelayLight_Setup() {
  pinMode(relayPin_1, OUTPUT);
  pinMode(relayPin_2, OUTPUT);
  pinMode(relayPin_3, OUTPUT);
  pinMode(relayPin_4, OUTPUT);

  // Initially turn OFF all relays
  digitalWrite(relayPin_1, HIGH);
  digitalWrite(relayPin_2, HIGH);
  digitalWrite(relayPin_3, HIGH);
  digitalWrite(relayPin_4, HIGH);
}


void RelayLight_MotorRed_On() {
  digitalWrite(relayPin_1, LOW);
}

void RelayLight_MotorRed_Off() {
  digitalWrite(relayPin_1, HIGH);
}

void RelayLight_MotorGreen_On() {
  digitalWrite(relayPin_4, LOW);
}

void RelayLight_MotorGreen_Off() {
  digitalWrite(relayPin_4, HIGH);
}

void RelayLight_CarRed_On() {
  digitalWrite(relayPin_3, LOW);
}

void RelayLight_CarRed_Off() {
  digitalWrite(relayPin_3, HIGH);
}

void RelayLight_CarGreen_On() {
  digitalWrite(relayPin_2, LOW);
}

void RelayLight_CarGreen_Off() {
  digitalWrite(relayPin_2, HIGH);
}

void RelayLight_OnAll() {
  digitalWrite(relayPin_1, LOW);
  digitalWrite(relayPin_2, LOW);
  digitalWrite(relayPin_3, LOW);
  digitalWrite(relayPin_4, LOW);
}

void RelayLight_OffAll() {
  digitalWrite(relayPin_1, HIGH);
  digitalWrite(relayPin_2, HIGH);
  digitalWrite(relayPin_3, HIGH);
  digitalWrite(relayPin_4, HIGH);
}