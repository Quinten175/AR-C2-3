"""Manta Bot package."""

from launch_ros.parameter_descriptions import ParameterFile
from launch_ros.actions import Node

controllers_yaml = os.path.join(
    get_package_share_directory('manta_bot'),
    'config',
    'diff_drive_controller.yaml'
)

Node(
    package='controller_manager',
    executable='ros2_control_node',
    parameters=[robot_description, controllers_yaml],
    output='screen',
)