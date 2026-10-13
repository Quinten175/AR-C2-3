import math
 
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from tf2_ros import TransformBroadcaster
from vision_msgs.msg import Detection2DArray
 
# ---------------- camera / person settings (unchanged) ----------------
IMG_W = 640
HFOV = math.radians(49.6)
FX = (IMG_W / 2) / math.tan(HFOV / 2)
CX = IMG_W / 2
 
PERSON_DIST = 1.5      # fake distance for every detected person (m)
PERSON_WIDTH = 0.4
 
# ---------------- robot / scan settings ----------------
ROBOT_RADIUS = 0.25
START_X, START_Y, START_YAW = 3.0, 1.5, math.pi / 2   # living room, facing the hallway door
RANGE_MIN, RANGE_MAX = 0.1, 12.0
N_RAYS = 720
MAP_RES = 0.05
 
DOOR_W = 0.9
 
 
# ---------------- world building ----------------
def wall(p1, p2, doors=()):
    """Axis-aligned wall from p1 to p2.
    doors: list of (center, is_open). Open doors leave a DOOR_W gap,
    closed doors stay solid wall."""
    (x1, y1), (x2, y2) = p1, p2
    horizontal = (y1 == y2)
    lo, hi = sorted((x1, x2) if horizontal else (y1, y2))
 
    def seg(a, b):
        return (a, y1, b, y1) if horizontal else (x1, a, x1, b)
 
    out, pos = [], lo
    for c, is_open in sorted(doors):
        if not is_open:
            continue
        a, b = c - DOOR_W / 2, c + DOOR_W / 2
        if a > pos:
            out.append(seg(pos, a))
        pos = b
    if pos < hi:
        out.append(seg(pos, hi))
    return out
 
 
def box(x1, y1, x2, y2):
    return [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]
 
 
def build_house():
    """10 x 8 m house.
 
        y=8  +---------+--------+------------+
             | bedroom | bath   | bedroom 2  |
        y=4.5+--[d]----+--[d]---+----[d]-----+
             |            hallway            |
        y=3  +--[d]-------------------[d]----+
             | living       [open]  kitchen  |
        y=0  +-------[front door]-------------+
             x=0                x=6        x=10
    """
    s = []
    # outer walls (front door in the bottom wall at x=4.95, open)
    s += wall((0, 0), (10, 0), doors=[(4.95, True)])
    s += wall((10, 0), (10, 8))
    s += wall((10, 8), (0, 8))
    s += wall((0, 8), (0, 0))
 
    # hallway south wall: doors to living room and kitchen
    s += wall((0, 3), (10, 3), doors=[(2.95, True), (7.95, False)])   # kitchen door closed
    # hallway north wall: doors to bedroom 1, bathroom, bedroom 2
    s += wall((0, 4.5), (10, 4.5), doors=[(1.95, True), (5.4, False), (7.95, True)])  # bathroom closed
 
    # living room | kitchen divider with a doorway
    s += wall((6, 0), (6, 3), doors=[(1.7, True)])
    # bedroom 1 | bathroom | bedroom 2 dividers
    s += wall((4, 4.5), (4, 8))
    s += wall((6.5, 4.5), (6.5, 8))
 
    # furniture
    s += box(0.3, 0.3, 2.1, 1.0)       # sofa
    s += box(3.5, 1.5, 4.7, 2.3)       # living-room table
    s += box(7.0, 0.2, 9.8, 0.8)       # kitchen counter
    s += box(8.0, 1.5, 9.0, 2.3)       # kitchen table
    s += box(0.3, 6.2, 1.9, 7.8)       # bed 1
    s += box(7.5, 6.5, 9.7, 7.8)       # bed 2
    s += box(4.2, 7.2, 5.0, 7.8)       # bathroom tub
    return np.array(s, dtype=float)
 
 
def raycast(segs, px, py, thetas):
    """Distance from (px, py) along each angle in thetas to the nearest segment."""
    dx, dy = np.cos(thetas)[:, None], np.sin(thetas)[:, None]
    ax, ay = segs[:, 0], segs[:, 1]
    ex, ey = segs[:, 2] - ax, segs[:, 3] - ay
    wx, wy = ax - px, ay - py
 
    denom = dx * ey - dy * ex
    with np.errstate(divide='ignore', invalid='ignore'):
        t = (wx * ey - wy * ex) / denom
        u = (wx * dy - wy * dx) / denom
    ok = (np.abs(denom) > 1e-9) & (t >= RANGE_MIN) & (u >= 0.0) & (u <= 1.0)
    t = np.where(ok, t, np.inf)
    rng = t.min(axis=1)
    rng[rng > RANGE_MAX] = np.inf
    return rng
 
 
def dist_to_segments(segs, px, py):
    ax, ay = segs[:, 0], segs[:, 1]
    ex, ey = segs[:, 2] - ax, segs[:, 3] - ay
    l2 = ex * ex + ey * ey
    u = np.clip(((px - ax) * ex + (py - ay) * ey) / np.where(l2 == 0, 1, l2), 0, 1)
    return np.hypot(px - (ax + u * ex), py - (ay + u * ey)).min()
 
 
# ---------------- node ----------------
class FakeScan(Node):
    def __init__(self):
        super().__init__('fake_scan_c')
        self.segs = build_house()
        self.x, self.y, self.yaw = START_X, START_Y, START_YAW
        self.v = 0.0
        self.w = 0.0
 
        self.pub = self.create_publisher(LaserScan, '/scan', 10)
        self.tf = TransformBroadcaster(self)
        self.create_subscription(Detection2DArray, '/detections', self.cb, 10)
        self.create_subscription(Twist, '/cmd_vel', self.on_cmd, 10)
 
        # static map of the house for RViz (latched)
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.map_pub = self.create_publisher(OccupancyGrid, '/map', qos)
        self.publish_map()
 
        self.last_t = self.get_clock().now()
        self.create_timer(0.05, self.step)
 
    # -- motion --
    def on_cmd(self, msg):
        self.v, self.w = msg.linear.x, msg.angular.z
 
    def step(self):
        now = self.get_clock().now()
        dt = (now - self.last_t).nanoseconds * 1e-9
        self.last_t = now
        self.yaw += self.w * dt
        nx = self.x + self.v * math.cos(self.yaw) * dt
        ny = self.y + self.v * math.sin(self.yaw) * dt
        if dist_to_segments(self.segs, nx, ny) > ROBOT_RADIUS:   # don't drive through walls
            self.x, self.y = nx, ny
 
    # -- map --
    def publish_map(self):
        pad = 0.2
        w = int((10 + 2 * pad) / MAP_RES)
        h = int((8 + 2 * pad) / MAP_RES)
        grid = np.zeros((h, w), dtype=np.int8)
        for x1, y1, x2, y2 in self.segs:
            n = max(2, int(math.hypot(x2 - x1, y2 - y1) / (MAP_RES / 2)))
            for k in range(n + 1):
                px = x1 + (x2 - x1) * k / n
                py = y1 + (y2 - y1) * k / n
                i = int((py + pad) / MAP_RES)
                j = int((px + pad) / MAP_RES)
                if 0 <= i < h and 0 <= j < w:
                    grid[i, j] = 100
        m = OccupancyGrid()
        m.header.frame_id = 'map'
        m.header.stamp = self.get_clock().now().to_msg()
        m.info.resolution = MAP_RES
        m.info.width, m.info.height = w, h
        m.info.origin.position.x = -pad
        m.info.origin.position.y = -pad
        m.info.origin.orientation.w = 1.0
        m.data = grid.flatten().tolist()
        self.map_pub.publish(m)
 
    # -- scan --
    def cb(self, dets):
        # bearings of detected persons (left = positive), relative to robot heading
        person_angles = []
        for d in dets.detections:
            if not d.results:
                continue
            r = d.results[0].hypothesis
            if r.class_id == '0' and r.score >= 0.5:
                u = d.bbox.center.position.x
                person_angles.append(math.atan((CX - u) / FX))
 
        scan = LaserScan()
        scan.header.stamp = dets.header.stamp
        scan.header.frame_id = 'laser'
        scan.angle_min = -math.pi
        scan.angle_max = math.pi
        scan.angle_increment = 2 * math.pi / N_RAYS
        scan.range_min = RANGE_MIN
        scan.range_max = RANGE_MAX
 
        a = scan.angle_min + np.arange(N_RAYS) * scan.angle_increment
        rng = raycast(self.segs, self.x, self.y, a + self.yaw)
 
        half = math.atan((PERSON_WIDTH / 2) / PERSON_DIST)
        for pa in person_angles:
            hit = np.abs(a - pa) < half
            rng[hit] = np.minimum(rng[hit], PERSON_DIST)   # walls can still be closer
 
        scan.ranges = rng.tolist()
        self.pub.publish(scan)
 
        # map -> laser transform with the same stamp as the scan
        t = TransformStamped()
        t.header.stamp = dets.header.stamp
        t.header.frame_id = 'map'
        t.child_frame_id = 'laser'
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.rotation.z = math.sin(self.yaw / 2)
        t.transform.rotation.w = math.cos(self.yaw / 2)
        self.tf.sendTransform(t)
 
 
def main():
    rclpy.init()
    node = FakeScan()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
 
 
if __name__ == '__main__':
    main()
 
