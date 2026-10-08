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

    // anti-windup: the integral term alone may reach at most full PWM.
    // the old fixed +-100 clamp allowed ki*100 = ~800 PWM of windup, which
    // railed the output and made every start overshoot badly.
    float imax = 255.0f / ki;
    if (integral > imax) integral = imax;
    if (integral < -imax) integral = -imax;

    float out = kp * error + ki * integral;
    prev_error = error;
    return out;
}

void PID::reset() {
    integral = 0;
    prev_error = 0;
}
