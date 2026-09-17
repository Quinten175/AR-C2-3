import rclpy
from rclpy.node import Node
import serial
import time
import sys

PORT = '/dev/ttyUSB0'  # Update this to your serial port
BAUD = 9600  # Update this to your baud rate


def send_command(cmd: str):
    ser = serial.Serial(PORT, BAUD, timeout=1)
    
    time.sleep(0.1)
    ser.reset_input_buffer()
    ser.write((cmd + '\n').encode('utf-8'))
    ser.flush()
    

    time.sleep(0.1)
    if ser.in_waiting > 0:
        print(ser.readline().decode('utf-8', errors='replace').rstrip())
    ser.close()


class SerialCommunicationNode(Node):

    
    
    def __init__(self):
        super().__init__('serial_communication_node')
        self.get_logger().info('Serial Communication Node has been started.')
        
        