import threading
import socketserver
from http import server
from threading import Condition

import cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update(self, jpeg_bytes):
        with self.condition:
            self.frame = jpeg_bytes
            self.condition.notify_all()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        output = self.server.output
        if self.path == '/':
            self.send_response(200)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception:
                pass  # client disconnected
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass  # keep the ROS console quiet


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class StreamNode(Node):
    def __init__(self):
        super().__init__('mjpeg_stream')
        self.declare_parameter('port', 9091)
        self.declare_parameter('topic', '/image_raw')
        self.declare_parameter('jpeg_quality', 80)

        self.bridge = CvBridge()
        self.output = StreamingOutput()
        self.quality = self.get_parameter('jpeg_quality').value

        self.create_subscription(
            Image, self.get_parameter('topic').value,
            self.on_image, qos_profile_sensor_data)

        port = self.get_parameter('port').value
        self.httpd = StreamingServer(('', port), StreamingHandler)
        self.httpd.output = self.output
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.get_logger().info(f'Serving MJPEG on port {port}')

    def on_image(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        ok, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
        if ok:
            self.output.update(jpeg.tobytes())

    def destroy_node(self):
        self.httpd.shutdown()
        super().destroy_node()


def main():
    rclpy.init()
    node = StreamNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()