import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):
    manta_pkg_share = get_package_share_directory('manta_bot')
    nav2_bringup_share = get_package_share_directory('nav2_bringup')

    nav2_params = os.path.join(manta_pkg_share, 'config', 'nav2_params.yaml')
    map_file = os.path.join(manta_pkg_share, 'map', 'my_map.yaml')
    if not os.path.isfile(map_file):
        raise RuntimeError(
            f"Map file '{map_file}' does not exist"
        )

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            nav2_params,
            {'yaml_filename': map_file}
        ]
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[nav2_params]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )

    odom_to_base_footprint = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_base_footprint',
        output='screen',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'odom', 'base_footprint'
        ],
        condition=IfCondition(LaunchConfiguration('publish_static_odom_tf'))
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_share, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'params_file': nav2_params,
            'autostart': 'true'
        }.items()
    )

    return [
        map_server,
        amcl,
        lifecycle_manager,
        odom_to_base_footprint,
        navigation
    ]


def generate_launch_description():
    manta_pkg_share = get_package_share_directory('manta_bot')
    return LaunchDescription([
        DeclareLaunchArgument(
            'publish_static_odom_tf',
            default_value='true',
            description='Set false if another node publishes odom to base_footprint TF'
        ),
        OpaqueFunction(function=launch_setup)
    ])
