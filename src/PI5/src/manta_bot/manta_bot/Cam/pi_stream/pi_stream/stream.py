import logging
import socketserver
from http import server
from threading import Condition, Thread

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import CompressedImage

PORT = 9091
# The detector already JPEG-encodes the annotated frame, so we just pass the bytes
# through: no raw image over DDS, no decode, no second encode.
TOPIC = '/image_annotated/compressed'


class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update(self, jpeg_bytes):
        with self.condition:
            self.frame = jpeg_bytes
            self.condition.notify_all()


output = StreamingOutput()


class MjpegNode(Node):
    def __init__(self):
        super().__init__('mjpeg_stream')
        self.sub = self.create_subscription(
            CompressedImage, TOPIC, self.on_image, qos_profile_sensor_data)
        self.get_logger().info(f'Subscribed to {TOPIC}')

    def on_image(self, msg: CompressedImage):
        output.update(bytes(msg.data))


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type',
                             'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        if not output.condition.wait(timeout=5.0):
                            continue
                        frame = output.frame
                    if frame is None:
                        continue
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s',
                                self.client_address, str(e))
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    rclpy.init()
    node = MjpegNode()

    httpd = StreamingServer(('', PORT), StreamingHandler)
    Thread(target=httpd.serve_forever, daemon=True).start()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
