#include <Arduino.h>

void setup() {
  // Start Serial1 for RX/TX on pins 19 (RX1) / 18 (TX1)
  Serial1.begin(9600);

  // Use A0 as a digital output and ensure it's off initially
  pinMode(A0, OUTPUT);
  digitalWrite(A0, LOW);
}

void loop() {
  // Read a command line from Serial1 (terminated by '\n')
  if (Serial1.available()) {
    String cmd = Serial1.readStringUntil('\n');
    cmd.trim();

    if (cmd.equalsIgnoreCase("ON") || cmd == "1") {
      digitalWrite(A0, HIGH);
      Serial1.println("A0 ON");
    } else if (cmd.equalsIgnoreCase("OFF") || cmd == "0") {
      digitalWrite(A0, LOW);
      Serial1.println("A0 OFF");
    } else {
      Serial1.print("Unknown:");
      Serial1.println(cmd);
    }
  }
}