import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import OpaqueFunction
from ament_index_python.packages import get_package_share_directory

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
            get_package_share_directory('manta_bot'),
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

    static_odom_node = Node(
        package='manta_bot',
        executable='static_odom_publisher',
        name='static_odom_publisher',
        output='screen'
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
        }]
    )

    # --- MAPPING & SLAM NODES
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config_path]
    )

    activate_mapping_node = Node(
        package='manta_bot',
        executable='activate_mapping',
        name='activate_mapping',
        output='screen'
    )

    # --- VISUALIZATION NODES
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return [
        # --- ROBOT STATE NODES
        urdf_file_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        static_odom_node,
        
        # --- SENSOR NODES
        rplidar_node,
        
        # --- MAPPING & SLAM NODES
        slam_node,
        activate_mapping_node,
        
        # --- VISUALIZATION NODES
        rviz_node
    ]
    
def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=launch_setup)
    ])