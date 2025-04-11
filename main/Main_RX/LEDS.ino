//Built-In LED
#define LEDpin_BuiltIn 2

void LED_Setup() {
  pinMode(LEDpin_BuiltIn, OUTPUT);
  LED_BuiltIn_Off();
}

void LED_BuiltIn_On() {
  digitalWrite(LEDpin_BuiltIn, HIGH);
}

void LED_BuiltIn_Off() {
  digitalWrite(LEDpin_BuiltIn, LOW);
}