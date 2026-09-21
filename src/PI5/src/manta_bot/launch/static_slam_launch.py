import os
from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node
from launch.actions import OpaqueFunction
from ament_index_python.packages import get_package_share_directory

def launch_setup(context, *args, **kwargs):
    slam_config_path = os.path.join(
        get_package_share_directory('manta_bot'),
        'config',
        'slam_config.yaml'
    )

    slam_node = LifecycleNode(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',
        output='screen',
        parameters=[slam_config_path]
    )

    static_odom_node = Node(
        package='manta_bot',
        executable='activate_mapping',
        name='activate_mapping',
        output='screen'
    )
    
    static_odom_node = Node(
        package='manta_bot',
        executable='static_odom_publisher',
        name='static_odom_publisher',
        output='screen'
    )

    rplidar_node = Node(
        package='rplidar_ros',
        executable='rplidar_node',
        name='rplidar_node',
        output='screen',
        parameters=[{
            'serial_port': '/dev/ttyUSB0',
            'serial_baudrate': 115200,
            'frame_id': 'laser',
            'inverted': False,
            'angle_compensate': True,
            'scan_mode': 'Standard'
        }]
    )

    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_laser_broadcaster',
        arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'base_footprint', 'laser'],
        output='screen'
    )

    return [
        static_odom_node,
        rplidar_node,
        static_tf_node,
        slam_node
    ]

def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=launch_setup)
    ])
