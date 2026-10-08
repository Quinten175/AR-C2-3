from collections import deque

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped

WINDOW_S = 0.5
GATE_M = 0.5


class PersonWaypoint(Node):
    def __init__(self):
        super().__init__('person_waypoint_node')
        self.buf = deque()  # (tijd_s, x, y)
        self.frame_id = ''
        self.publisher = self.create_publisher(PointStamped, '/waypoint_of_person', 10)
        self.create_subscription(PointStamped, '/person_point', self.person_point_callback, 10)
        self.create_timer(0.1, self.on_timer)

    def now_s(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def person_point_callback(self, msg):
        self.frame_id = msg.header.frame_id
        self.buf.append((self.now_s(), msg.point.x, msg.point.y))

    def on_timer(self):
        t = self.now_s()
        while self.buf and t - self.buf[0][0] > WINDOW_S:
            self.buf.popleft()
        if not self.buf:
            return

        pts = np.array([(x, y) for _, x, y in self.buf])
        ref = pts[np.argmin(np.hypot(pts[:, 0], pts[:, 1]))]
        near = pts[np.hypot(pts[:, 0] - ref[0], pts[:, 1] - ref[1]) < GATE_M]
        mx, my = near.mean(axis=0)

        out = PointStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = self.frame_id
        out.point.x, out.point.y = float(mx), float(my)
        self.publisher.publish(out)


def main():
    rclpy.init()
    node = PersonWaypoint()
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