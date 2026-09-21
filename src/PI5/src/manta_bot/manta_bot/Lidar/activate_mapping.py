import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition

class ActiveMapping(Node):
    def __init__(self):
        super().__init__('activate_mapping')
        self.activation_subscriber = self.create_subscription(Bool, 'activate_mapping', self.activation_callback, 10)
        self.slam_client = self.create_client(ChangeState, '/slam_toolbox/change_state')

    def activation_callback(self, msg):
        if msg.data:
            self.slam_client.wait_for_service()
            request = ChangeState.Request()
            request.transition.id = Transition.TRANSITION_CONFIGURE
            self.slam_client.call_async(request)

            request.transition.id = Transition.TRANSITION_ACTIVATE
            self.slam_client.call_async(request)
        else:
            self.slam_client.wait_for_service()
            request = ChangeState.Request()
            request.transition.id = Transition.TRANSITION_DEACTIVATE
            self.slam_client.call_async(request)

            request.transition.id = Transition.TRANSITION_CLEANUP
            self.slam_client.call_async(request)


def main(args=None):
    rclpy.init(args=args)
    node = ActiveMapping()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()   