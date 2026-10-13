from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    make_nodes = Node(
        package='manta_bot',
        executable='make_nodes',
        name='make_nodes',
        output='screen'
    )

    waypoint_orderer = Node(
        package='manta_bot',
        executable='waypoint_orderer',
        name='waypoint_orderer',
        output='screen',
        parameters=[
            {
                'global_frame': 'map',
                'robot_frame': 'base_footprint',
                'return_to_start': False
            }
        ]
    )

    return LaunchDescription([
        make_nodes,
        waypoint_orderer
    ])