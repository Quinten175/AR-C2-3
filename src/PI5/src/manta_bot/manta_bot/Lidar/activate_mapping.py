import rclpy
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition
from sensor_msgs.msg import LaserScan


class AutoStartMapping(Node):
    def __init__(self):
        super().__init__('auto_start_mapping')
        self.slam_client = self.create_client(ChangeState, '/slam_toolbox/change_state')
        self._scan_received = False
        self.create_subscription(
            LaserScan, '/scan', self._scan_cb, 10
        )

    def _scan_cb(self, msg):
        self._scan_received = True

    def start(self):
        # Wait for /scan to be publishing
        while rclpy.ok() and not self._scan_received:
            rclpy.spin_once(self, timeout_sec=0.1)
            if not self._scan_received:
                self.get_logger().info('Waiting for /scan ...')

        # Wait for slam_toolbox service
        while rclpy.ok() and not self.slam_client.wait_for_service(timeout_sec=0.1):
            rclpy.spin_once(self, timeout_sec=0.1)

        self._change_state(Transition.TRANSITION_CONFIGURE, self._activate)

    def _activate(self):
        self._change_state(Transition.TRANSITION_ACTIVATE)

    def _change_state(self, transition_id, callback=None):
        request = ChangeState.Request()
        request.transition.id = transition_id
        future = self.slam_client.call_async(request)
        future.add_done_callback(lambda f: self._on_result(f, transition_id, callback))

    def _on_result(self, future, transition_id, callback):
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Transition {transition_id} succeeded')
                if callback:
                    callback()
            else:
                self.get_logger().error(f'Transition {transition_id} failed')
        except Exception as e:
            self.get_logger().error(f'Error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = AutoStartMapping()
    node.start()
    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)
    node.destroy_node()
    rclpy.shutdown() 
