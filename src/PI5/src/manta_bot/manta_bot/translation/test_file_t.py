import math
import numpy as np
import rclpy
from rclpy.node import Node
from message_filters import Subscriber, ApproximateTimeSynchronizer
from sensor_msgs.msg import LaserScan
from vision_msgs.msg import Detection2DArray
from geometry_msgs.msg import PointStamped

# --- your numbers ---
IMG_W = 640
HFOV = math.radians(49.6)
FX = (IMG_W / 2) / math.tan(HFOV / 2)   # replace with calibrated value later
CX = IMG_W / 2
CAM_X, CAM_Y = 0.1225, 0.004             # camera position in LIDAR frame (adjust if lidar isn't at the centre)
CAM_YAW = 0.0                            # camera yaw relative to lidar, rad


def u_to_bearing(u):
    # ROS convention: left is positive, pixel u increases to the right
    return math.atan((CX - u) / FX) + CAM_YAW


class Fusion(Node):
    def __init__(self):
        super().__init__('person_fusion')
        det = Subscriber(self, Detection2DArray, '/detections')   # your topic
        scan = Subscriber(self, LaserScan, '/scan')
        self.sync = ApproximateTimeSynchronizer([det, scan], 10, 0.05)
        self.sync.registerCallback(self.cb)
        self.pub = self.create_publisher(PointStamped, '/person_point', 10)

    def cb(self, dets, scan):
        ranges = np.array(scan.ranges)
        angles = scan.angle_min + np.arange(len(ranges)) * scan.angle_increment
        valid = np.isfinite(ranges) & (ranges > scan.range_min) & (ranges < scan.range_max)
        x = ranges[valid] * np.cos(angles[valid])
        y = ranges[valid] * np.sin(angles[valid])

        # bearing of every scan point as seen from the camera
        bearing = np.arctan2(y - CAM_Y, x - CAM_X)
        dist = np.hypot(x - CAM_X, y - CAM_Y)

        for d in dets.detections:
            # (filter on class "person" here)
            u_c = d.bbox.center.position.x
            half = d.bbox.size_x / 2
            th_left = u_to_bearing(u_c - half)
            th_right = u_to_bearing(u_c + half)
            m = (bearing <= th_left) & (bearing >= th_right)
            if m.sum() < 3:
                continue
            # nearest points in the wedge, median to reject outliers
            idx = np.argsort(dist[m])[:5]
            px = np.median(x[m][idx])
            py = np.median(y[m][idx])
            out = PointStamped()
            out.header = scan.header
            out.point.x, out.point.y = float(px), float(py)
            self.pub.publish(out)


def main():
    rclpy.init()
    rclpy.spin(Fusion())