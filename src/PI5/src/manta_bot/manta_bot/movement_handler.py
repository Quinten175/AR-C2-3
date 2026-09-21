import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from .serial_com import send_command

try:
    from hardware_interface.system_interface import SystemInterface
    from hardware_interface.types import HardwareInterfaceReturn
except ImportError:
    class SystemInterface:  # pragma: no cover
        pass

    class HardwareInterfaceReturn:  # pragma: no cover
        OK = 0
        ERROR = 1


class MantaBotHardware(SystemInterface):
    """ros2_control-compatible hardware interface for a 2-wheel differential drive robot.

    This class receives wheel velocity commands from `diff_drive_controller` and converts
    them to the serial commands your robot expects.
    """

    def __init__(self):
        self._cmd = [0.0, 0.0]
        self._state = [0.0, 0.0]

    def on_init(self, hardware_info):
        self._joint_names = [joint.name for joint in hardware_info.joints]
        self._cmd = [0.0, 0.0]
        self._state = [0.0, 0.0]
        return True

    def read(self, time, period):
        self._state[0] = self._cmd[0]
        self._state[1] = self._cmd[1]
        return HardwareInterfaceReturn.OK

    def write(self, time, period):
        left_wheel_cmd, right_wheel_cmd = self._cmd
        self._drive_wheels(left_wheel_cmd, right_wheel_cmd)
        return HardwareInterfaceReturn.OK

    def _drive_wheels(self, left_rad_per_sec: float, right_rad_per_sec: float):
        left_pwm = self._rad_per_sec_to_pwm(left_rad_per_sec)
        right_pwm = self._rad_per_sec_to_pwm(right_rad_per_sec)

        if left_pwm >= 0:
            send_command(f'M1F:{int(left_pwm)}')
        else:
            send_command(f'M1R:{int(abs(left_pwm))}')

        if right_pwm >= 0:
            send_command(f'M2F:{int(right_pwm)}')
        else:
            send_command(f'M2R:{int(abs(right_pwm))}')

    def _rad_per_sec_to_pwm(self, velocity: float) -> int:

        pwm = int(abs(velocity) * 300.0)
        pwm = max(0, min(255, pwm))
        return pwm if velocity >= 0 else -pwm

    @property
    def command(self):
        return self._cmd

    @command.setter
    def command(self, values):
        self._cmd = list(values)


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
        """Convert Twist message to motor commands."""
        lin_x = msg.linear.x
        ang_z = msg.angular.z

        threshold = 0.01

        speed = int(abs(lin_x) * 255)
        turn_speed = int(abs(ang_z) * 255)

        if abs(lin_x) < threshold and abs(ang_z) < threshold:
            self.motor1_stop()
            self.motor2_stop()
        elif lin_x > threshold and abs(ang_z) < threshold:
            self.motor1_forward(speed)
            self.motor2_forward(speed)
        elif lin_x < -threshold and abs(ang_z) < threshold:
            self.motor1_reverse(speed)
            self.motor2_reverse(speed)
        elif ang_z > threshold:
            self.motor1_forward(turn_speed)
            self.motor2_reverse(turn_speed)
        elif ang_z < -threshold:
            self.motor1_reverse(turn_speed)
            self.motor2_forward(turn_speed)

    def motor1_forward(self, speed: int = 255):
        self.get_logger().info(f'Motor 1 Forward - Speed: {speed}')
        send_command(f'M1F:{speed}')

    def motor1_reverse(self, speed: int = 255):
        self.get_logger().info(f'Motor 1 Reverse - Speed: {speed}')
        send_command(f'M1R:{speed}')

    def motor2_forward(self, speed: int = 255):
        self.get_logger().info(f'Motor 2 Forward - Speed: {speed}')
        send_command(f'M2F:{speed}')

    def motor2_reverse(self, speed: int = 255):
        self.get_logger().info(f'Motor 2 Reverse - Speed: {speed}')
        send_command(f'M2R:{speed}')

    def motor1_stop(self):
        self.get_logger().info('Motor 1 Stop')
        send_command('M1S')

    def motor2_stop(self):
        self.get_logger().info('Motor 2 Stop')
        send_command('M2S')

    def emergency_stop(self):
        self.get_logger().info('EMERGENCY STOP - All motors stopped')
        send_command('ESTOP')


def main(args=None):
    rclpy.init(args=args)
    movement_handler = MovementHandler()
    rclpy.spin(movement_handler)
    movement_handler.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
