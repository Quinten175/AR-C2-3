#include "pid.h"

PID::PID(float p, float i) {
    kp = p;
    ki = i;
    integral = 0;
    prev_error = 0;
}

float PID::update(float target, float measured, float dt) {
    float error = target - measured;
    integral += error * dt;

    // anti-windup
    if (integral > 100) integral = 100;
    if (integral < -100) integral = -100;

    float out = kp * error + ki * integral;
    prev_error = error;
    return out;
}

void PID::reset() {
    integral = 0;
    prev_error = 0;
}
