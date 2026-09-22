#include <Arduino.h>
#include "motor_control.h"

void setup() {
  // Start Serial for communication with Raspberry Pi / host
  Serial.begin(115200);

  // Initialize motor pins and enable pin
  motor_control_init();
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');

    
    cmd.trim();
    cmd.toUpperCase();

    // default speed
    int speed = 255;
    int colon = cmd.indexOf(':');
    if (colon >= 0) {
      speed = cmd.substring(colon + 1).toInt();
      speed = constrain(speed, 0, 255);
    }

    if (cmd.startsWith("M1F")) {
      Serial.println("Motor 1 Forward at speed: " + String(speed));
      motor1_forward((uint8_t)speed);
    } else if (cmd.startsWith("M1R")) {
      Serial.println("Motor 1 Reverse at speed: " + String(speed));
      motor1_reverse((uint8_t)speed);
    } else if (cmd.startsWith("M2F")) {
      Serial.println("Motor 2 Forward at speed: " + String(speed));
      motor2_forward((uint8_t)speed);
    } else if (cmd.startsWith("M2R")) {
      Serial.println("Motor 2 Reverse at speed: " + String(speed));
      motor2_reverse((uint8_t)speed);
    } else if (cmd.startsWith("M1S")) {
      Serial.println("Motor 1 Stop");
      motor1_stop();
    } else if (cmd.startsWith("M2S")) {
      Serial.println("Motor 2 Stop");
      motor2_stop();
    } else if (cmd.startsWith("ESTOP")) {
      Serial.println("Emergency Stop");
      emergency_stop();
    }
  }
  delay(1);

}