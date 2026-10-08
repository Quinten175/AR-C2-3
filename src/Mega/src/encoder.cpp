#include "encoder.h"

// Mega interrupt pins 18-21
// Motor 1: pin 18 = green (A), pin 19 = yellow (B)
// Motor 2: pin 20 = green (A), pin 21 = yellow (B)
const uint8_t ENC1_A = 18;
const uint8_t ENC1_B = 19;
const uint8_t ENC2_A = 20;
const uint8_t ENC2_B = 21;

static volatile long count1 = 0;
static volatile long count2 = 0;

// Hall encoder outputs are open-collector, so the internal pull-ups are used.
// Quadrature 2x decoding: interrupt on every edge of channel A (CHANGE),
// read channel B at that moment for the direction.
// If a wheel reports the opposite sign, swap that motor's green/yellow wires.
static void isr_enc1() {
    if (digitalRead(ENC1_A) != digitalRead(ENC1_B)) count1++;
    else count1--;
}

static void isr_enc2() {
    if (digitalRead(ENC2_A) != digitalRead(ENC2_B)) count2++;
    else count2--;
}

void encoder_init() {
    pinMode(ENC1_A, INPUT_PULLUP);
    pinMode(ENC1_B, INPUT_PULLUP);
    pinMode(ENC2_A, INPUT_PULLUP);
    pinMode(ENC2_B, INPUT_PULLUP);

    // pins 18-21 are external-interrupt pins on the Mega
    attachInterrupt(digitalPinToInterrupt(ENC1_A), isr_enc1, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENC2_A), isr_enc2, CHANGE);
}

long encoder1_count() {
    noInterrupts();
    long c = count1;
    interrupts();
    return c;
}

long encoder2_count() {
    noInterrupts();
    long c = count2;
    interrupts();
    return c;
}

// ticks since the last call (sign = direction), consumed by the speed loop
long encoder1_delta() {
    noInterrupts();
    long d = count1;
    count1 = 0;
    interrupts();
    return d;
}

long encoder2_delta() {
    noInterrupts();
    long d = count2;
    count2 = 0;
    interrupts();
    return -d;
}


