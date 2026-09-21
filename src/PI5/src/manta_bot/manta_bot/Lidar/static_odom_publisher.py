from mpi4py import rc

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
import tf2_ros

class StaticOdomPublisher(Node):

    def __init__(self):
        super().__init__('static_odom_publisher')
        self.odom_publisher = self.create_publisher(Odometry, 'odom', 10)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)
        timer_period = 0.05
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info('Static Odom Publisher has been started.')

    def timer_callback(self):
        current_time = self.get_clock().now().to_msg()

        t = TransformStamped()
        t.header.stamp = current_time
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0
        self.tf_broadcaster.sendTransform(t)

        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = 0.0
        odom.pose.pose.position.y = 0.0
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.w = 1.0

        pose_cov = [0.0] * 36
        pose_cov[0] = 1e-9
        pose_cov[7] = 1e-9
        pose_cov[14] = 1e-9
        pose_cov[21] = 1e-9
        pose_cov[28] = 1e-9
        pose_cov[35] = 1e-9
        odom.pose.covariance = pose_cov

        odom.twist.twist.linear.x = 0.0
        odom.twist.twist.linear.y = 0.0
        odom.twist.twist.angular.z = 0.0

        twist_cov = [0.0] * 36
        twist_cov[0] = 1e-9
        twist_cov[7] = 1e-9
        twist_cov[14] = 1e-9
        twist_cov[21] = 1e-9
        twist_cov[28] = 1e-9
        twist_cov[35] = 1e-9
        odom.twist.covariance = twist_cov

        self.odom_publisher.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = StaticOdomPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
