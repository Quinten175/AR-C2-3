import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_share = FindPackageShare('manta_bot')

    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=PathJoinSubstitution([
            pkg_share,
            'urdf',
            'robotassembly.urdf'
        ])
    )

    robot_description_content = ParameterValue(
        Command(['cat ', LaunchConfiguration('urdf_file')]),
        value_type=str
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

    STNP_map_root = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_root',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'root']
    )
    
    STPN_map_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_base_link',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'base_link']
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        urdf_file_arg,
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        STNP_map_root,
        STPN_map_base,
        rviz_node
    ])