#!/usr/bin/env python3
"""
waypoint_orderer: subscribes to a list of coordinates, computes a visiting
order (see tour_planner.py), publishes it, and sends it to Nav2.

Input : geometry_msgs/PoseArray on 'tsp/nodes'
Output: nav_msgs/Path           on 'visit_order'  (for RViz / debugging)
        nav2_msgs/FollowWaypoints action 'follow_waypoints' (Nav2)

Parameters: global_frame (map), robot_frame (base_link), return_to_start (false)
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseArray, PoseStamped
from nav_msgs.msg import Path
from nav2_msgs.action import FollowWaypoints
from tf2_ros import Buffer, TransformListener, TransformException

from .tour_planner import compute_order


class WaypointOrderer(Node):
    def __init__(self):
        super().__init__('waypoint_orderer')

        self.declare_parameter('global_frame', 'map')
        self.declare_parameter('robot_frame', 'base_link')
        self.declare_parameter('return_to_start', False)
        self.global_frame = self.get_parameter('global_frame').value
        self.robot_frame = self.get_parameter('robot_frame').value
        self.return_to_start = self.get_parameter('return_to_start').value

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.sub = self.create_subscription(
            PoseArray, 'tsp/nodes', self.on_waypoints, 10)
        self.order_pub = self.create_publisher(Path, 'tsp/visit_order', 10)
        self.nav_client = ActionClient(self, FollowWaypoints, 'follow_waypoints')

        self._goal_handle = None
        self._pending_poses = None
        self._server_wait_timer = None
        self.get_logger().info('waypoint_orderer ready, waiting on /tsp/nodes')

    # -- helpers -----------------------------------------------------------
    def robot_pose(self, stamp):
        """Current robot pose in the global frame as a PoseStamped, or None."""
        try:
            t = self.tf_buffer.lookup_transform(
                self.global_frame, self.robot_frame, rclpy.time.Time())
        except TransformException as e:
            self.get_logger().warn(f'No robot pose ({e}); starting from first point')
            return None
        ps = PoseStamped()
        ps.header.frame_id = self.global_frame
        ps.header.stamp = stamp
        ps.pose.position.x = t.transform.translation.x
        ps.pose.position.y = t.transform.translation.y
        ps.pose.position.z = t.transform.translation.z
        ps.pose.orientation = t.transform.rotation
        return ps

    def make_pose(self, pose, stamp):
        ps = PoseStamped()
        ps.header.frame_id = self.global_frame
        ps.header.stamp = stamp
        ps.pose = pose
        q = ps.pose.orientation
        if q.x == q.y == q.z == q.w == 0.0:
            q.w = 1.0  # unset quaternion -> identity
        return ps

    # -- main callback -----------------------------------------------------
    def on_waypoints(self, msg: PoseArray):
        if not msg.poses:
            self.get_logger().warn('Received empty waypoint list, ignoring')
            return

        if msg.header.frame_id and msg.header.frame_id != self.global_frame:
            self.get_logger().error(
                f'Waypoints are in "{msg.header.frame_id}" but this node assumes '
                f'"{self.global_frame}". Transform them first or change the parameter.')
            return

        stamp = self.get_clock().now().to_msg()
        start_pose = self.robot_pose(stamp)
        start_xy = None
        if start_pose is not None:
            start_xy = (start_pose.pose.position.x, start_pose.pose.position.y)

        points = [(p.position.x, p.position.y) for p in msg.poses]
        order = compute_order(start_xy, points)
        self.get_logger().info(f'Visiting order: {order}')

        ordered = [self.make_pose(msg.poses[i], stamp) for i in order]
        if self.return_to_start and start_pose is not None:
            ordered.append(start_pose)

        # 1) Publish the order (handy for RViz)
        path = Path()
        path.header.frame_id = self.global_frame
        path.header.stamp = stamp
        path.poses = ordered
        self.order_pub.publish(path)

        # 2) Send to Nav2
        self.send_to_nav2(ordered)

    def send_to_nav2(self, poses):
        if self._goal_handle is not None:
            self._goal_handle.cancel_goal_async()
            self._goal_handle = None

        if not self.nav_client.server_is_ready():
            self._pending_poses = poses
            if self._server_wait_timer is None:
                self._server_wait_timer = self.create_timer(
                    0.5,
                    self._send_pending_goal_when_ready,
                )
            self.get_logger().warn(
                'follow_waypoints action server is not ready; waiting to send '
                'the TSP route')
            return

        self._send_goal(poses)

    def _send_pending_goal_when_ready(self):
        if self._pending_poses is None or not self.nav_client.server_is_ready():
            return

        poses = self._pending_poses
        self._pending_poses = None
        self._server_wait_timer.cancel()
        self._server_wait_timer = None
        self._send_goal(poses)

    def _send_goal(self, poses):
        goal = FollowWaypoints.Goal()
        goal.poses = poses
        future = self.nav_client.send_goal_async(goal, feedback_callback=self.on_feedback)
        future.add_done_callback(self.on_goal_response)

    def on_goal_response(self, future):
        handle = future.result()
        if not handle.accepted:
            self.get_logger().error('Nav2 rejected the waypoints')
            return
        self._goal_handle = handle
        handle.get_result_async().add_done_callback(self.on_result)

    def on_feedback(self, fb):
        self.get_logger().info(f'Heading to waypoint #{fb.feedback.current_waypoint}')

    def on_result(self, future):
        missed = list(future.result().result.missed_waypoints)
        if missed:
            self.get_logger().warn(f'Missed waypoints: {missed}')
        else:
            self.get_logger().info('All waypoints visited')
        self._goal_handle = None


def main(args=None):
    rclpy.init(args=args)
    node = WaypointOrderer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
