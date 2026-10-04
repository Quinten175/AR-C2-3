import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    manta_pkg = get_package_share_directory('manta_bot')
    robotassembly_pkg = get_package_share_directory('robotassembly')

    urdf_file = os.path.join(robotassembly_pkg, 'urdf', 'robotassembly.urdf')
    controllers_file = os.path.join(manta_pkg, 'config', 'diff_drive_controller.yaml')

    robot_description = ParameterValue(
        Command(['cat ', urdf_file]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        output='screen',
        parameters=[{'robot_description': robot_description}, controllers_file],
        # Controllers are spawned inside this process, so topic remappings for
        # controllers must be applied here (not on the spawner nodes).
        remappings=[('diff_drive_controller/cmd_vel', '/cmd_vel')]
    )

    joint_state_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster']
    )

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller']
    )

    return LaunchDescription([
        robot_state_publisher_node,
        control_node,
        joint_state_spawner,
        diff_drive_spawner,
    ])
