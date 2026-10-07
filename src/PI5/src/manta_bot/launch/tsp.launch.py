import os

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from ament_index_python.packages import get_package_share_directory

def launch_setup(context, *args, **kwargs):
    manta_pkg_share = get_package_share_directory('manta_bot')

    node_pub = Node(
        package='manta_bot',
        executable='make_nodes',
        name='make_nodes',
        output='screen'
    )
    
    waypoint_orderer = Node(
        package='manta_bot',
        executable='waypoint_orderer',
        name='waypoint_orderer',
        output='screen'
    )

    return [
        node_pub,
        waypoint_orderer,
    ]


def generate_launch_description():
    return LaunchDescription([
        OpaqueFunction(function=launch_setup)
    ])