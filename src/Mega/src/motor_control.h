#ifndef MOTOR_CONTROL_H
#define MOTOR_CONTROL_H

#include <Arduino.h>

void motor_control_init();
void motor1_forward(uint8_t speed);
void motor1_reverse(uint8_t speed);
void motor2_forward(uint8_t speed);
void motor2_reverse(uint8_t speed);
void motor1_stop();
void motor2_stop();
void emergency_stop();

#endif // MOTOR_CONTROL_H
