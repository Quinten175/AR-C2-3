import os
import threading
from flask import Flask, render_template, jsonify, request
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


@app.route('/api/drive', methods=['POST'])
def drive():
    """Accept serial motor commands from the web UI."""
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'error': 'Missing command'}), 400

    cmd = data['command']
    # Forward to serial com module
    try:
        from manta_bot.Movement.serial_com import send_command
        for c in cmd.split(';'):
            c = c.strip()
            if c:
                send_command(c)
        return jsonify({'status': 'ok', 'command': cmd})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/action', methods=['POST'])
def action():
    """Handle start/stop/reset actions."""
    data = request.get_json()
    if not data or 'action' not in data:
        return jsonify({'error': 'Missing action'}), 400

    act = data['action'].lower()
    try:
        from manta_bot.Movement.serial_com import send_command
        commands = {
            'start': 'START',
            'stop': 'M1S;M2S',
            'reset': 'RESET',
        }
        cmd = commands.get(act)
        if not cmd:
            return jsonify({'error': f'Unknown action: {act}'}), 400

        for c in cmd.split(';'):
            send_command(c.strip())
        return jsonify({'status': 'ok', 'action': act})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
