import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition


class ActiveMapping(Node):
    def __init__(self):
        super().__init__('activate_mapping')

        self.activation_subscriber = self.create_subscription(
            Bool,
            'activate_mapping',
            self.activation_callback,
            10
        )

        self.slam_client = self.create_client(
            ChangeState,
            '/slam_toolbox/change_state'
        )

    def activation_callback(self, msg):
        if not self.slam_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(
                'SLAM Toolbox change_state service not available'
            )
            return

        if msg.data:
            self.change_state(
                Transition.TRANSITION_CONFIGURE,
                self.activate_mapping
            )
        else:
            self.change_state(
                Transition.TRANSITION_DEACTIVATE
            )

    def change_state(self, transition_id, callback=None):
        request = ChangeState.Request()
        request.transition.id = transition_id

        future = self.slam_client.call_async(request)

        def done(future):
            try:
                response = future.result()

                if response.success:
                    self.get_logger().info(
                        f'Lifecycle transition {transition_id} succeeded'
                    )

                    if callback is not None:
                        callback()
                else:
                    self.get_logger().error(
                        f'Lifecycle transition {transition_id} failed'
                    )

            except Exception as e:
                self.get_logger().error(
                    f'Failed to change SLAM Toolbox state: {e}'
                )

        future.add_done_callback(done)

    def activate_mapping(self):
        self.change_state(
            Transition.TRANSITION_ACTIVATE
        )


def main(args=None):
    rclpy.init(args=args)

    node = ActiveMapping()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()