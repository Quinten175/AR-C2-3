#!/usr/bin/env python3

import os
import struct
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Header


DEVICE = "/dev/input/js0"

EVENT_SIZE = 8

JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS = 0x02
JS_EVENT_INIT = 0x80


class GamepadCmdVel(Node):

    def __init__(self):
        super().__init__("gamepad_cmd_vel")

        self.pub = self.create_publisher(
            TwistStamped,
            "/cmd_vel",
            10
        )

        self.forward = 0.0
        self.steering = 0.0

        self.running = True

        self.joystick = open(DEVICE, "rb")

        self.get_logger().info(
            f"Connected to joystick: {DEVICE}"
        )

        # Thread continuously reads joystick events
        self.thread = threading.Thread(
            target=self.read_joystick,
            daemon=True
        )

        self.thread.start()

        # Publish cmd_vel at 20 Hz
        self.timer = self.create_timer(
            0.05,
            self.publish_cmd_vel
        )

    def normalize_axis(self, value, deadzone=0.05):

        value = float(value)

        normalized = value / 32767.0

        # Deadzone
        if abs(normalized) < deadzone:
            return 0.0

        # Re-scale after deadzone
        if normalized > 0:
            normalized = (
                normalized - deadzone
            ) / (1.0 - deadzone)
        else:
            normalized = (
                normalized + deadzone
            ) / (1.0 - deadzone)

        return max(-1.0, min(1.0, normalized))

    def read_joystick(self):

        while self.running:

            data = self.joystick.read(EVENT_SIZE)

            if len(data) != EVENT_SIZE:
                continue

            _, value, event_type, number = struct.unpack(
                "IhBB",
                data
            )

            # Ignore initialization events
            if event_type & JS_EVENT_INIT:
                event_type &= ~JS_EVENT_INIT

            # Axis
            if event_type == JS_EVENT_AXIS:

                if number == 0:
                    # Left/right
                    self.steering = self.normalize_axis(
                        value
                    )

                elif number == 1:
                    # Forward/backward
                    # Invert Y so pushing forward is positive
                    self.forward = -self.normalize_axis(
                        value
                    )

            # Buttons
            elif event_type == JS_EVENT_BUTTON:

                if value:
                    self.get_logger().info(
                        f"Button {number} pressed"
                    )

    def publish_cmd_vel(self):

        msg = TwistStamped()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Your original speed limits
        msg.twist.linear.x = self.forward * 0.25
        msg.twist.angular.z = self.steering * 0.5

        self.pub.publish(msg)

    def destroy_node(self):

        self.running = False

        try:
            self.joystick.close()
        except Exception:
            pass

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = GamepadCmdVel()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
