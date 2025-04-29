#define relayPin_1 25 //MotorRed
#define relayPin_2 13 //CarGreen
#define relayPin_3 26 //CarRed
#define relayPin_4 27 //MotorGreen 

void setup() {
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

void loop() {
  // Turn ON relay 1
  digitalWrite(relayPin_1, LOW);
  delay(2000);
  // Turn ON relay 2
  digitalWrite(relayPin_2, LOW);
  delay(2000);

  // Turn ON relay 3
  digitalWrite(relayPin_3, LOW);
  delay(2000);

  // Turn ON relay 4
  digitalWrite(relayPin_4, LOW);
  delay(2000);

  digitalWrite(relayPin_1, HIGH);
  digitalWrite(relayPin_2, HIGH);
  digitalWrite(relayPin_3, HIGH);
  digitalWrite(relayPin_4, HIGH);
  // Small pause before repeating
  delay(2000);
}
