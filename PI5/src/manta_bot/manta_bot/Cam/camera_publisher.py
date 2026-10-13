#!/usr/bin/env python3

import cv2
import time
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


camera_id = 0

class CameraPublisher(Node):
    def __init__(self):
        super().__init__('camera_publisher')
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)

        if not self.cap.isOpened():
            self.get_logger().error("Failed to open camera")
            return
        if self.cap.isOpened():
            self.get_logger().info("Camera opened successfully")

        # Request YUYV first
        fourcc = cv2.VideoWriter_fourcc(*"YUYV")
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.get_logger().info(f"Camera opened: {self.cap.isOpened()}")
        self.get_logger().info(f"Width: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
        self.get_logger().info(f"Height: {self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        self.get_logger().info(f"FPS: {self.cap.get(cv2.CAP_PROP_FPS)}")
        self.get_logger().info(f"FOURCC: {int(self.cap.get(cv2.CAP_PROP_FOURCC))}")

        self.bridge = CvBridge()
        self.publisher = self.create_publisher(Image, '/image_raw', 10)

        self.timer = self.create_timer(1.0 / 30.0, self.publish_frame)

    def publish_frame(self):
        start = time.monotonic()
        ret, frame = self.cap.read()
        elapsed = time.monotonic() - start

        if not ret:
            self.get_logger().error("Failed to read frame from camera")
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        self.publisher.publish(msg)

        #self.get_logger().info(f"Published frame: shape={frame.shape}, read={elapsed * 1000:.1f} ms")


def main(args=None):
    rclpy.init(args=args)

    camera_publisher = None

    try:
        camera_publisher = CameraPublisher()
        rclpy.spin(camera_publisher)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        print(f"Camera publisher error: {e}")

    finally:
        if camera_publisher is not None:
            camera_publisher.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()
        rclpy.shutdown()
if __name__ == '__main__':
    main()
