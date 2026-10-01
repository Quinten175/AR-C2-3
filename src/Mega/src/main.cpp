#include <Arduino.h>
#include "motor_control.h"
#include "closed_loop.h"

// old open-loop commands (M1F, M2R, ...) still work as before.
// new closed-loop commands:
//   V:<rpm1>,<rpm2>  set BOTH wheel target rpms in one packet (negative = reverse)
//   VS               stop both wheels (closed loop)
//   SS               print measured rpm of both wheels

unsigned long last_update = 0;
const unsigned long LOOP_MS = 20;   // 50 Hz control rate

unsigned long last_cmd_ms = 0;
bool timed_out = false;
const unsigned long CMD_TIMEOUT_MS = 500;   // stop if the host goes silent

// non-blocking line assembly for the atomic V:<left>,<right> packet
char line_buf[32];
uint8_t line_len = 0;

void setup() {
  // Start Serial for communication with Raspberry Pi / host
  Serial.begin(115200);

  motor_control_init();
  closed_loop_init();

  last_update = millis();
}



void handle_line(const char *raw) {
  String cmd(raw);
  cmd.trim();
  cmd.toUpperCase();

  int colon = cmd.indexOf(':');

  // atomic packet: both wheel targets in one message -> both wheels update together
  if (cmd.startsWith("V:") && colon >= 0) {
    float rpm1 = 0, rpm2 = 0;
    if (sscanf(cmd.c_str() + colon + 1, "%f,%f", &rpm1, &rpm2) == 2) {
      closed_loop_set_targets(rpm1, rpm2);
      last_cmd_ms = millis();
      timed_out = false;
    }
    return;
  }

  if (cmd.startsWith("VS")) {
    closed_loop_stop();
    return;
  }

  if (cmd.startsWith("SS")) {
    float r1, r2;
    closed_loop_get_status(r1, r2);
    Serial.println("RPM1: " + String(r1) + " RPM2: " + String(r2));
    return;
  }

  // fall through to the old open-loop commands
  int speed = 255;
  if (colon >= 0) {
    speed = cmd.substring(colon + 1).toInt();
    speed = constrain(speed, 0, 255);
  }

  if (cmd.startsWith("M1F")) {
    motor1_forward((uint8_t)speed);
    closed_loop_set_target1(0);
    closed_loop_set_manual(1, true);
    last_cmd_ms = millis();
    timed_out = false;
  } 
  else if (cmd.startsWith("M1R")) {
    motor1_reverse((uint8_t)speed);
    closed_loop_set_target1(0);
    closed_loop_set_manual(1, true);
    last_cmd_ms = millis();
    timed_out = false;
  }  
  if (cmd.startsWith("M2F")) {
    motor2_forward((uint8_t)speed);
    closed_loop_set_target2(0);
    closed_loop_set_manual(2, true);
    last_cmd_ms = millis();
    timed_out = false;
  } else if (cmd.startsWith("M2R")) {
    motor2_reverse((uint8_t)speed);
    closed_loop_set_target2(0);
    closed_loop_set_manual(2, true);
    last_cmd_ms = millis();
    timed_out = false;
  }  if (cmd.startsWith("M1S")) {
    motor1_stop();
    closed_loop_set_target1(0);
    closed_loop_set_manual(1, false);
  }  if (cmd.startsWith("M2S")) {
    motor2_stop();
    closed_loop_set_target2(0);
    closed_loop_set_manual(2, false);
  }  if (cmd.startsWith("ESTOP")) {
    closed_loop_stop();
    emergency_stop();
  }
}

void loop() {
  // read whatever arrived, one full line at a time (never blocks the control loop)
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n') {
      line_buf[line_len] = '\0';
      handle_line(line_buf);
      line_len = 0;
    } else if (c != '\r' && line_len < sizeof(line_buf) - 1) {
      line_buf[line_len++] = c;
    }
  }

  // run the PI loops at a fixed rate
  unsigned long now = millis();
  if (now - last_update >= LOOP_MS) {
    float dt = (now - last_update) / 1000.0;
    last_update = now;
    closed_loop_update(dt);
  }

  // host went silent: stop once
  if (!timed_out && now - last_cmd_ms > CMD_TIMEOUT_MS) {
    timed_out = true;
    closed_loop_stop();
  }
}

