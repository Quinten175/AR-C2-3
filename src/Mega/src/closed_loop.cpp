#include "closed_loop.h"
#include "pid.h"
#include "encoder.h"
#include "motor_control.h"

// tuned values
static PID pid1(0.68, 8.2);
static PID pid2(0.71, 7.5);

static float target1 = 0;
static float target2 = 0;
static float rpm1 = 0;
static float rpm2 = 0;
static bool sync_motors = false;   // diff drive needs independent wheels

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

    float out1 = 0;
    float out2 = 0;

    if (target1 != 0) {
        out1 = pid1.update(fabs(target1), rpm1, dt);
        out1 = constrain(out1, 0, 255);
        if (out1 < PWM_FLOOR) out1 = PWM_FLOOR;
        if (target1 < 0) out1 = -out1;
    } else {
        pid1.reset();
    }

    if (t2 != 0) {
        out2 = pid2.update(fabs(t2), rpm2, dt);
        out2 = constrain(out2, 0, 255);
        if (out2 < PWM_FLOOR) out2 = PWM_FLOOR;
        if (t2 < 0) out2 = -out2;
    } else {
        pid2.reset();
    }

    drive(1, out1);
    drive(2, out2);
}

void closed_loop_set_target1(float rpm) { target1 = rpm; }
void closed_loop_set_target2(float rpm) { target2 = rpm; }
void closed_loop_set_sync(bool on) { sync_motors = on; }

void closed_loop_stop() {
    target1 = 0;
    target2 = 0;
    closed_loop_update(0.02);
}

void closed_loop_get_status(float &out_rpm1, float &out_rpm2) {
    out_rpm1 = rpm1;
    out_rpm2 = rpm2;
}
