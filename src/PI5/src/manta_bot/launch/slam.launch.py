import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.parameter_descriptions import ParameterValue
from launch.actions import OpaqueFunction
from ament_index_python.packages import get_package_share_directory
from launch.actions import Shutdown

def launch_setup(context, *args, **kwargs):
    manta_pkg_share = get_package_share_directory('manta_bot')

    slam_config_path = os.path.join(
        manta_pkg_share,
        'config',
        'slam_config.yaml'
    )

    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=os.path.join(
            manta_pkg_share,
            'urdf',
            'robotassembly.urdf'
        )
    )

    robot_description_content = ParameterValue(
        Command([
            'cat ',
            LaunchConfiguration('urdf_file')
        ]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content
        }]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen'
    )

    odom_to_base_footprint_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_base_footprint',
        output='screen',
        condition=IfCondition(LaunchConfiguration('publish_static_odom_tf')),
        arguments=[
            '0',
            '0',
            '0',
            '0',
            '0',
            '0',
            'odom',
            'base_footprint'
        ],
    )

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

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_config_path],
        on_exit=Shutdown(reason='slam_toolbox exited unexpectedly')
    )

    activate_mapping_node = Node(
        package='manta_bot',
        executable='activate_mapping',
        name='activate_mapping',
        output='screen'
    )

    start_activate_after_slam = RegisterEventHandler(
        OnProcessStart(
            target_action=slam_node,
            on_start=[activate_mapping_node]
        )
    )   

    UI_app = Node(
        package='manta_bot',
        executable='UI_app',
        name='UI_app',
        output='screen'
    )

    return [
        urdf_file_arg,
        robot_state_publisher_node,
        joint_state_publisher_node,
        odom_to_base_footprint_node,
        rplidar_node,
        slam_node,
        start_activate_after_slam,
        UI_app,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'publish_static_odom_tf',
            default_value='true',
            description='Set false if another node publishes odom to base_footprint TF'
        ),
        OpaqueFunction(function=launch_setup)
    ])