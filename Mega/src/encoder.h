#ifndef ENCODER_H
#define ENCODER_H

#include <Arduino.h>

// Reads the two hall encoders of the JGB37-520 motors.
// Wiring (Mega pins): motor1 green = 18 (A), motor1 yellow = 19 (B),
//                     motor2 green = 20 (A), motor2 yellow = 21 (B).
// Counts per wheel revolution:
// 11 PPR encoder, 2 edges per tick (CHANGE), gear ratio 34:1.
const float COUNTS_PER_REV = 11.0 * 2.0 * 34.0;

void encoder_init();
long encoder1_count();
long encoder2_count();

// returns ticks since last call (and direction), used for speed
long encoder1_delta();
long encoder2_delta();

#endif
