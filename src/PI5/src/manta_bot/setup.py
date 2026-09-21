from setuptools import find_packages, setup
import os

package_name = 'manta_bot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        ('share/' + package_name + '/config', ['config/diff_drive_controller.yaml']),

        (os.path.join('share', package_name, 'launch'), ['launch/static_slam_launch.py']),
        (os.path.join('share', package_name, 'config'), ['config/slam_config.yaml']),

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
            f'active_mapping = {package_name}.Lidar.active_mapping:main',
            'movement_handler = manta_bot.movement_handler:main',
        ],
    },
)
