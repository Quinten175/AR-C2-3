#!/usr/bin/env python3

import struct

DEVICE = "/dev/input/js0"

# Linux joystick event:
# uint32 time
# int16 value
# uint8 type
# uint8 number
EVENT_SIZE = 8

with open(DEVICE, "rb") as js:
    while True:
        data = js.read(EVENT_SIZE)

        if len(data) != EVENT_SIZE:
            continue

        time_ms, value, event_type, number = struct.unpack(
            "IhBB", data
        )

        # Ignore initialization flag
        event_type &= ~0x80

        if event_type == 0x01:
            print(f"BUTTON {number}: {value}")

        elif event_type == 0x02:
            print(f"AXIS {number}: {value}")
