#!/usr/bin/env python3
"""
Serial Debug Node - Continuously reads and logs serial output from Arduino.

This node is useful for debugging Arduino firmware behavior, encoder readings,
motor commands, and PID controller diagnostics.
"""

import rclpy
from rclpy.node import Node
import serial
import threading
import sys
import time


class SerialDebugNode(Node):
    """ROS2 Node that monitors and logs all serial output from the Arduino."""

    def __init__(self):
        super().__init__('serial_debug')
        
        self.declare_parameter('port', '/dev/ttyAMA0')
        self.declare_parameter('baud', 115200)
        
        self.port = self.get_parameter('port').value
        self.baud = self.get_parameter('baud').value
        
        self.get_logger().info(f'Serial Debug Node starting on {self.port} @ {self.baud} baud')
        
        self.ser = None
        self.running = True
        
        # Open serial port
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            self.get_logger().info(f'✓ Serial port opened: {self.port}')
        except Exception as e:
            self.get_logger().error(f'✗ Failed to open serial port {self.port}: {e}')
            self.running = False
            return
        
        # Start reader thread
        self.reader_thread = threading.Thread(
            target=self._read_loop,
            daemon=True
        )
        self.reader_thread.start()
        
        # Create a timer to keep the node alive
        self.timer = self.create_timer(1.0, self._keep_alive)

    def _read_loop(self):
        """Continuously read and log serial data."""
        while self.running and self.ser and self.ser.is_open:
            try:
                line = self.ser.readline()
                if line:
                    decoded = line.decode('utf-8', errors='replace').rstrip()
                    if decoded:  # Only log non-empty lines
                        self.get_logger().info(f'[ARDUINO] {decoded}')
            except Exception as e:
                self.get_logger().error(f'Serial read error: {e}')
                time.sleep(0.5)

    def _keep_alive(self):
        """Keep the node running."""
        pass

    def destroy_node(self):
        """Cleanup on shutdown."""
        self.running = False
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialDebugNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
