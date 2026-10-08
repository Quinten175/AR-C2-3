import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    # 1. This returns: /home/rik-noorman/AR-C2-3/src/PI5/install/manta_bot/share/manta_bot
    package_share_dir = get_package_share_directory('manta_bot')
    
    # 2. Fix the path concatenation to target 'Cam/pi_stream' directly
    # (Do NOT add an extra 'manta_bot' string folder here)
    ui_workspace = os.path.join(package_share_dir, 'Cam', 'pi_stream')

    return LaunchDescription([
        ExecuteProcess(
            cmd=['npm', 'start'],
            cwd=ui_workspace,  # Points to the exact un-nested directory
            output='screen',
            shell=True         # Helps the underlying OS locate the npm binary alias securely
        )
    ])