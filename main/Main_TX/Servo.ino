void Servo_Unlock() {
  // Rotate counter-clockwise
  myservo.write(0);  // Top for exit
  delay(5000);

  // Stop again
  myservo.write(90);
  delay(2000);
}