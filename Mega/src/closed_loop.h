#ifndef CLOSED_LOOP_H
#define CLOSED_LOOP_H

#include <Arduino.h>

// PI speed control per wheel. Targets are in RPM (sign = direction).
// The motor sync flag drives both wheels with the same target.
void closed_loop_init();
void closed_loop_update(float dt);   // call every cycle, dt in seconds

void closed_loop_set_target1(float rpm);
void closed_loop_set_target2(float rpm);
// set both wheel targets at once (atomic update, sign = direction)
void closed_loop_set_targets(float rpm1, float rpm2);
void closed_loop_set_sync(bool on);
void closed_loop_set_manual(uint8_t motor, bool on);
void closed_loop_stop();             // stops both wheels, resets PIDs
void closed_loop_get_status(float &out_rpm1, float &out_rpm2);

#endif
