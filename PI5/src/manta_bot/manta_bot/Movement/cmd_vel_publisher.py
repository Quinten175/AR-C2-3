import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Header


class CmdVelDummy(Node):
    """Publishes a sequence of TwistStamped commands to `/cmd_vel` for testing.

    Sequence steps are (duration_seconds, linear_x, angular_z).
    """

    def __init__(self):
        super().__init__('cmd_vel_dummy')
        self.pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

        # Define a movement sequence: forward, stop, turn left, forward-right, reverse, stop
        self.sequence = [
            (2.0, 0.2, 0.0),  # drive forward
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
            msg = TwistStamped()
            msg.header = Header()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'base_link'
            self.pub.publish(msg)
            return

        duration, lin_x, ang_z = self.sequence[self._step_index]
        msg = TwistStamped()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = float(lin_x)
        msg.twist.angular.z = float(ang_z)
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
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
