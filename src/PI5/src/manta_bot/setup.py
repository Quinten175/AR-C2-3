from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'manta_bot'

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
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*.stl')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),

    ],
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
            f'activate_mapping = {package_name}.Lidar.activate_mapping:main',
            f'movement_handler = {package_name}.movement_handler:main',
            f'UI_app = {package_name}.UI.UI_app:main',
        ],
        'ros2_control_systems': [
            'manta_bot_hardware = manta_bot.movement_handler:MantaBotHardware',
        ],
    },
)