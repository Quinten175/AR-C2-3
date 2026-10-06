import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from std_msgs.msg import Float64MultiArray
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray


class MakeNodes(Node):
    def __init__(self):
        super().__init__('make_nodes')

        self.nodes = []

        self.nodes_publisher = self.create_publisher(
            Float64MultiArray,
            '/tsp/nodes',
            10
        )

        self.marker_publisher = self.create_publisher(
            MarkerArray,
            '/tsp/node_markers',
            10
        )

        self.subscription = self.create_subscription(
            PointStamped,
            '/clicked_point',
            self.point_callback,
            10
        )

        self.get_logger().info('MakeNodes started')
        self.get_logger().info('Waiting for clicks on /clicked_point')

    def point_callback(self, msg):
        x = msg.point.x
        y = msg.point.y

        self.nodes.append([x, y])

        self.publish_nodes()
        self.publish_markers()

        node_number = len(self.nodes)

        self.get_logger().info(
            f'Node {node_number}: x={x:.3f}, y={y:.3f}'
        )

    def publish_nodes(self):
        message = Float64MultiArray()

        for node in self.nodes:
            message.data.append(node[0])
            message.data.append(node[1])

        self.nodes_publisher.publish(message)

    def publish_markers(self):
        marker_array = MarkerArray()

        delete_marker = Marker()
        delete_marker.header.frame_id = 'map'
        delete_marker.header.stamp = self.get_clock().now().to_msg()
        delete_marker.ns = 'tsp_nodes'
        delete_marker.id = 0
        delete_marker.action = Marker.DELETEALL

        marker_array.markers.append(delete_marker)

        for index, node in enumerate(self.nodes):
            x = node[0]
            y = node[1]

            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'tsp_nodes'
            marker.id = index + 1
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD

            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = 0.15
            marker.pose.orientation.w = 1.0

            marker.scale.x = 0.25
            marker.scale.y = 0.25
            marker.scale.z = 0.25

            marker.color.a = 1.0
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0

            marker_array.markers.append(marker)

            text = Marker()
            text.header.frame_id = 'map'
            text.header.stamp = self.get_clock().now().to_msg()
            text.ns = 'tsp_node_numbers'
            text.id = index + 1000
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD

            text.pose.position.x = x
            text.pose.position.y = y
            text.pose.position.z = 0.5
            text.pose.orientation.w = 1.0

            text.scale.z = 0.3

            text.color.a = 1.0
            text.color.r = 1.0
            text.color.g = 1.0
            text.color.b = 1.0

            text.text = str(index + 1)

            marker_array.markers.append(text)

        self.marker_publisher.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)

    node = MakeNodes()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()