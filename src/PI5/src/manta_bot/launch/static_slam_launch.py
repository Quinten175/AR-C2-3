import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import OpaqueFunction
from ament_index_python.packages import get_package_share_directory
from launch.actions import Shutdown

def launch_setup(context, *args, **kwargs):
    # --- CONFIGS
    manta_pkg_share = get_package_share_directory('manta_bot')

    slam_config_path = os.path.join(
        manta_pkg_share,
        'config',
        'slam_config.yaml'
    )
    
    robot_description_content = ParameterValue(
        Command(['cat ', LaunchConfiguration('urdf_file')]),
        value_type=str
    )

    # --- ROBOT STATE NODES
    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=os.path.join(
            get_package_share_directory('robotassembly'),
            'urdf',
            'robotassembly.urdf'
        )
    )
    
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{'zeros': {}}]
    )

    # --- SENSOR NODES
    rplidar_node = Node(
        package='rplidar_ros',
        executable='rplidar_composition',
        name='rplidar_node',
        output='screen',
        parameters=[{
            'serial_port': '/dev/ttyUSB0',
            'serial_baudrate': 115200,
            'frame_id': 'laser_frame',
            'inverted': False,
            'angle_compensate': True,
            'scan_mode': 'Boost',
            'scan_frequency': 5.5
        }],
        on_exit=Shutdown(reason='rplidar_node exited unexpectedly')
    )

    # --- MAPPING & SLAM NODES
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config_path]
    )

    # Statische transformatie van je robot naar de lidar (Zorgt dat SLAM de Lidar snapt!)
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_to_laser_broadcaster',
        arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'base_footprint', 'laser_frame'],
        output='screen'
    )

    return [
        # urdf_file_arg,
        # robot_state_publisher_node,
        # joint_state_publisher_gui_node,
        rplidar_node,
        # slam_node,
        static_tf_node
    ]
    
def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=launch_setup)
    ])
