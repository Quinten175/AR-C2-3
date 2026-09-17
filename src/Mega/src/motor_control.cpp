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
        
    } 
    void motor1_reverse(){

    }
    void motor2_forward(){

    }
    void motor2_reverse(){
    
    }
    void motor1_stop(){

    }
    void motor2_stop(){
    
    }
    void emergency_stop(){

    }
};