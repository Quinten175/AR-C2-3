"""
Pure-Python tour planner (no ROS imports): convex hull + angle-based insertion.
Kept separate from the node so it can be tested on its own.
"""
import math
import random


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def turn(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def graham(points):
    S = min(points, key=lambda p: (p[1], p[0]))
    others = [p for p in points if p != S]  # was `p not in S`, which tested membership in the tuple
    others.sort(key=lambda p: (math.atan2(p[1] - S[1], p[0] - S[0]), distance(S, p)))
    route = [S, others[0]]
    for p in others[1:]:
        route.append(p)
        while len(route) >= 3 and turn(route[-3], route[-2], route[-1]) <= 0:
            del route[-2]
    route.append(S)
    total = sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
    return route, total


def angles(p, a, b):
    v1 = (a[0] - p[0], a[1] - p[1])
    v2 = (b[0] - p[0], b[1] - p[1])
    n1 = math.hypot(*v1)
    n2 = math.hypot(*v2)
    if n1 == 0 or n2 == 0:
        return 0.0
    cos_t = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
    return math.acos(max(-1.0, min(1.0, cos_t)))


def graphical(points, start=(0, 0)):
    all_points = points + [start]
    route, _ = graham(all_points)
    remaining = [p for p in all_points if p not in route]
    while remaining:
        p = random.choice(remaining)
        best_angle = -1
        best_i = None
        for i in range(len(route) - 1):
            ang = angles(p, route[i], route[i + 1])
            if ang > best_angle:
                best_angle, best_i = ang, i
        route.insert(best_i + 1, p)
        remaining.remove(p)
    route = route[:-1]
    k = route.index(start)
    route = route[k:] + route[:k] + [start]
    total = sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
    return route, total


def compute_order(start, points):
    """
    start:  (x, y) of the robot, or None (then the first point is used)
    points: list of (x, y)
    returns: indices into `points` in visiting order (open path, no return leg)
    """
    points = [tuple(p) for p in points]
    if not points:
        return []

    lookup = {}  # coordinate -> every index that has it (handles duplicates)
    for i, p in enumerate(points):
        lookup.setdefault(p, []).append(i)

    start = tuple(start) if start is not None else points[0]
    unique = [p for p in lookup if p != start]

    if not unique:  # every waypoint sits exactly on the start
        return lookup.get(start, [])

    route, _total = graphical(unique, start)
    order = []
    for p in route[:-1]:  # drop the closing return-to-start
        order.extend(lookup.get(p, []))
    return order
