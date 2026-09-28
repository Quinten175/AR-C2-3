import os
import threading

from flask import Flask, render_template, jsonify, request

import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from geometry_msgs.msg import Twist

from ament_index_python.packages import get_package_share_directory

from slam_toolbox.srv import SaveMap

package_dir = get_package_share_directory('manta_bot')
template_dir = os.path.join(package_dir, 'UI')
static_dir = os.path.join(template_dir, 'static')
map_dir = os.path.join(template_dir, 'map')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

node = None


class ROSNode(Node):
    def __init__(self):
        super().__init__('UI_app')

        self.mapping_pub = self.create_publisher(
            Bool,
            'activate_mapping',
            10
        )
        
        self.slam_save_client = self.create_client(
            SaveMap,
            '/slam_toolbox/save_map'
        )
        
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
    
    def save_map(self):
        pass
    
    def reset_map(self):
        pass

    def publish_cmd_vel(self, linear_x=0.0, angular_z=0.0):
        msg = Twist()

        msg.linear.x = float(linear_x)

        msg.linear.y = 0.0
        msg.linear.z = 0.0

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

def save_map_done(self, future):
    try:
        response = future.result()
        self.get_logger().info('Map saved successfully')
    except Exception as e:
        self.get_logger().error(f'Failed to save map: {e}')

@app.route('/api/save', methods=['POST'])
def save(self):
    if not self.client.wait_for_service(timeout_sec=5.0):
        self.get_logger().error(
            'SLAM Toolbox save_map service not available'
        )
        return jsonify({
            'success': False,
            'error': 'SLAM Toolbox service unavailable'
        }), 503

    map_dir = (
        Path(get_package_share_directory('my_robot_package'))
        / 'map'
    )
    map_dir.mkdir(parents=True, exist_ok=True)

    map_path = map_dir / 'map'

    request = SaveMap.Request()
    request.name.data = str(map_path)

    future = self.client.call_async(request)
    future.add_done_callback(self.save_map_done)

    return jsonify({
        'success': True,
        'path': str(map_path)
    })

@app.route('/api/reset', methods=['POST'])
def reset():

    return jsonify({'success': True})

@app.route('/api/drive', methods=['POST'])
def drive():


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

    data = request.get_json()

    if not data or 'action' not in data:
        return jsonify({'error': 'Missing action'}), 400

    act = data['action'].lower()

    try:
        if act == 'start':
            node.get_logger().info('START')

        elif act == 'stop':
            node.stop_robot()

        elif act == 'reset':

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