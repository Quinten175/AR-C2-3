#include <Arduino.h>
#include "motor_control.h"

void setup() {
  // Start Serial for communication with Raspberry Pi / host
  Serial.begin(115600);

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
      motor1_forward((uint8_t)speed);
    } else if (cmd.startsWith("M1R")) {
      motor1_reverse((uint8_t)speed);
    } else if (cmd.startsWith("M2F")) {
      motor2_forward((uint8_t)speed);
    } else if (cmd.startsWith("M2R")) {
      motor2_reverse((uint8_t)speed);
    } else if (cmd.startsWith("M1S")) {
      motor1_stop();
    } else if (cmd.startsWith("M2S")) {
      motor2_stop();
    } else if (cmd.startsWith("ESTOP")) {
      emergency_stop();
    }
  }
  delay(10);
}