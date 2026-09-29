#ifndef PID_H
#define PID_H

// Simple PI controller for wheel speed
class PID {
public:
    PID(float p, float i);

    // returns PWM value in -255..255
    float update(float target, float measured, float dt);
    void reset();

private:
    float kp, ki;
    float integral;
    float prev_error;
};

#endif
