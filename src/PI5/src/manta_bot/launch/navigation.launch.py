import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    manta_pkg_share = get_package_share_directory('manta_bot')
    nav2_bringup_share = get_package_share_directory('nav2_bringup')

    nav2_params = os.path.join(manta_pkg_share, 'config', 'nav2_params.yaml')

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(manta_pkg_share, 'launch', 'slam.launch.py')
        ),
        launch_arguments={
            'publish_static_odom_tf': LaunchConfiguration(
                'publish_static_odom_tf'
            )
        }.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup_share,
                'launch',
                'navigation_launch.py'
            )
        ),
        launch_arguments={
            'params_file': nav2_params,
            'autostart': 'true',
            'use_composition': 'False'
        }.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'publish_static_odom_tf',
            default_value='false',
            description='Set false if another node publishes odom to base_footprint TF'
        ),
        slam,
        navigation
    ])
