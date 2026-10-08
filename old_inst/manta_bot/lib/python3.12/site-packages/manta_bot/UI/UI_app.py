import os
import threading

from flask import Flask, render_template, jsonify, request

import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from geometry_msgs.msg import Twist


template_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=template_dir)

node = None


class ROSNode(Node):
    def __init__(self):
        super().__init__('UI_app')

        # Mapping publisher
        self.mapping_pub = self.create_publisher(
            Bool,
            'activate_mapping',
            10
        )

        # cmd_vel publisher
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            'cmd_vel',
            10
        )

        self.active_mapping_state = False

    def toggle_mapping_state(self):
        self.active_mapping_state = not self.active_mapping_state

        msg = Bool()
        msg.data = self.active_mapping_state

        self.mapping_pub.publish(msg)

        return self.active_mapping_state

    def publish_cmd_vel(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()

        # Linear velocity
        msg.linear.x = float(linear_x)

        # Everything else stays zero
        msg.linear.y = 0.0
        msg.linear.z = 0.0

        # Angular velocity
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = float(angular_z)

        self.cmd_vel_pub.publish(msg)

    def stop_robot(self):
        self.publish_cmd_vel(0.0, 0.0)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/toggle', methods=['POST'])
def toggle():
    new_state = node.toggle_mapping_state()
    return jsonify({'state': new_state})


@app.route('/api/drive', methods=['POST'])
def drive():
    """
    Receive velocity commands from the web UI.

    Expected JSON:
    {
        "linear": 0.5,
        "angular": 0.2
    }
    """

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Missing JSON data'}), 400

    try:
        linear = float(data.get('linear', 0.0))
        angular = float(data.get('angular', 0.0))

        node.publish_cmd_vel(linear, angular)

        return jsonify({
            'status': 'ok',
            'linear': linear,
            'angular': angular
        })

    except (ValueError, TypeError) as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/action', methods=['POST'])
def action():
    """Handle start/stop/reset actions."""

    data = request.get_json()

    if not data or 'action' not in data:
        return jsonify({'error': 'Missing action'}), 400

    act = data['action'].lower()

    try:
        if act == 'start':
            # Start action
            node.get_logger().info('START')

        elif act == 'stop':
            # Stop robot by publishing zero velocity
            node.stop_robot()

        elif act == 'reset':
            # Reset action
            node.get_logger().info('RESET')

        else:
            return jsonify({
                'error': f'Unknown action: {act}'
            }), 400

        return jsonify({
            'status': 'ok',
            'action': act
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def spin_ros():
    rclpy.spin(node)


def main():
    global node

    rclpy.init()

    node = ROSNode()

    ros_thread = threading.Thread(
        target=spin_ros,
        daemon=True
    )

    ros_thread.start()

    try:
        app.run(
            host='0.0.0.0',
            port=5000
        )

    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()