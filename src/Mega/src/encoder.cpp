#include "encoder.h"

// Mega interrupt pins 18-21
const uint8_t ENC1_A = 18;
const uint8_t ENC1_B = 19;
const uint8_t ENC2_A = 20;
const uint8_t ENC2_B = 21;

static volatile long count1 = 0;
static volatile long count2 = 0;

void isr1() { count1++; }
void isr2() { count2++; }

void encoder_init() {
    pinMode(ENC1_A, INPUT_PULLUP);
    pinMode(ENC1_B, INPUT_PULLUP);
    pinMode(ENC2_A, INPUT_PULLUP);
    pinMode(ENC2_B, INPUT_PULLUP);

    attachInterrupt(digitalPinToInterrupt(ENC1_A), isr1, CHANGE);
    attachInterrupt(digitalPinToInterrupt(ENC2_A), isr2, CHANGE);
}

long encoder1_count() { return count1; }
long encoder2_count() { return count2; }

long encoder1_delta() {
    long c = count1;
    count1 = 0;
    return c;
}

long encoder2_delta() {
    long c = count2;
    count2 = 0;
    return c;
}
