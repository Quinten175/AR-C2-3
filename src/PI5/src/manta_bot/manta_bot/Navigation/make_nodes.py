import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
from visualization_msgs.msg import Marker
from visualization_msgs.msg import MarkerArray
from std_srvs.srv import Trigger
from manta_bot_interfaces.msg import Position, TspMarker, TspMarkers


class MakeNodes(Node):
    def __init__(self):
        super().__init__('make_nodes')

        self.nodes = []

        self.nodes_publisher = self.create_publisher(
            TspMarkers,
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
        
        self.clear_service = self.create_service(
            Trigger,
            '/tsp/clear_nodes',
            self.clear_nodes_callback
        )

        self.get_logger().info('MakeNodes started')

    def clear_nodes_callback(self, request, response):
        self.nodes.clear()
        self.publish_nodes()
        self.publish_markers()

        response.success = True
        response.message = 'Nodes cleared'

        return response

    def point_callback(self, msg):
        self.nodes.append([msg.point.x, msg.point.y])
        self.publish_nodes()
        self.publish_markers()

        self.get_logger().info(
            f'Node {len(self.nodes)}: x={msg.point.x:.3f}, y={msg.point.y:.3f}'
        )

    def publish_nodes(self):
        message = TspMarkers()

        for node in self.nodes:
            marker = TspMarker()
            marker.position.x = node[0]
            marker.position.y = node[1]
            message.poses.append(marker)

        self.nodes_publisher.publish(message)

    def publish_markers(self):
        marker_array = MarkerArray()

        delete = Marker()
        delete.header.frame_id = 'map'
        delete.header.stamp = self.get_clock().now().to_msg()
        delete.action = Marker.DELETEALL

        marker_array.markers.append(delete)

        for index, node in enumerate(self.nodes):
            marker = Marker()

            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()

            marker.ns = 'tsp_nodes'
            marker.id = index
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD

            marker.pose.position.x = node[0]
            marker.pose.position.y = node[1]
            marker.pose.position.z = 0.05
            marker.pose.orientation.w = 1.0

            marker.scale.x = 0.12
            marker.scale.y = 0.12
            marker.scale.z = 0.12

            marker.color.a = 1.0
            marker.color.r = 1.0
            marker.color.g = 0.0
            marker.color.b = 0.0

            marker_array.markers.append(marker)

            text = Marker()

            text.header.frame_id = 'map'
            text.header.stamp = self.get_clock().now().to_msg()

            text.ns = 'tsp_node_numbers'
            text.id = index
            text.type = Marker.TEXT_VIEW_FACING
            text.action = Marker.ADD

            text.pose.position.x = node[0]
            text.pose.position.y = node[1]
            text.pose.position.z = 0.25
            text.pose.orientation.w = 1.0

            text.scale.z = 0.2

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