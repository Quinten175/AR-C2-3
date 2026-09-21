import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class CmdVelDummy(Node):
    """Publishes a sequence of Twist commands to `/cmd_vel` for testing.

    Sequence steps are (duration_seconds, linear_x, angular_z).
    """

    def __init__(self):
        super().__init__('cmd_vel_dummy')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Define a movement sequence: forward, stop, turn left, forward-right, reverse, stop
        self.sequence = [
            (3.0, 0.2, 0.0),  # drive forward
            (1.0, 0.0, 0.0),  # stop
            (2.0, 0.0, 0.6),  # turn left in place
            (1.0, 0.0, 0.0),  # stop
            (3.0, 0.15, -0.2),  # forward with slight right
            (2.0, -0.15, 0.0),  # reverse
            (1.0, 0.0, 0.0),  # stop
        ]

        self._step_index = 0
        self._step_elapsed = 0.0
        self._rate_hz = 10.0

        # Timer to publish at a fixed rate and advance sequence
        self.timer = self.create_timer(1.0 / self._rate_hz, self._tick)
        self.get_logger().info('CmdVelDummy started, publishing to /cmd_vel')

    def _tick(self):
        if self._step_index >= len(self.sequence):
            # keep publishing zero to ensure robot stops
            msg = Twist()
            self.pub.publish(msg)
            return

        duration, lin_x, ang_z = self.sequence[self._step_index]
        msg = Twist()
        msg.linear.x = float(lin_x)
        msg.angular.z = float(ang_z)
        self.pub.publish(msg)

        self._step_elapsed += 1.0 / self._rate_hz
        if self._step_elapsed >= duration:
            self._step_index += 1
            self._step_elapsed = 0.0


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelDummy()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
