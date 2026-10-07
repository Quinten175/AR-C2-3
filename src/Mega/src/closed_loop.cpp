#include "closed_loop.h"
#include "pid.h"
#include "encoder.h"
#include "motor_control.h"

// tuned values
static PID pid2(0.68, 8.2);
static PID pid1(0.71, 7.5);

static float target1 = 0;
static float target2 = 0;
static float rpm1 = 0;
static float rpm2 = 0;
static bool sync_motors = false;   // diff drive needs independent wheels
static bool manual1 = false;       // true while an open-loop command drives that motor
static bool manual2 = false;

// below ~80 PWM the motor stalls, so hold the duty up
const uint8_t PWM_FLOOR = 80;

static float ticks_to_rpm(long ticks, float dt) {
    float revs = ticks / COUNTS_PER_REV;
    return (revs / dt) * 60.0;
}

static void drive(uint8_t motor, float pwm) {
    if (pwm > 0) {
        if (motor == 1) motor1_forward((uint8_t)pwm);
        else motor2_forward((uint8_t)pwm);
    } else if (pwm < 0) {
        if (motor == 1) motor1_reverse((uint8_t)(-pwm));
        else motor2_reverse((uint8_t)(-pwm));
    } else {
        if (motor == 1) motor1_stop();
        else motor2_stop();
    }
}

void closed_loop_init() {
    encoder_init();
}

void closed_loop_update(float dt) {
    rpm1 = ticks_to_rpm(encoder1_delta(), dt);
    rpm2 = ticks_to_rpm(encoder2_delta(), dt);

    float t2 = target2;
    if (sync_motors) t2 = target1;

    // both targets zero -> hard-stop BOTH wheels in the same cycle.
    // coasting (PWM=0) lets each wheel spin down at its own rate,
    // which is why one wheel used to stop later than the other.
    if (target1 == 0 && t2 == 0 && !manual1 && !manual2) {
        pid1.reset();
        pid2.reset();
        motor1_stop();
        motor2_stop();
    } else {
        float out1 = 0;
        float out2 = 0;

        // motor 1: skip while an open-loop command (M1F/M1R) is driving it
        if (!manual1) {
            if (target1 != 0) {
                out1 = pid1.update(fabs(target1), rpm1, dt);
                out1 = constrain(out1, 0, 255);
                if (out1 < PWM_FLOOR) out1 = PWM_FLOOR;
                if (target1 < 0) out1 = -out1;
            } else {
                pid1.reset();
            }
            drive(1, out1);
        }

        // motor 2: skip while an open-loop command (M2F/M2R) is driving it
        if (!manual2) {
            if (t2 != 0) {
                out2 = pid2.update(fabs(t2), rpm2, dt);
                out2 = constrain(out2, 0, 255);
                if (out2 < PWM_FLOOR) out2 = PWM_FLOOR;
                if (t2 < 0) out2 = -out2;
            } else {
                pid2.reset();
            }
            drive(2, out2);
        }
    }
}

void closed_loop_set_target1(float rpm) { target1 = rpm; }
void closed_loop_set_target2(float rpm) { target2 = rpm; }

void closed_loop_set_targets(float rpm1, float rpm2) {
    target1 = rpm1;
    target2 = rpm2;
}
void closed_loop_set_sync(bool on) { sync_motors = on; }

void closed_loop_set_manual(uint8_t motor, bool on) {
    if (motor == 1) manual1 = on;
    else manual2 = on;
}

void closed_loop_stop() {
    target1 = 0;
    target2 = 0;
    manual1 = false;   // take the motors back so they actually get stopped
    manual2 = false;
    pid1.reset();
    pid2.reset();
    motor1_stop();     // stop both in the same instant, no coasting
    motor2_stop();
}

void closed_loop_get_status(float &out_rpm1, float &out_rpm2) {
    out_rpm1 = rpm1;
    out_rpm2 = rpm2;
}
