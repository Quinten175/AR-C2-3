#include <Arduino.h>

void setup() {
  // Start Serial1 for RX/TX on pins 19 (RX1) / 18 (TX1)
  Serial.begin(115600);

  // Use A0 as a digital output and ensure it's off initially
  pinMode(A0, OUTPUT);
  digitalWrite(A0, LOW);
}

void loop() {
  // Read a command line from Serial1 (terminated by '\n')
  Serial.println("Test");
  if (Serial.available())
   {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.equalsIgnoreCase("ON") || cmd == "1") {
      digitalWrite(A0, HIGH);
      Serial.println("A0 ON");
    } else if (cmd.equalsIgnoreCase("OFF") || cmd == "0") {
      digitalWrite(A0, LOW);
      Serial.println("A0 OFF");
    } else {
      Serial.print("Unknown:");
      Serial.println(cmd);
    }
  }
  delay(10); // Add a small delay to avoid overwhelming the serial buffer
}