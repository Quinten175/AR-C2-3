import os
import threading
from flask import Flask, render_template, jsonify
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool

template_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=template_dir)
node = None


class ROSNode(Node):
    def __init__(self):
        super().__init__('UI_app')
        self.pub = self.create_publisher(Bool, 'activate_mapping', 10)
        self.active_mapping_state = False

    def toggle_mapping_state(self):
        self.active_mapping_state = not self.active_mapping_state
        msg = Bool()
        msg.data = self.active_mapping_state
        self.pub.publish(msg)
        return self.active_mapping_state


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/toggle', methods=['POST'])
def toggle():
    new_state = node.toggle_mapping_state()
    return jsonify({'state': new_state})


def spin_ros():
    rclpy.spin(node)


def main():
    global node
    rclpy.init()
    node = ROSNode()

    ros_thread = threading.Thread(target=spin_ros, daemon=True)
    ros_thread.start()

    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()