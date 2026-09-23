#include "motor_control.h"

const uint8_t In1 = 3;
const uint8_t In2 = 4;
const uint8_t EnA = 2;

const uint8_t In3 = 5;
const uint8_t In4 = 6;
const uint8_t EnB = 7;

int motor_speed1 = 0;
int motor_speed2 = 0;


void motor1_forward(uint8_t speed)
{
    digitalWrite(In1, LOW);
    digitalWrite(In2, HIGH);

    analogWrite(EnA, speed);

    motor_speed1 = speed;
}


void motor1_reverse(uint8_t speed)
{
    digitalWrite(In1, HIGH);
    digitalWrite(In2, LOW);

    analogWrite(EnA, speed);

    motor_speed1 = speed;
}


void motor2_forward(uint8_t speed)
{
    digitalWrite(In3, LOW);
    digitalWrite(In4, HIGH);

    analogWrite(EnB, speed);

    motor_speed2 = speed;
}


void motor2_reverse(uint8_t speed)
{
    digitalWrite(In3, HIGH);
    digitalWrite(In4, LOW);

    analogWrite(EnB, speed);

    motor_speed2 = speed;
}


void motor1_stop()
{
    analogWrite(EnA, 0);

    digitalWrite(In1, LOW);
    digitalWrite(In2, LOW);

    motor_speed1 = 0;
}


void motor2_stop()
{
    analogWrite(EnB, 0);

    digitalWrite(In3, LOW);
    digitalWrite(In4, LOW);

    motor_speed2 = 0;
}


void emergency_stop()
{
    analogWrite(EnA, 0);
    analogWrite(EnB, 0);

    digitalWrite(In1, LOW);
    digitalWrite(In2, LOW);
    digitalWrite(In3, LOW);
    digitalWrite(In4, LOW);

    motor_speed1 = 0;
    motor_speed2 = 0;
}


void motor_control_init()
{
    pinMode(In1, OUTPUT);
    pinMode(In2, OUTPUT);
    pinMode(EnA, OUTPUT);

    pinMode(In3, OUTPUT);
    pinMode(In4, OUTPUT);
    pinMode(EnB, OUTPUT);

    emergency_stop();
}