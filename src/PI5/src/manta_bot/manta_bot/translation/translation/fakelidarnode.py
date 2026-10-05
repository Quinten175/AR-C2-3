import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

PERSON_DIST = 1.5
PERSON_ANGLE = 0.0
PERSON_WIDTH = 0.4
WALL_DIST = 3.0


class FakeScan(Node):
    def __init__(self):
        super().__init__('fake_scan')
        self.pub = self.create_publisher(LaserScan, '/scan', 10)
        self.create_timer(0.1, self.tick)   # 10 Hz

    def tick(self):
        n = 720
        scan = LaserScan()
        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = 'laser'
        scan.angle_min = -math.pi
        scan.angle_max = math.pi
        scan.angle_increment = 2 * math.pi / n
        scan.range_min = 0.1
        scan.range_max = 12.0

        half = math.atan((PERSON_WIDTH / 2) / PERSON_DIST)
        ranges = []
        for i in range(n):
            a = scan.angle_min + i * scan.angle_increment
            r = WALL_DIST / math.cos(a) if abs(a) < math.radians(60) else float('inf')
            if abs(a - PERSON_ANGLE) < half:
                r = PERSON_DIST
            ranges.append(r)
        scan.ranges = ranges
        self.pub.publish(scan)


def main():
    rclpy.init()
    rclpy.spin(FakeScan())