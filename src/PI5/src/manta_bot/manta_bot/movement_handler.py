import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from Serial_Comunication import send_command

class MovementHandler(Node):
    
    # movement commands
    
    
    def __init__(self):
        super().__init__('movement_handler')
        self.get_logger().info('Movement Handler Node has been started.')
        
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.velocity_callback,
            10
        )
    
    def velocity_callback(self, msg: Twist):
        """Convert Twist message to motor commands"""
        lin_x = msg.linear.x  # forward/backward
        ang_z = msg.angular.z  # rotation
        
        threshold = 0.01
        
        speed = int(abs(lin_x) * 255)
        turn_speed = int(abs(ang_z) * 255)
        
        if abs(lin_x) < threshold and abs(ang_z) < threshold:
            # Stop
            self.motor1_stop()
            self.motor2_stop()
        elif lin_x > threshold and abs(ang_z) < threshold:
            # Forward
            self.motor1_forward(speed)
            self.motor2_forward(speed)
        elif lin_x < -threshold and abs(ang_z) < threshold:
            # Reverse
            self.motor1_reverse(speed)
            self.motor2_reverse(speed)
        elif ang_z > threshold:
            # Turn right
            self.motor1_forward(turn_speed)
            self.motor2_reverse(turn_speed)
        elif ang_z < -threshold:
            # Turn left 
            self.motor1_reverse(turn_speed)
            self.motor2_forward(turn_speed)
    
    def motor1_forward(self, speed: int = 255):
        self.get_logger().info(f'Motor 1 Forward - Speed: {speed}')
        send_command(f'M1F:{speed}')
    
    def motor1_reverse(self, speed: int = 255):
        self.get_logger().info(f'Motor 1 Reverse - Speed: {speed}')
        send_command(f'M1R:{speed}')
    
    def motor2_forward(self, speed: int = 255):
        self.get_logger().info(f'Motor 2 Forward - Speed: {speed}')
        send_command(f'M2F:{speed}')
    
    def motor2_reverse(self, speed: int = 255):
        self.get_logger().info(f'Motor 2 Reverse - Speed: {speed}')
        send_command(f'M2R:{speed}')
    
    def motor1_stop(self):
        self.get_logger().info('Motor 1 Stop')
        send_command('M1S')
    
    def motor2_stop(self):
        self.get_logger().info('Motor 2 Stop')
        send_command('M2S')
    
    def emergency_stop(self):
        self.get_logger().info('EMERGENCY STOP - All motors stopped')
        send_command('ESTOP')
        
    