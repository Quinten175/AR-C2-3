#include "motor_control.h"

// Pin definitions - replace these with your actual wiring
static const uint8_t M1_PWM_PIN = 5; 
static const uint8_t M1_DIR_PIN = 4; 
static const uint8_t M2_PWM_PIN = 6; 
static const uint8_t M2_DIR_PIN = 7; 

static const uint8_t ENABLE_PIN = A0;

void motor_control_init() {
  pinMode(M1_PWM_PIN, OUTPUT);
  pinMode(M1_DIR_PIN, OUTPUT);
  pinMode(M2_PWM_PIN, OUTPUT);
  pinMode(M2_DIR_PIN, OUTPUT);
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);

  analogWrite(M1_PWM_PIN, 0);
  analogWrite(M2_PWM_PIN, 0);
}

void motor1_forward(uint8_t speed) {
  digitalWrite(ENABLE_PIN, HIGH);
  digitalWrite(M1_DIR_PIN, HIGH);
  analogWrite(M1_PWM_PIN, speed);
}

void motor1_reverse(uint8_t speed) {
  digitalWrite(ENABLE_PIN, HIGH);
  digitalWrite(M1_DIR_PIN, LOW);
  analogWrite(M1_PWM_PIN, speed);
}

void motor2_forward(uint8_t speed) {
  digitalWrite(ENABLE_PIN, HIGH);
  digitalWrite(M2_DIR_PIN, HIGH);
  analogWrite(M2_PWM_PIN, speed);
}

void motor2_reverse(uint8_t speed) {
  digitalWrite(ENABLE_PIN, HIGH);
  digitalWrite(M2_DIR_PIN, LOW);
  analogWrite(M2_PWM_PIN, speed);
}

void motor1_stop() {
  analogWrite(M1_PWM_PIN, 0);
}

void motor2_stop() {
  analogWrite(M2_PWM_PIN, 0);
}

void emergency_stop() {
  // immediately stop both motors and disable power
  analogWrite(M1_PWM_PIN, 0);
  analogWrite(M2_PWM_PIN, 0);
  digitalWrite(ENABLE_PIN, LOW);
}
#include <Arduino.h>


class MotorControl {


    public:
    //pin definitions
    int In1 = 3; // Motor 1 input pin 1
    int In2 = 4; // Motor 1 input pin 2
    int EnA = 2; // Motor 1 enable pin (PWM)
    int In3 = 5; // Motor 2 input pin 1
    int In4 = 6; // Motor 2 input pin 2
    int EnB = 7; // Motor 2 enable pin (PWM)

    
    int motor_speed1 = 0; // Speed of the motor (0-255)
    int motor_speed2 = 0; // Speed of the motor (0-255)
    int motor_direction1 = 0; // Direction of the motor (0 for forward, 1 for reverse)
    int motor_direction2 = 0; // Direction of the motor (0 for forward, 1 for reverse)

    
    

    void motor1_forward(){
        motor_speed1 = 200;    // There is no real reason that it's set to 200, you can adjust as you like :)
        analogWrite(EnA, motor_speed1);   
        digitalWrite(In1, LOW);
        digitalWrite(In2, HIGH);
    } 
    void motor1_reverse(){
        motor_speed1 = 200;
        analogWrite(EnA, motor_speed1);
        digitalWrite(In1, HIGH);
        digitalWrite(In2, LOW);
    }
    void motor2_forward(){
        motor_speed2 = 200;
        analogWrite(EnB, motor_speed2);
        digitalWrite(In3, LOW);
        digitalWrite(In4, HIGH);
    }
    void motor2_reverse(){
        motor_speed2 = 200;
        analogWrite(EnB, motor_speed2);
        digitalWrite(In3, HIGH);
        digitalWrite(In4, LOW); 
    }
    void motor1_stop(){ 
    // EnA=Low and In1 and In2 = X (doesn't matter if high of low) is a freerunning motor stop.
        motor_speed1 = 0;
        analogWrite(EnA, motor_speed1);
        digitalWrite(In1, LOW);
        digitalWrite(In2, HIGH); 
    }
    void motor2_stop(){
        motor_speed2 = 0;
        analogWrite(EnB, motor_speed2);
        digitalWrite(In3, LOW);
        digitalWrite(In4, HIGH);
    }
    void emergency_stop(){
        motor_speed1 = 200; 
        motor_speed2 = 200;
        digitalWrite(In1, LOW);
        digitalWrite(In2, LOW);
        digitalWrite(In3, LOW);
        digitalWrite(In4, LOW);
    }
};