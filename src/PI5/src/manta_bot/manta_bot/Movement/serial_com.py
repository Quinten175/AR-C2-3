import rclpy
from rclpy.node import Node
import serial
import time
import sys
import atexit
import threading

PORT = '/dev/ttyAMA0'  # change to the correct device if needed
BAUD = 115600

_SER = None
_SER_LOCK = threading.Lock()


def _open_serial():
    global _SER
    if _SER is not None and getattr(_SER, 'is_open', False):
        return
    try:
        _SER = serial.Serial(PORT, BAUD, timeout=1)
    except Exception as e:
        print(f"Failed to open serial port {PORT}: {e}", file=sys.stderr)
        _SER = None


def close_serial():
    """Close the module serial port if open."""
    global _SER
    try:
        if _SER is not None and getattr(_SER, 'is_open', False):
            _SER.close()
    except Exception:
        pass
    _SER = None


atexit.register(close_serial)


def send_command(cmd: str):

    _open_serial()
    global _SER
    if _SER is None:
        print(f"Serial port {PORT} unavailable; command not sent: {cmd}", file=sys.stderr)
        return

    with _SER_LOCK:
        try:
            time.sleep(0.01)
            _SER.reset_input_buffer()
            _SER.write((cmd + '\n').encode('utf-8'))
            _SER.flush()
            time.sleep(0.01)
            if _SER.in_waiting > 0:
                print(_SER.readline().decode('utf-8', errors='replace').rstrip())
        except Exception as e:
            print(f"Serial write failed: {e}", file=sys.stderr)



class SerialCommunicationNode(Node):

    def __init__(self):
        super().__init__('serial_communication_node')
        self.get_logger().info('Serial Communication Node has been started.')

