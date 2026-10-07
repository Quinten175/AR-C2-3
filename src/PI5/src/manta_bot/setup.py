from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'manta_bot'

## with debugging claude said I should add this function to include the models in the package, otherwise they are not found when installed via colcon build
def package_files(dest, src):
    out = []
    for root, _, files in os.walk(src):
        if files:
            rel = os.path.relpath(root, src)
            target = dest if rel == '.' else os.path.join(dest, rel)
            out.append((target, [os.path.join(root, f) for f in files]))
    return out

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),

    ] + package_files(os.path.join('share', package_name, 'models'), 'manta_bot/Cam/models'),

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='quin',
    maintainer_email='quintenvandervalk@gmail.com',
    description='Manta Bot package with diff-drive controller support',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            f'static_odom_publisher = {package_name}.Lidar.static_odom_publisher:main',

            'cmd_vel_dummy = manta_bot.Movement.cmd_vel_publisher:main',

            f'activate_mapping = {package_name}.Lidar.activate_mapping:main',
            f'movement_handler = {package_name}.Movement.movement_handler:main',
            f'UI_app = {package_name}.UI.UI_app:main',
            f'person_fusion = {package_name}.translation.test_file:main',
            
            f'fake_scan_c = {package_name}.translation.fakelidarnode_c:main',
            f'fake_scan = {package_name}.translation.fakelidarnode:main',
            f'camera_publisher = {package_name}.Cam.camera_publisher:main',
            f'yolo_detector = {package_name}.Cam.yolo26_ros2:main', 
            f'stream = {package_name}.Cam.stream:main',
            f'stream_node = {package_name}.Cam.stream_node:main',

            

        ],
        'ros2_control_systems': [
            'manta_bot_hardware = manta_bot.Movement.movement_handler:MantaBotHardware',
        ],
    },
)