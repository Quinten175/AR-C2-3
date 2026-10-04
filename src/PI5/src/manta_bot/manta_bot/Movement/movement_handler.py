import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import math

from .serial_com import send_command, send_wheel_velocities

# robot geometry, must match config/diff_drive_controller.yaml
WHEEL_RADIUS = 0.0295      # m
WHEEL_SEPARATION = 0.255   # m

try:
    from hardware_interface.system_interface import SystemInterface
    from hardware_interface.types import HardwareInterfaceReturn
    from hardware_interface.types import CallbackReturn
except Exception:  #
    class SystemInterface:
        pass

    class HardwareInterfaceReturn:
        OK = 0
        ERROR = 1

    class CallbackReturn:
        SUCCESS = 0
        ERROR = 1


class MantaBotHardware(SystemInterface):


    def __init__(self):
        self._cmd = []
        self._state = []
        self._joint_names = []

    def on_init(self, hardware_info):
        self._joint_names = [joint.name for joint in hardware_info.joints]
        self._cmd = [0.0 for _ in self._joint_names]
        self._state = [0.0 for _ in self._joint_names]
        return CallbackReturn.SUCCESS

    def on_configure(self, previous_state=None):
        return CallbackReturn.SUCCESS

    def on_activate(self, previous_state=None):
        return CallbackReturn.SUCCESS

    def on_deactivate(self, previous_state=None):
        return CallbackReturn.SUCCESS

    def on_cleanup(self, previous_state=None):
        return CallbackReturn.SUCCESS

    def on_shutdown(self, previous_state=None):
        return CallbackReturn.SUCCESS

    def read(self, time, period):
        # For this simple robot we mirror commanded velocities to state
        for i in range(len(self._state)):
            self._state[i] = self._cmd[i]
        return HardwareInterfaceReturn.OK

    def write(self, time, period):
        left_wheel_cmd, right_wheel_cmd = self._cmd
        self._drive_wheels(left_wheel_cmd, right_wheel_cmd)
        return HardwareInterfaceReturn.OK

    def _drive_wheels(self, left_rad_per_sec: float, right_rad_per_sec: float):
        # both wheels in one atomic packet (rad/s -> rpm, sign = direction)
        left_rpm = left_rad_per_sec * 60.0 / (2.0 * math.pi)
        right_rpm = right_rad_per_sec * 60.0 / (2.0 * math.pi)
        send_wheel_velocities(left_rpm, right_rpm)

    @property
    def command(self):
        return self._cmd

    @command.setter
    def command(self, values):
        self._cmd = list(values)

    def export_state_interfaces(self):
        interfaces = []
        for i, name in enumerate(self._joint_names):
            interfaces.append({'name': name, 'interface': 'velocity', 'get': (lambda idx=i: self._state[idx])})
        return interfaces

    def export_command_interfaces(self):
        interfaces = []
        for i, name in enumerate(self._joint_names):
            interfaces.append({'name': name, 'interface': 'velocity', 'set': (lambda v, idx=i: self._set_cmd(idx, v))})
        return interfaces

    def _set_cmd(self, idx, value):
        self._cmd[idx] = value


class MovementHandler(Node):


    def __init__(self):
        super().__init__('movement_handler')
        self.get_logger().info('Movement Handler Node has been started.')

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_callback,
            10,
        )

    def velocity_callback(self, msg: Twist):
        """Convert Twist message to ONE combined wheel-velocity packet."""
        lin_x = msg.linear.x
        ang_z = msg.angular.z

        threshold = 0.01

        if abs(lin_x) < threshold and abs(ang_z) < threshold:
            self.stop_wheels()
            return

        # differential drive kinematics -> per-wheel linear speed (m/s)
        v_left = lin_x - (ang_z * WHEEL_SEPARATION / 2.0)
        v_right = lin_x + (ang_z * WHEEL_SEPARATION / 2.0)

        # m/s -> rad/s -> rpm (sign = direction)
        left_rpm = ((v_left / WHEEL_RADIUS) * 60.0 / (2.0 * math.pi)*2)
        right_rpm = ((v_right / WHEEL_RADIUS) * 60.0 / (2.0 * math.pi)*2)

        self.get_logger().info(
            f'Wheel targets - left: {left_rpm:.1f} rpm, right: {right_rpm:.1f} rpm'
        )
        send_wheel_velocities(left_rpm, right_rpm)

    def stop_wheels(self):
        self.get_logger().info('Stop both wheels')
        send_wheel_velocities(0.0, 0.0)

    def emergency_stop(self):
        self.get_logger().info('EMERGENCY STOP - All motors stopped')
        send_wheel_velocities(0.0, 0.0)


def main(args=None):
    rclpy.init(args=args)
    movement_handler = MovementHandler()
    rclpy.spin(movement_handler)
    movement_handler.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
