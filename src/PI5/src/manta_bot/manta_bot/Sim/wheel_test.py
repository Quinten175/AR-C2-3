import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class WheelTest(Node):
    def __init__(self):
        super().__init__('wheel_test')

        self.pub = self.create_publisher(
            JointState,
            '/joint_states',
            10
        )

        self.left_pos = 0.0
        self.right_pos = 0.0

        # Angular velocity in rad/s
        self.left_speed = 2.0
        self.right_speed = 2.0

        # 100 Hz
        self.dt = 0.01

        self.timer = self.create_timer(
            self.dt,
            self.update
        )

    def update(self):
        # Integrate velocity -> position
        self.left_pos += self.left_speed * self.dt
        self.right_pos += self.right_speed * self.dt

        msg = JointState()

        msg.header.stamp = self.get_clock().now().to_msg()

        msg.name = [
            'motor_left_1_wheel_left_to_motor_left',
            'motor_right_1_wheel_right_to_motor_right'
        ]

        msg.position = [
            self.left_pos,
            self.right_pos
        ]

        msg.velocity = [
            self.left_speed,
            self.right_speed
        ]

        self.pub.publish(msg)


def main():
    rclpy.init()

    node = WheelTest()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()
