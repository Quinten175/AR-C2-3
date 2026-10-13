import os
import threading

from flask import Flask, render_template, jsonify, request

import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from geometry_msgs.msg import TwistStamped
from std_msgs.msg import Header

from ament_index_python.packages import get_package_share_directory
from std_msgs.msg import Empty

from slam_toolbox.srv import SaveMap, DeserializePoseGraph, Reset, SerializePoseGraph

package_dir = get_package_share_directory('manta_bot')
template_dir = os.path.join(package_dir, 'UI')
static_dir = os.path.join(template_dir, 'static')
map_dir = os.path.join(package_dir, 'map')  
os.makedirs(map_dir, exist_ok=True)

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

node = None


class ROSNode(Node):
    def __init__(self):
        super().__init__('UI_app')
        app.config['ros_node'] = self
        
        self.slam_save_client = self.create_client(
            SaveMap,
            '/slam_toolbox/save_map'
        )
        
        self.tsp = self.create_publisher(
            Empty,
            'tsp/trigger',
            10
        )
        
        self.slam_serialize_client = self.create_client(
            SerializePoseGraph,
            '/slam_toolbox/serialize_map'
        )
        
        self.slam_load_client = self.create_client(
            DeserializePoseGraph,
            '/slam_toolbox/deserialize_map'
        )

        self.slam_reset_client = self.create_client(
            Reset,
            '/slam_toolbox/reset'
        )
        
        self.cmd_vel_pub = self.create_publisher(
            TwistStamped,
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
    
    def toggle_waypoint(self):
        self.active_mapping_state = not self.active_mapping_state

        msg = Empty()

        self.tsp.publish(msg)
        
        return self.tsp
    
    def save_map(self):
        pass
    
    def reset_map(self):
        pass

    def publish_cmd_vel(self, linear_x=0.0, angular_z=0.0):
        msg = TwistStamped()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'

        # Linear velocity
        msg.twist.linear.x = float(linear_x)

        # Everything else stays zero
        msg.twist.linear.y = 0.0
        msg.twist.linear.z = 0.0

        # Angular velocity
        msg.twist.angular.x = 0.0
        msg.twist.angular.y = 0.0
        msg.twist.angular.z = float(angular_z)

        self.cmd_vel_pub.publish(msg)

    def stop_robot(self):
        self.publish_cmd_vel(0.0, 0.0)


@app.route('/')
def index():
    return render_template('index.html')


def slam_service_done(future, operation):
    try:
        response = future.result()

        if hasattr(response, 'resultf'):
            print(f'{operation} result code: {response.result}')

            if response.result == 0:
                print(f'{operation} completed successfully')
            else:
                print(
                    f'SLAM Toolbox failed to perform {operation}. '
                    f'Result code: {response.result}'
                )
        else:
            print(f'{operation} completed successfully')

    except Exception as e:
        print(f'Failed to call {operation} service: {e}')


@app.route('/api/togglewaypoint', methods=['POST'])
def toggle_waypoint():
    node = app.config['ros_node']
    node.toggle_waypoint()
    return jsonify({'success': True, 'active': "toggled"})

@app.route('/api/save', methods=['POST'])
def save():
    node = app.config['ros_node']

    if not node.slam_save_client.wait_for_service(timeout_sec=5.0) or \
       not node.slam_serialize_client.wait_for_service(timeout_sec=5.0):
        return jsonify({'success': False, 'error': 'SLAM Toolbox service unavailable'}), 503

    map_path = os.path.abspath(os.path.join(map_dir, 'my_map'))

    save_req = SaveMap.Request()
    save_req.name.data = map_path
    node.slam_save_client.call_async(save_req)

    ser_req = SerializePoseGraph.Request()
    ser_req.filename = map_path
    ser_future = node.slam_serialize_client.call_async(ser_req)

    event = threading.Event()
    ser_future.add_done_callback(lambda f: event.set())
    if not event.wait(timeout=30.0):
        return jsonify({'success': False, 'error': 'serialize timeout'}), 504

    result = ser_future.result().result
    if result != 0:
        return jsonify({'success': False, 'error': f'serialize failed ({result})'}), 500

    return jsonify({'success': True})
    
@app.route('/api/load', methods=['POST'])
def load():
    node = app.config['ros_node']

    if not node.slam_load_client.wait_for_service(timeout_sec=5.0):
        return jsonify({'success': False, 'error': 'SLAM Toolbox service unavailable'}), 503

    map_path = os.path.join(map_dir, 'my_map')
    node.get_logger().info(f'Loading map from: \'{map_path}\'')
    
    request = DeserializePoseGraph.Request()
    request.filename = map_path
    request.match_type = 1   
    node.get_logger().info(f'Request: {request}')
    future = node.slam_load_client.call_async(request)
    future.add_done_callback(lambda f: slam_service_done(f, 'load_map'))

    return jsonify({'success': True})   

@app.route('/api/reset', methods=['POST'])
def reset():
    node = app.config['ros_node']

    if not node.slam_reset_client.wait_for_service(timeout_sec=5.0):
        node.get_logger().error(
            'SLAM Toolbox reset service not available'
        )
        return jsonify({
            'success': False,
            'error': 'SLAM Toolbox service unavailable'
        }), 503

    request = Reset.Request()

    future = node.slam_reset_client.call_async(request)
    future.add_done_callback(
        lambda future: slam_service_done(future, 'reset_map')
    )

    return jsonify({
        'success': True,
    })


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
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()