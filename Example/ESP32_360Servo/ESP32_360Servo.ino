#include <ESP32Servo.h>  // ✅ Right library for simple servo control

Servo myservo;

void setup() {
  myservo.setPeriodHertz(50);        // Standard 50Hz
  myservo.attach(32, 500, 2400);      // Attach GPIO 32, safe PWM range
}

void loop() {
  // Rotate counter-clockwise
  myservo.write(0);  // Top for exit
  delay(2000);

  // Stop again
  myservo.write(90);
  delay(2000);
}
