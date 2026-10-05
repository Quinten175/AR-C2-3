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
CROP = 0.2                               # fraction of box width taken on each side of the centre


def u_to_bearing(u):
    return math.atan((CX - u) / FX) + CAM_YAW
    # Converts a pixel column u into an angle (bearing) from the camera's forward axis. 
    # CX - u is the offset from the image centre; dividing by FX and taking atan gives the angle. 
    # It is flipped (CX - u) because in the image, u grows to the right, but in ROS, positive angles are to the left (counter-clockwise).


class Fusion(Node):
    def __init__(self):
        super().__init__('person_fusion')
<<<<<<< HEAD

        self.get_logger().info('Person fusion node is gestart!')

        det = Subscriber(self, Detection2DArray, '/detections')
=======
        det = Subscriber(self, Detection2DArray, '/detections')   # your topic
>>>>>>> 7575e69 (fix)
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
            if not d.results:
                continue
            r = d.results[0].hypothesis
            if r.class_id != '0' or r.score < 0.5:   # person only (person is class 0 in COCO)
                continue

            u_c = d.bbox.center.position.x
            half = CROP * d.bbox.size_x              # CROP = 0.2 -> middle 40%
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
    node = Fusion()
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