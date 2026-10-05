import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from vision_msgs.msg import Detection2DArray

IMG_W = 640
HFOV = math.radians(49.6)
FX = (IMG_W / 2) / math.tan(HFOV / 2)
CX = IMG_W / 2

PERSON_DIST = 1.5      # fake distance for every detected person (m)
PERSON_WIDTH = 0.4
WALL_DIST = 3.0


class FakeScan(Node):
    def __init__(self):
        super().__init__('fake_scan')
        self.pub = self.create_publisher(LaserScan, '/scan', 10)
        self.create_subscription(Detection2DArray, '/detections', self.cb, 10)

    def cb(self, dets):
        # bearings of detected persons (left = positive)
        person_angles = []
        for d in dets.detections:
            if not d.results:
                continue
            r = d.results[0].hypothesis
            if r.class_id == '0' and r.score >= 0.5:
                u = d.bbox.center.position.x
                person_angles.append(math.atan((CX - u) / FX))

        n = 720
        scan = LaserScan()
        scan.header.stamp = dets.header.stamp
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
            rng = WALL_DIST / math.cos(a) if abs(a) < math.radians(60) else float('inf')
            for pa in person_angles:
                if abs(a - pa) < half:
                    rng = PERSON_DIST
            ranges.append(rng)
        scan.ranges = ranges
        self.pub.publish(scan)


def main():
    rclpy.init()
    rclpy.spin(FakeScan())