import os
import time

import cv2
import numpy as np
import rclpy
from ament_index_python.packages import get_package_share_directory
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage, Image
from ultralytics import YOLO
from vision_msgs.msg import Detection2D, Detection2DArray, ObjectHypothesisWithPose


class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__("yolo_detector")

        self.declare_parameter("image_topic", "/image_raw")
        self.declare_parameter("detections_topic", "/detections")
        self.declare_parameter("annotated_image_topic", "/image_annotated")
        # .pt file, or an exported folder such as "yolo26n_ncnn_model"
        self.declare_parameter("model_name", "yolo26n.pt")
        self.declare_parameter("imgsz", 320)  # smaller = much faster on the Pi CPU
        self.declare_parameter("jpeg_quality", 70)
        # Raw annotated Image is ~0.9 MB/frame at 640x480; only enable if you need it
        self.declare_parameter("publish_raw_annotated", False)

        image_topic = self.get_parameter("image_topic").value
        detections_topic = self.get_parameter("detections_topic").value
        annotated_topic = self.get_parameter("annotated_image_topic").value
        model_name = self.get_parameter("model_name").value
        self.imgsz = int(self.get_parameter("imgsz").value)
        self.jpeg_quality = int(self.get_parameter("jpeg_quality").value)
        self.publish_raw = bool(self.get_parameter("publish_raw_annotated").value)

        self.bridge = CvBridge()

        share = get_package_share_directory("yolo26_ros2")
        model_path = os.path.join(share, "models", model_name)
        self.get_logger().info(f"Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path, task="detect")
        self.exported = os.path.isdir(model_path)  # NCNN/ONNX: imgsz fixed at export
        self.names = self.model.names
        self.get_logger().info("YOLO model loaded successfully")

        # sensor QoS = best effort, depth 5: stale frames are dropped, not queued
        self.img_sub = self.create_subscription(
            Image, image_topic, self.image_callback, qos_profile_sensor_data
        )
        self.det_pub = self.create_publisher(Detection2DArray, detections_topic, 10)
        self.raw_pub = self.create_publisher(Image, annotated_topic, 1)
        self.compressed_pub = self.create_publisher(
            CompressedImage, annotated_topic + "/compressed", qos_profile_sensor_data
        )

        self._frames = 0
        self._t0 = time.monotonic()

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

            kwargs = {"verbose": False, "classes": [0]}
            if not self.exported:
                kwargs["imgsz"] = self.imgsz
            result = self.model(cv_image, **kwargs)[0]

            xyxy = result.boxes.xyxy.cpu().numpy()
            cls = result.boxes.cls.cpu().numpy().astype(int)
            conf = result.boxes.conf.cpu().numpy()

            det_array = Detection2DArray()
            det_array.header = msg.header
            for (x1, y1, x2, y2), c, s in zip(xyxy, cls, conf):
                det = Detection2D()
                det.bbox.center.position.x = float((x1 + x2) / 2)
                det.bbox.center.position.y = float((y1 + y2) / 2)
                det.bbox.size_x = float(x2 - x1)
                det.bbox.size_y = float(y2 - y1)
                hyp = ObjectHypothesisWithPose()
                hyp.hypothesis.class_id = str(c)
                hyp.hypothesis.score = float(s)
                det.results.append(hyp)
                det_array.detections.append(det)
            self.det_pub.publish(det_array)

            # Only draw/encode when somebody is actually listening
            want_jpeg = self.compressed_pub.get_subscription_count() > 0
            want_raw = self.publish_raw and self.raw_pub.get_subscription_count() > 0
            if want_jpeg or want_raw:
                for (x1, y1, x2, y2), c, s in zip(xyxy.astype(int), cls, conf):
                    cv2.rectangle(cv_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        cv_image,
                        f"{self.names[c]}: {s:.2f}",
                        (x1, max(y1 - 5, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )

                if want_jpeg:
                    ok, jpg = cv2.imencode(
                        ".jpg", cv_image, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
                    )
                    if ok:
                        out = CompressedImage()
                        out.header = msg.header
                        out.format = "jpeg"
                        out.data = jpg.tobytes()
                        self.compressed_pub.publish(out)

                if want_raw:
                    raw = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
                    raw.header = msg.header
                    self.raw_pub.publish(raw)

            self._frames += 1
            now = time.monotonic()
            if now - self._t0 >= 5.0:
                self.get_logger().info(f"Detector: {self._frames / (now - self._t0):.1f} fps")
                self._frames = 0
                self._t0 = now

        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
