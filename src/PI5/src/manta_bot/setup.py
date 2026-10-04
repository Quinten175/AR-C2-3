from setuptools import find_packages, setup
import os
from glob import glob
 
package_name = 'manta_bot'
def generate_data_files():
    data_files = [
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'UI'),glob('manta_bot/UI/*.html')),
        (os.path.join('share', package_name, 'UI', 'static'),glob('manta_bot/UI/static/*')),
    ]
    return data_files
setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    package_data={
        'manta_bot': [
            'UI/*.html',
            'UI/static/*',
        ],
    },
    data_files=generate_data_files(),
    install_requires=['setuptools'],
    zip_safe=False,
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
            f'cmd_vel_dummy = {package_name}.Movement.cmd_vel_publisher:main',
            f'activate_mapping = {package_name}.Lidar.activate_mapping:main',
            f'wheel_test = {package_name}.Sim.wheel_test:main',
            f'movement_handler = {package_name}.Movement.movement_handler:main',
            f'gamepad_controller = {package_name}.Movement.controller:main',
            f'UI_app = {package_name}.UI.UI_app:main',
            f'serial_debug = {package_name}.Movement.serial_debug:main',
        ],
        'ros2_control_systems': [
            f'manta_bot_hardware = {package_name}.Movement.movement_handler:MantaBotHardware',
        ],
    },
)   
 
