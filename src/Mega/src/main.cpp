#include <Arduino.h>
#include "motor_control.h"
#include "closed_loop.h"

// old open-loop commands (M1F, M2R, ...) still work as before.
// new closed-loop commands:
//   V1:<rpm>  set left wheel target rpm (negative = reverse)
//   V2:<rpm>  set right wheel target rpm
//   VS        stop both wheels (closed loop)
//   SS        print measured rpm of both wheels

unsigned long last_update = 0;
const unsigned long LOOP_MS = 20;   // 50 Hz control rate

void setup() {
  // Start Serial for communication with Raspberry Pi / host
  Serial.begin(115200);

  motor_control_init();
  closed_loop_init();

  last_update = millis();
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');

    cmd.trim();
    cmd.toUpperCase();

    int colon = cmd.indexOf(':');

    if (cmd.startsWith("V1") && colon >= 0) {
      float rpm = cmd.substring(colon + 1).toFloat();
      Serial.println("V1 target: " + String(rpm));
      closed_loop_set_target1(rpm);
    } else if (cmd.startsWith("V2") && colon >= 0) {
      float rpm = cmd.substring(colon + 1).toFloat();
      Serial.println("V2 target: " + String(rpm));
      closed_loop_set_target2(rpm);
    } else if (cmd.startsWith("VS")) {
      Serial.println("Closed loop stop");
      closed_loop_stop();
    } else if (cmd.startsWith("SS")) {
      float r1, r2;
      closed_loop_get_status(r1, r2);
      Serial.println("RPM1: " + String(r1) + " RPM2: " + String(r2));
    } else {
      // fall through to the old open-loop commands
      int speed = 255;
      if (colon >= 0) {
        speed = cmd.substring(colon + 1).toInt();
        speed = constrain(speed, 0, 255);
      }

      if (cmd.startsWith("M1F")) {
        Serial.println("Motor 1 Forward at speed: " + String(speed));
        motor1_forward((uint8_t)speed);
        closed_loop_set_target1(0);
      } else if (cmd.startsWith("M1R")) {
        Serial.println("Motor 1 Reverse at speed: " + String(speed));
        motor1_reverse((uint8_t)speed);
        closed_loop_set_target1(0);
      } else if (cmd.startsWith("M2F")) {
        Serial.println("Motor 2 Forward at speed: " + String(speed));
        motor2_forward((uint8_t)speed);
        closed_loop_set_target2(0);
      } else if (cmd.startsWith("M2R")) {
        Serial.println("Motor 2 Reverse at speed: " + String(speed));
        motor2_reverse((uint8_t)speed);
        closed_loop_set_target2(0);
      } else if (cmd.startsWith("M1S")) {
        Serial.println("Motor 1 Stop");
        motor1_stop();
        closed_loop_set_target1(0);
      } else if (cmd.startsWith("M2S")) {
        Serial.println("Motor 2 Stop");
        motor2_stop();
        closed_loop_set_target2(0);
      } else if (cmd.startsWith("ESTOP")) {
        Serial.println("Emergency Stop");
        closed_loop_stop();
        emergency_stop();
      }
    }
  }

  // run the PI loops at a fixed rate
  unsigned long now = millis();
  if (now - last_update >= LOOP_MS) {
    float dt = (now - last_update) / 1000.0;
    last_update = now;
    closed_loop_update(dt);
  }
}
