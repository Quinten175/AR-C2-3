import rclpy
from rclpy.node import Node
import serial
import time
import sys
import atexit
import threading

PORT = '/dev/ttyAMA0'  # change to the correct device if needed
BAUD = 115200

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

            print(_SER.readline().decode('utf-8', errors='replace').rstrip())
        except Exception as e:
            print(f"Serial write failed: {e}", file=sys.stderr)


def send_wheel_velocities(left_rpm: float, right_rpm: float):
    """Send BOTH wheel target velocities in one atomic packet: V:<left>,<right>.

    The Mega applies both targets together, so the wheels never get a
    half-updated command pair.
    """
    left_rpm = float(left_rpm)
    right_rpm = float(right_rpm)

    # keep the packet inside the Mega's line buffer (32 bytes incl. terminator)
    if abs(left_rpm) > 999.0 or abs(right_rpm) > 999.0:
        print(
            f"Wheel rpm out of range, clamping: left={left_rpm} right={right_rpm}",
            file=sys.stderr,
        )
        left_rpm = max(-999.0, min(999.0, left_rpm))
        right_rpm = max(-999.0, min(999.0, right_rpm))

    cmd = f"V:{left_rpm:.1f},{right_rpm:.1f}"
    send_command(cmd)



class SerialCommunicationNode(Node):

    def __init__(self):
        super().__init__('serial_communication_node')
        self.get_logger().info('Serial Communication Node has been started.')
        

